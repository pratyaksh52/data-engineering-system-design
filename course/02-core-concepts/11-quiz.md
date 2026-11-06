# Module 2 Quiz: Core Concepts

Fifteen questions on partitioning, ingestion, backfills, lineage, cost, monitoring, contracts, late data and deduplication. Answer each one out loud or on paper first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. Date, hour and tenant

A clickstream pipeline lands 200 GB a day of Parquet from 5,000 tenants. Support runs "yesterday's events for tenant 4127" all day, so a teammate proposes partitioning by date, hour and tenant. Another proposes date and tenant. Which do you pick, or what do you propose instead, and what is the arithmetic?

<details>
<summary>Answer</summary>

Propose **date-only partitioning, with the table clustered by `tenant_id` inside each day.**

Divide data per day by partitions per day. Date, hour and tenant gives 24 x 5,000 = 120,000 partitions a day, about 1.7 MB each. Date and tenant gives 5,000 partitions of about 40 MB. Both are far below the roughly 1 GB per partition you want (files of 128 MB to 1 GB), so both cause the small-files problem: listing and opening tiny files costs more than reading them, and the metadata grows until planning a query is slower than running it. Date-only gives one 200 GB partition, about 800 files of 256 MB, which is healthy.

Clustering gives you the tenant skip without the folders. Rows inside each day are sorted by tenant, so the min and max statistics in the Parquet blocks let the engine read only the blocks that can hold tenant 4127: about 40 MB instead of 200 GB.

The tempting answer is date and tenant, because "support is per tenant". Folders are the coarse cut, and a column with thousands of values belongs in clustering.

Covered in [Partitioning](01-partitioning.md).
</details>

### Q2. The tenant that is 40 percent of traffic (multiple choice)

Events flow through Kafka keyed by `tenant_id`. Peak ingest is 35 MB/s and one tenant sends 40 percent of it. That tenant's partition is falling behind. Which fix works, and what does it cost?

- A. Double the partition count of the topic
- B. Switch the key to `event_date`
- C. Salt that tenant's key into 8 sub-keys, and have readers combine the 8 slices
- D. Raise the consumer's memory so one consumer can keep up

<details>
<summary>Answer</summary>

**C.** The big tenant sends 0.4 x 35 = 14 MB/s, above the roughly 10 MB/s planning figure for one partition. Salting (appending something like `hash(event_id) % 8` to the key) spreads that tenant over up to 8 partitions at about 1.75 MB/s each. The cost is on the read side: a query for that tenant reads 8 slices and merges them, aggregates become two-step (partial sums, then a final sum), and order is lost across the salts. Salt only the known giant keys.

A is the tempting answer. One key hashes to exactly one partition however many partitions exist, so the hot tenant stays put, and adding partitions to a live topic remaps keys and breaks ordering for a while. B throws away the per-tenant ordering the key was chosen for and creates a single-day hot spot. D treats a one-partition throughput limit as a memory problem.

Covered in [Partitioning](01-partitioning.md).
</details>

### Q3. Cancelled orders that never disappear

The nightly job copies new and changed orders from Postgres with `WHERE updated_at > :last_watermark`. Finance reports two problems: cancelled orders are still in the warehouse, and about one order in a thousand is missing. Explain both and fix both.

<details>
<summary>Answer</summary>

These are two of the standard gaps of a watermark load.

**Cancellations.** If the cancel is a hard delete, the row is gone from the source and has no `updated_at` to find. Fixes: a soft delete (a `deleted_at` or status column), a periodic comparison of primary keys, or change data capture (CDC), which reads deletes from the database log.

**The missing one in a thousand.** A transaction that started at 01:59 and committed at 02:03 carries a 01:59 timestamp. If a run read up to 02:00 before the commit, the row never qualifies again. The fix is an **overlap window**: each run starts from the last watermark minus about 10 minutes, and an upsert keyed on the order ID absorbs the repeated rows. Bound each query above with the run's start time so a retry reads the same rows.

If finance needs exact numbers every 15 minutes, move to CDC. The watermark has a third weakness you cannot test from the warehouse side: code paths that change rows without touching `updated_at`.

The tempting answer is "run it more often". That narrows the window but never closes it, and does nothing about deletes.

Covered in [Ingestion Patterns](02-ingestion-patterns.md).
</details>

### Q4. The courier's CSV

A courier partner drops a daily CSV on an SFTP server, usually by 05:00. Last week your job loaded a file at 04:58 while it was still being written, and on Friday the partner re-sent Thursday's file under a new name. Nobody noticed either until a finance review. What do you change?

<details>
<summary>Answer</summary>

Files need four parts, and each answers one of the failures.

1. **A completion signal.** Ask the partner to write under a temporary name and rename on finish, or to add a marker file (such as `_SUCCESS`) or a manifest with expected row counts. Without one, read only files whose size has stopped changing. This stops the half-written load.
2. **A ledger of loaded files.** Record each file's name and checksum. A re-sent file with a new name but the same content has the same checksum and is skipped, which also makes retries safe.
3. **Land untouched, then parse.** Copy the original into the raw zone first, so a parse failure never costs you the file.
4. **An expectation of arrival.** "Daily file by 05:00" is a freshness check, and a missing file should alert like a failed job.

Also check the content: the partner may re-send corrected values under the same keys, so load with an upsert on the business key and decide which copy wins.

The tempting answer is "wait until 05:30 to be safe". A later start is a guess about the partner's behavior, not a signal, and it fails the first time they are late.

Covered in [Ingestion Patterns](02-ingestion-patterns.md).
</details>

### Q5. Forty-five days of wrong revenue

A currency-conversion bug has produced wrong `fact_revenue` rows for 45 days. The fix is a ten-minute code change. Kafka keeps 3 days of data, the payments API cannot return history, and about 1 TB of raw JSON landed each day. Walk through how you correct the data.

<details>
<summary>Answer</summary>

1. **Rerun safely.** Every job takes its date as a parameter and overwrites that date's partition, so the backfill is the same job run for 45 dates. If the job appends, make it idempotent first, or the rerun duplicates rows.
2. **Choose the input.** Replay from the raw layer. Kafka holds only 3 days and the API has no history, so raw object storage is the only complete source.
3. **Size it.** 45 days x 1 TB = 45 TB, roughly 625 to 1,250 core-hours: a couple of hours of compute on 500 cores, half a day end to end. Cap it at, say, 5 dates in parallel on a separate queue so today's run is not starved.
4. **Protect readers.** Write to a shadow table (`fact_revenue_v2`), validate daily totals against raw and the old table, then flip a view. Rollback is flipping back.
5. **Finish the job.** Rerun the dependents (monthly rollup, feature table) for the affected dates in dependency order, and tell finance and other consumers the date range and expected change before it lands.

The tempting answer is an `UPDATE` on the wrong rows. It is fast, but nobody can reproduce it and the next code change can bring the bug back.

Covered in [Backfill and Reprocessing](03-backfill-and-reprocessing.md).
</details>

### Q6. A backfill that gives today's answer (multiple choice)

A daily job joins orders to the `customers` table and reads each customer's current tier. You backfill September, and the tier-based discount report for September changes in ways nobody can explain. What is the most likely cause?

- A. The job read the customer's tier as it is now, instead of as of each run date
- B. The job is not partitioned by date
- C. The raw layer was compressed with the wrong codec
- D. The backfill ran too many dates in parallel

<details>
<summary>Answer</summary>

**A.** A job that reads "now" or "the current dimension row" produces today's answer for a past date. A backfill is reproducible only if every input is pinned to the run's date. Where the answer depends on how a dimension looked back then, read it as of that date (a Type 2 dimension with validity dates makes this possible).

B is a real cost and safety problem, since an unpartitioned output makes a rerun rewrite everything, but it would not change September's values. D hurts shared-cluster capacity, not the numbers. C has nothing to do with the symptom. The tell is a change tied to customer attributes, and an input that moves with time is the usual reason.

Covered in [Backfill and Reprocessing](03-backfill-and-reprocessing.md).
</details>

### Q7. Renaming `orders.amount`

The orders team wants to rename `orders.amount` to `orders.amount_gross`. You have table-level lineage showing 14 tables that read `orders`, and several of them are built with Spark jobs. The team asks whether that is enough to proceed. What do you tell them?

<details>
<summary>Answer</summary>

Table-level lineage says 14 tables read `orders`, so you would ask 14 teams whether they use `amount`. **Column-level lineage** answers the real question: it might show that only 3 tables use that column, so you talk to 3 teams. For a rename, this is where column level earns its cost.

Be honest about its blind spots. Parsing SQL breaks on `SELECT *`, SQL built as a string at runtime, and code in Python or Spark. For the Spark jobs you need runtime lineage events (the jobs report what they read and wrote, for example in the OpenLineage format), with the query log as a backstop. Where column detail is unavailable, fall back to table level for those jobs and flag them. Also make sure the graph includes consumers outside the pipeline: dashboards, notebooks and models.

Then ship the rename as expand and contract: publish `amount_gross` next to `amount`, move the 3 consumers, then remove the old column.

The tempting answer is "table-level is enough, we'll just announce it". That pushes the discovery work onto 14 teams and still misses the one nobody remembers.

Covered in [Data Lineage](04-data-lineage.md), with the change workflow in [Data Contracts](07-data-contracts.md).
</details>

### Q8. The dashboard that scans 6 TB

A dashboard refreshes every 15 minutes and scans the whole 30-day events table (6 TB of Parquet) on a scan-priced engine at about $5 per TB. Finance asks you to cut the bill. A colleague suggests moving old data to a cheaper storage tier. What do you do first?

<details>
<summary>Answer</summary>

Find the biggest line before choosing a lever. At 6 TB a run, the dashboard costs about $30 per run, 96 runs a day, roughly $2,900 a day. Storing the 6 TB costs only about $140 a month, so tiering it saves almost nothing.

Read less, in order of effort:

1. **Filter on the partition column** (yesterday's partition): 200 GB, about $1 a run, about $96 a day.
2. **Select only the three columns the dashboard shows**: about 12 GB, about $0.06 a run, about $6 a day.
3. **Better still, don't run the query.** Compute the aggregate once an hour into a small summary table of a few MB and point the dashboard at it.

Same answer on screen, roughly 500 times cheaper, with no hardware change. Name the price too: the summary table adds staleness and one more table to maintain.

The tempting answer is cheaper storage, the smallest of the four buckets (storage, compute, scans and requests, egress). Interviewers listen for the order: measure, take the cheapest lever, then talk about tiers and spot capacity.

Covered in [Cost Optimization](05-cost-optimization.md), with pruning in [Partitioning](01-partitioning.md).
</details>

### Q9. 41 alerts and one that mattered

An on-call engineer is woken 41 times in 13 minutes: failed tasks that succeeded on retry, 12 stale-table alerts from one late extract, and one zero-row payments extract. The finance table is due at 07:00, the extract normally finishes by 03:00 and the transform takes 90 minutes. What do you change?

<details>
<summary>Answer</summary>

Page on the **SLA at risk**, not on failures. Treat 07:00 as a budget: with the extract done at 03:00 and a 90-minute transform, the table is ready by about 04:30, leaving 2.5 hours of slack. A task that fails at 02:05 and retries successfully costs 10 minutes of slack and wakes nobody. If at 05:00 the extract has still produced nothing, only 2 hours remain against a 90-minute transform, so page now, while there is time to fix it. A failure-based rule pages at 02:05 for something that heals, and may stay silent at 05:00 because no task has "failed".

Then clean up the noise:

- **Retries first, then alert** on exhausted retries, waiting about 10 minutes before firing.
- **Group by root cause.** The 12 stale-table alerts are one late extract. Page once on the cause, list the affected tables, and use lineage to silence the children.
- **Route by urgency.** Page, ticket or dashboard. Retries and consumer lag go on a dashboard.
- **Measure the noise.** Sort the last 30 pages into needed-a-human, fixed-itself and nobody-knew-what-to-do, then delete or demote the noisy ones.
- **Make the real alert detectable.** A zero-row load is a hard rule ("rows > 0"), and every page links to a runbook.

The tempting answer is to tune the failure alerts or mute the channel. Muting hides the real alert along with the noise, so fix the signal.

Covered in [Monitoring and Alerting](06-monitoring-and-alerting.md), with grouping through [Data Lineage](04-data-lineage.md).
</details>

### Q10. A bank-holiday Monday (multiple choice)

Your volume check alerts if today's rows are more than 20 percent below or 30 percent above the average of the same weekday over the last 4 weeks. The last four Mondays had 291,000, 305,000, 288,000 and 312,000 orders. This Monday is a bank holiday and brings 250,000. What happens, and is it the right behavior?

- A. The alert fires, because any value below the average is abnormal
- B. No alert, because the lower bound is about 239,000 and a holiday dip of about 16 percent is normal variation
- C. The alert fires, because the check compares with Sunday, which had fewer orders
- D. No alert, because volume checks only look for zero rows

<details>
<summary>Answer</summary>

**B.** The average is 299,000, so the lower bound is about 239,000 and the upper bound about 389,000. A count of 250,000 is 16 percent below the average and passes, while a real failure like 4,000 rows trips the check by a mile. The tolerance is wider than ordinary variation (the four Mondays sit within about 4 percent of their average) and narrow enough to catch real problems.

A would page on every normal dip. C describes the mistake the lesson warns about: comparing with yesterday fires every Monday, so compare the same weekday. D confuses the hard rule (rows must not be zero) with the seasonal baseline, which is for numbers that vary. Use hard rules for things never acceptable (null keys, zero rows) and a baseline for volume.

Covered in [Monitoring and Alerting](06-monitoring-and-alerting.md).
</details>

### Q11. Dollars become cents

The orders team changes the `total` field from dollars to cents. The name and type stay the same. The schema registry accepts the change, every check goes green, and the board metric is 100 times too high on Friday. What failed, and what would have stopped it?

<details>
<summary>Answer</summary>

A registry checks **structure, not meaning**. A rename or retype is rejected in every compatibility mode, but a unit change on an unchanged field passes all of them. The deeper cause is that the agreement between producer and consumers existed only in people's heads.

A **data contract** writes it down: schema, semantics (units, time zone, allowed values), quality rules, delivery promises, ownership and a change policy, versioned and owned by the producer. Layered enforcement then stops the change at several points:

1. **Producer CI** compares the contract and fails the pull request, the cheapest place.
2. **The registry** at publish time, as a backstop.
3. **Ingestion validation** with a dead-letter queue, which can check data rules like "total is within a plausible range".
4. **Table-level tests** on the serving table.

The last defense is monitoring. A distribution check (average order value jumping from $62 to $6,200) catches this change even if every contract check was bypassed.

The right way to make the change is expand and contract: publish `total_cents` alongside `total`, find consumers through lineage, move them within a deprecation window, then remove `total`. The tempting answer is "add schema drift alerts", which finds out after the damage and cannot see a unit change at all.

Covered in [Data Contracts](07-data-contracts.md), with the distribution check in [Monitoring and Alerting](06-monitoring-and-alerting.md).
</details>

### Q12. Replaying history under a schema registry (multiple choice)

A Kafka topic holds events written under schema versions 1, 2 and 3. A new consumer will replay the topic from the beginning and read everything with the newest schema. The subject uses BACKWARD compatibility. Which statement is correct?

- A. BACKWARD is enough, because each version was checked against the one before it
- B. FORWARD is needed, because old data must be readable by old readers
- C. NONE is fine, because consumers can ignore fields they do not understand
- D. BACKWARD_TRANSITIVE is needed, because version 3 must be able to read version 1 data too

<details>
<summary>Answer</summary>

**D.** BACKWARD means readers on the **new** schema can read data written with the **previous** one. Non-transitive modes compare a new version only with the latest, so v3 may be compatible with v2 and v2 with v1 while v3 cannot read v1. A consumer replaying from offset 0 meets all three versions, so the check must run against all earlier versions: BACKWARD_TRANSITIVE. The same applies to a warehouse table holding years of data written under old versions.

A is the tempting answer, and exactly the trap: each hop passes while the chain does not. B asks the wrong question, since the issue is a new reader reading old data, which is the BACKWARD direction. C confuses ignoring unknown fields with decoding data that lacks fields the new schema requires. Say it as "who can read whose data".

Covered in [Data Contracts](07-data-contracts.md).
</details>

### Q13. Choosing the watermark delay

A food-delivery app shows orders per hour on a live dashboard, and finance reads a daily warehouse table. You measured event lateness: p50 1 second, p95 20 seconds, p99 8 minutes, p99.9 3 hours. How do you set the watermark and handle the rest?

<details>
<summary>Answer</summary>

Aggregate by **event time**, because the business question is when the order happened, and store both `event_time` and `ingested_at` so lateness stays measurable.

Set the watermark delay from the data. A 10-minute allowance covers about 99 percent of events, and windows close roughly 10 minutes after their end. Waiting 3 hours to catch the last 0.1 percent would make every dashboard tile 3 hours stale to protect about 1 order in 1,000, the wrong trade for a live view.

Handle the tail with a second path:

- **Allowed lateness** (for example 1 hour) updates the window if a late event arrives soon after, with a keyed sink that upserts by window and key.
- **Too-late events** go to a side topic, never silently dropped. Count them and watch the late rate.
- **A nightly batch** recomputes the last 3 days from raw data and overwrites those partitions, so the warehouse is correct.

State the user-visible contract: the dashboard is provisional, the finance table is final after 3 days. At 20,000 events a second, even 99.9 percent coverage leaves about 20 events per second too late, so the tail is routine.

The tempting answer is a single 3-hour watermark, which buys near-complete results for every consumer at the price of freshness for all of them.

Covered in [Late-Arriving Data](08-late-arriving-data.md).
</details>

### Q14. Remembering every ID

A team proposes deduplicating 1 billion events a day inside the stream job by remembering every event ID forever. A measurement of one day of raw data shows 99.9 percent of duplicates arrive within 30 minutes of the first copy. What do you propose, with numbers?

<details>
<summary>Answer</summary>

Windowed streaming dedup plus batch dedup as the guarantee.

Streaming state grows with window length times event rate. At about 50 bytes per remembered key:

- Global for one year: about 365 billion keys, roughly 18 TB. That is not stream state.
- 24-hour window: 1 billion keys, about 50 GB, workable across a few workers.
- **1-hour window: about 42 million keys, about 2 GB.** Since 99.9 percent of duplicates arrive within 30 minutes, it removes nearly all of them at one twenty-fourth of the day-long state.

Partition the stream by the dedup key so all copies of an event reach the same worker. Keep every copy in the raw layer and run a nightly batch `MERGE` on the event ID (deduplicating the batch with `ROW_NUMBER` first, and filtering the target to recent partitions). A duplicate that slips past the window is then a wrong live number for a few hours, not forever, provided the live number is labeled provisional.

First, ask whether each event carries an ID generated at the producer before any retry. An ID stamped by your own ingestion service makes every retry look new.

The tempting answer is "remember everything, to be safe". It buys catching a duplicate that arrives 3 weeks later at the price of terabytes of state.

Covered in [Deduplication at Scale](09-deduplication-at-scale.md), with the state sizing built on [Key DE Numbers](10-key-de-numbers.md).
</details>

### Q15. How do you get exactly-once? (multiple choice)

A stream job reads from Kafka and appends rows to a warehouse table. It crashes after writing a batch but before saving its offset, and on restart it reads the same events again. Which change gives an exactly-once effect in the table?

- A. Turn on the Kafka producer's idempotent mode
- B. Reduce the checkpoint interval to one second
- C. Write with an upsert (`MERGE`) keyed by the event ID
- D. Add a Bloom filter in front of the sink

<details>
<summary>Answer</summary>

**C.** Delivery is at-least-once: the network cannot tell a lost message from a lost acknowledgement, so a reliable system resends when unsure. What you can have is an exactly-once **effect**, built from at-least-once delivery plus an idempotent write. With an upsert on the event ID, replayed events land on the same rows, so delivery happened twice and the effect happened once. Name the hop and the key.

A is the tempting answer. The idempotent producer removes duplicates caused by the producer's own retries when writing to Kafka, and does not reach a warehouse table downstream of the consumer. B shrinks the replay window but never closes it, since a crash can always fall between the write and the checkpoint. D has false positives that drop genuinely new events, which is unacceptable for anything like payments.

Covered in [Deduplication at Scale](09-deduplication-at-scale.md).
</details>
