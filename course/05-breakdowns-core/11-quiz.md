# Module 5 Quiz: Core Breakdowns

Fifteen questions on the ten core design breakdowns: which option to pick and why, what breaks at scale, and what the interviewer asks next. Answer each one out loud or on paper first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. The noisy neighbor

You run a company-wide log search with about 750 MB/s of peak ingest. During an incident the `checkout` service starts logging a stack trace on every request, and its 5 MB/s becomes 100 MB/s. Twenty minutes later engineers on unrelated teams say their logs are stale too. Why did that happen, and what do you change?

<details markdown="1">
<summary>Answer</summary>

The message log absorbed the burst, but the indexer is shared. It can only index so fast, so its lag grew to about 20 minutes, and every service's logs became 20 minutes stale, not just checkout's. One noisy service blinded the company at the moment it most needed to see.

Autoscaling the indexer on consumer lag is the mid-level answer. It is slow (new search nodes take minutes to join) and still treats a DEBUG line from a broken service like an ERROR from a healthy one.

The senior answer is isolation. Give each service an ingest quota for the hot tier (for example 3x its 7-day p95 rate). Above it, keep every ERROR, WARN and audit line and sample the rest (1 in 20), recording how many were skipped. The lake writer is not quota-limited, so nothing is lost permanently. Show a banner such as "checkout sampled at 1:20 from 02:14" so engineers know. "Scale the cluster" treats a fairness problem as a capacity problem.

Covered in [Log Aggregation](01-log-aggregation.md).
</details>

### Q2. Cut the logging bill in half (multiple choice)

Finance says the logging platform costs about $85k a month and wants half of it gone. The hot search tier (7 days on SSD) is about $45k to $50k, the message log about $20k to $30k, and the object-storage lake about $5k to $8k. Which first move is the strongest?

- A. Switch the lake from Parquet to a more compact format and shorten its retention
- B. Stop indexing DEBUG lines and routine health-check and access lines in the hot tier, turning the access lines into metrics
- C. Move the hot tier from 7 days to 1 day
- D. Negotiate a lower price per terabyte with the storage vendor

<details markdown="1">
<summary>Answer</summary>

**B.** The hot tier is the expensive line, and its cost scales with the bytes you choose to index. In a typical mix, DEBUG is about 30% of lines and routine `200 OK` access and health lines about 20%. Dropping DEBUG by default (a service can switch it on for an hour when someone is debugging) and converting access lines into counts, while the raw lines still go to the lake, halves what reaches the hot tier. That saves roughly $30k of an $85k bill. Be honest that this is a third, not half, and offer showback (publishing each team's bill) as the next lever.

A optimizes the cheap line: the lake is under 10% of the bill, so even a big win barely moves the total. That is the classic mistake of not doing the math first. C cuts debugging power the requirements did not agree to give up, and D is procurement, not design.

Covered in [Log Aggregation](01-log-aggregation.md).
</details>

### Q3. Unique visitors over 90 days

A URL shortener gets 1 billion clicks a day. A customer picks a 90-day range and asks for unique visitors on one link. Your stream job stores an exact distinct count per link per day, and the dashboard sums the days. A newsletter link clicked by the same 10,000 subscribers each week shows 130,000 visitors. What is wrong, and what would you store instead?

<details markdown="1">
<summary>Answer</summary>

Clicks add, but distinct counts do not. A visitor who returns on 30 different days is counted 30 times by the sum, and the same happens when you sum links to get an account total. A range answer cannot be derived from daily integers.

The exact fix is one row per (link, day, visitor) and `COUNT(DISTINCT visitor_id)` over the range. That is about 700 million rows a day, and a link with 2 million visitors a day means up to 180 million IDs in memory for one view. Fine for an export, not for a dashboard at 500 ms.

The strong answer is a **HyperLogLog sketch** per link per day. A sketch is a small, fixed-size structure (at most about 12 KB) that estimates the number of distinct values, with a standard error of about 1.04 divided by the square root of its bucket count. Sketches merge by taking the per-bucket maximum, so a 90-day query merges 90 small sketches and an account total merges across links. State the trade-off: the answer is approximate (within about 1%), and you keep an exact path from the lake for invoices and exports.

Keeping the exact daily number feels safer, but it is exact about the wrong question.

Covered in [URL Shortener Analytics](02-url-shortener-analytics.md).
</details>

### Q4. The viral link

Clicks go into a topic with 48 partitions, keyed by `link_id`. One link starts receiving 50,000 clicks a second at about 500 bytes each. The dashboard lag grows for many unrelated links. A teammate says, "Add more partitions." Respond, and give the design that actually works.

<details markdown="1">
<summary>Answer</summary>

Adding partitions does nothing: one `link_id` always hashes to one partition. That partition receives 25 MB/s, past the 10 MB/s planning figure, and every other link on it lags too. That is a hot partition.

Mid-level fix: partition by `click_id` so load spreads across all 48 partitions, then re-key by `link_id` in the stream job. That moves the hot spot: one subtask still handles 50,000 events a second and applies backpressure to everything sharing it.

Senior fix: **local-global (two-phase) aggregation**. Each reader accumulates a partial count and a partial HLL sketch per link for about 2 seconds, then sends one partial per link to the keyed step. With 48 readers, the viral link's subtask gets about 24 partials a second instead of 50,000 events. This works only because the aggregates merge: counts add and sketches merge by maximum. An exact median could not be split this way.

Covered in [URL Shortener Analytics](02-url-shortener-analytics.md).
</details>

### Q5. Finance closed October (multiple choice)

Finance signed off the October report. On 5 November, 3,000 marketplace orders dated 30 October and 40,000 returns of October sales arrive in the warehouse. Finance wants closed months frozen. Merchandising wants October's return rate to reflect every return. Which design serves both?

- A. Load the rows into October and tell finance to expect small restatements
- B. Reject any row dated in a closed month so October never changes
- C. Keep two copies of the sales table, one frozen and one live
- D. Give every activity row an `event_date` and a `posting_period`, where late rows get the current open month as their posting period, and let each team filter on the date it needs

<details markdown="1">
<summary>Answer</summary>

**D.** Three dates are in play: when the event happened, when the original order happened, and when the warehouse learned about it. Finance's rule is about the accounting month, which is a different question from merchandising's "which month's sales were returned". Store both. The late 30 October orders keep `event_date = 2026-10-30` and get `posting_period = 2026-11`. Finance reports by `posting_period`, so October never moves and November shows labeled prior-period adjustments. Merchandising reports by `order_date`, sees the late data in October, and the dashboard states that the return window is still open. A `loaded_at` column answers "what did the signed report contain?" with a filter.

A breaks the signed report: a rerun disagrees with it and nobody can say why. B loses the late orders and returns forever. C creates two numbers with no rule for which is official. Say it aloud: two teams need two answers to "which month is this in", and both are right.

Covered in [E-commerce Warehouse](03-e-commerce-warehouse.md).
</details>

### Q6. The backdated Gold tier

A customer's loyalty tier was changed to Gold, backdated to 1 October. The change reached the warehouse on 3 October. The customer dimension keeps history with Type 2 rows. Which tier should orders placed on 1 and 2 October show, and what do you key the dimension rows on to make that happen?

<details markdown="1">
<summary>Answer</summary>

Those orders should show Gold, because that is what the business decided was true on those dates. Build each dimension row's `valid_from` from the business effective date (1 October), not from the time the change was captured (3 October). The capture or commit time answers "what did we know when", which is useful for audit but wrong for "what tier was this customer on when they ordered".

The catch is that facts loaded on 1 and 2 October already point at the old (Standard) dimension row, and a lookup at load time could not see a change that had not arrived. The senior answer adds a **lookback window**: when a dimension change arrives with a `valid_from` in the past, re-key the facts in that window (here, the customer's orders since 1 October) to the new row. Bound the window (the breakdown uses 35 days, longer than the loyalty job's worst backdating) and send anything older to a review queue instead of silently rewriting old facts. Amounts and posting periods never change, so finance's totals stay put.

The CDC commit time is tempting because it is the timestamp in front of you.

Covered in [E-commerce Warehouse](03-e-commerce-warehouse.md), with dimension history in [Data Model Design](../01-the-framework/06-data-model-design.md).
</details>

### Q7. The dip at the right edge

A real-time payments dashboard charts approval rate in 10-second buckets by attempt time. The newest bucket always shows about 75% and climbs to 91% as outcomes arrive. The team has learned to ignore the right edge. What is happening, and what do you build so a real outage is still caught within seconds?

<details markdown="1">
<summary>Answer</summary>

Attempts still in flight count in the denominator but not in the numerator. An issuer can take up to 30 seconds to answer (the timeout), so the newest bucket is still filling. People learn that the right edge always dips, then ignore it during a real outage.

The first fix is to bucket by **completion time**, which makes the right edge stable. Its blind spot: when an issuer stops answering, nothing completes for 30 seconds, then the timeouts land at once, so for half a minute the chart looks calm.

The senior design keeps three views. Completion-time wall charts for stability. An **in-flight gauge per issuer** (attempts started minus attempts completed, emitted every second): an issuer handling 200 payments a second with a 400 ms response has about 80 in flight, so if it goes silent the gauge passes 1,000 within 5 seconds, far ahead of the first timeout. Alert at about 5x normal. And attempt-time charts for after-the-fact analysis, with buckets younger than the timeout plus pipeline delay drawn grey and labelled provisional.

Covered in [Real-Time Dashboard](04-real-time-dashboard.md).
</details>

### Q8. Three hundred screens (multiple choice)

The operations wall has 300 viewers, each screen with 40 charts refreshed every 5 seconds. That is 2,400 queries a second, nearly all identical, against a real-time OLAP store that is also serving analysts' drill-downs. During an incident everyone opens the dashboard at once. What is the strongest design?

- A. Put the dashboard behind a service that computes each distinct chart query once and shares the result, push the wall to browsers, and fence off the ad hoc drill-down with its own limits
- B. Let browsers query the OLAP store directly and add replicas when load grows
- C. Lower the refresh rate to 60 seconds so the store can keep up
- D. Precompute every possible chart in the stream job and serve it from a key-value store

<details markdown="1">
<summary>Answer</summary>

**A.** 2,400 identical queries a second is really 40 distinct queries run once each. A shared result cache (or a push channel) turns 300 viewers into the cost of one, and a separate lane with timeouts and concurrency limits for drill-down stops an analyst's expensive query from slowing the wall during the incident, which is exactly when both are busiest.

B scales cost linearly with viewers, and the incident that brings 300 people in is when the store is hottest. C trades away the 10-second freshness requirement to hide a design problem. D fails the first unplanned question ("break this down by issuer and card type"), which is why the store is an OLAP engine, not a key-value store.

Covered in [Real-Time Dashboard](04-real-time-dashboard.md).
</details>

### Q9. Out-of-order updates

Your CDC pipeline copies a payments table from 40 source databases into a lake mirror. A retry replays a `pending` update after a `settled` update for the same payment, and finance briefly reports a settled payment as pending. The team says, "We partition by primary key, so order is guaranteed." Where is that wrong, and where do you enforce order?

<details markdown="1">
<summary>Answer</summary>

Partitioning by primary key keeps a key's events in order inside Kafka, and nothing more. Order breaks elsewhere: inside a micro-batch, where the lake writer reads many partitions in parallel and shuffles; when partitions are added and the key-to-partition mapping changes; on connector restart, because at-least-once delivery replays events already applied; and after a re-snapshot or failover, where log positions from before and after may not compare (a MySQL file and offset means nothing on a different server).

Mid-level answer: guard the `MERGE` so a row updates only if the incoming log position is newer than the stored one. That fixes reordering and replays within one connector's lifetime.

Senior answer: enforce ordering in one place, the sink, by comparing keys and never trusting delivery order. Build `_ordering_key` from the engine's position (the LSN in Postgres; file, position and row number in MySQL), prefixed with a `_generation` bumped on every re-snapshot, lost slot or failover, so the new generation beats anything left from the old. Add that mirrors are consistent per table but only eventually consistent across tables.

Covered in [CDC Replication](05-cdc-replication.md), with the pattern in [CDC Patterns](../03-architecture-patterns/04-cdc-patterns.md).
</details>

### Q10. Forty terabytes on day one

You must copy 40 TB from 40 production databases into the lake before CDC can be trusted. The payments database alone is 10 TB of rows. Through one connection at about 20 MB/s that takes almost 6 days. Compare the defaults and describe the approach you would defend.

<details markdown="1">
<summary>Answer</summary>

**Bad: every connector runs its default initial snapshot.** Streaming does not start until it finishes, so for about 6 days the slot holds roughly 4 TB of WAL on the primary's disk, one long transaction blocks vacuum, and a failure on day 5 starts over.

**Good: incremental snapshots while streaming.** Start every connector streaming immediately and backfill tables in primary-key chunks interleaved with live changes. It is resumable, uses no long transaction, and any table can be redone alone: the right default for most of the 3,000 tables. It falls short on the giants, because chunks still come through one connector from the primary, so payments still takes days and competes with checkout.

**Great: bulk export the handful of tables over about 100 GB from a read replica.** Note the log position when the slot is created, wait for the replica to pass it, read the table in parallel primary-key ranges (16 readers bring 10 TB to roughly 9 hours), and write straight to the lake with that position as the ordering key. Streaming then applies on top, and the sink's ordering guard keeps the newer value.

Covered in [CDC Replication](05-cdc-replication.md).
</details>

### Q11. Ninety seconds for 3 GB (multiple choice)

In a medallion lake, a query on a small events table (about 15 MB a day, six months old, 3 GB total) takes 90 seconds. The table commits every 15 minutes from 12 writer tasks. Metadata shows about 210,000 files and 17,000 snapshots. What is the root cause, and the first fix?

- A. The table is too big for the engine; add more query compute
- B. Parquet is a slow format; switch the table to JSON
- C. Thousands of tiny files from frequent commits across many writers; fix the write side (one file per partition per commit, a commit rhythm matched to the consumer), then compact and expire snapshots based on table health
- D. The catalog is overloaded; add more catalog replicas

<details markdown="1">
<summary>Answer</summary>

**C.** 96 commits a day times 12 files is about 1,150 files of 13 KB each. A query opens every file; at 50 ms first-byte latency and 128 parallel reads, opening 210,000 files costs about 80 seconds before any real work. This is the small-files problem, and 3,900 small tables have it.

First stop creating the files: send each partition's rows to one writer task, and set the commit rhythm from what consumers need (a team that wants "this morning's refunds by 10:00" does not need a 15-minute commit). That alone takes the table from 1,150 files a day to 24. Then run maintenance as a service that measures table health (files per partition, average file size, snapshots) and compacts only the roughly 200 of 10,000 tables that need it, not a blanket nightly job over everything.

A is wrong because 3 GB is trivial and more compute only opens the same files faster. B makes it worse. D misreads the symptom: the time goes on file opens. Remember that "tier" (how fresh) and "volume class" (how big) are separate settings; most small-file disasters give a small table a big table's commit rhythm because someone asked for "real time".

Covered in [Medallion Data Lake](06-medallion-data-lake.md).
</details>

### Q12. Why it is not a volume problem

You are asked to design an ETL framework that lets 300 engineers run 5,000 pipelines (70% daily, 25% hourly, 5% every 15 minutes). A candidate opens with Spark cluster sizing. What are the real design pressures, with numbers, and what does the platform do about each?

<details markdown="1">
<summary>Answer</summary>

Spark and the warehouse do the heavy lifting; the load that matters is on the scheduler. That is about 57,500 runs and 460,000 task runs a day, only about 5 a second on average. Averages mislead here:

- **The midnight burst.** At 00:00 UTC all 5,000 pipelines are due in the same minute, roughly 80 first tasks a second against an average of 5. Spread start times by hashing each pipeline's name and set queue priorities by tier.
- **Waiting costs slots.** If each run holds a worker for 30 minutes while it waits for inputs, that adds about 30,000 slot-hours a day and more than doubles the fleet just to sleep. Use deferrable waits that do not hold a worker, with timeouts and alerts.
- **Parse cost.** At 0.2 s per generated DAG, 5,000 DAGs are 1,000 CPU-seconds per pass, over 30 cores re-reading files that only change on merge. Compile configs in CI so the scheduler's parse is trivial.
- **People.** About 6 platform engineers for 300 users means anything needing platform review per pipeline does not scale. Teams write a declarative spec with a few step types and a container escape hatch, validated in CI in under 10 minutes or people route around it.

"None of this is a data-volume problem" is the senior framing.

Covered in [ETL Framework](07-etl-framework.md).
</details>

### Q13. Great offline, worse in production

A fraud model scored well offline and performs worse in production. The feature store builds training sets by joining labels to a feature table. You find that the training join uses each feature row's `feature_ts` (for example "the 7 days up to midnight"), though that value is only readable online from 03:10. What is the bug, and how do you find and prevent more like it?

<details markdown="1">
<summary>Answer</summary>

It is **leakage**, one cause of training-serving skew. Joining on `feature_ts` hands every label between midnight and 03:10 a value that production did not yet have, and for fraud, three hours of future information is plenty. The join must use `available_ts`: the first moment the value could be read. Two related traps: joining on label time instead of prediction time, and recomputing late source data into old rows (append a correction with a new `available_ts` instead).

Prevention is a point-in-time join: for each label, keep the newest feature row with `available_ts <= prediction_time`, bounded by the view's TTL. The TTL is also what makes the join finish. Without it, 500 million labels against two years of daily history is 730 candidates each, about 365 billion rows; with a 2-day bound, at most 2.

Detection is what interviewers push on. Overall accuracy cannot say which of 300 features is at fault, and distribution checks miss a feature read from the wrong key. The strong answer is **feature logging**: log the exact values served with each prediction, then hourly replay the point-in-time join for a sample and compare value by value. A match rate per feature view (target 99.9%) pinpoints the feature and time. "We use the same code" detects nothing.

Covered in [Feature Store](08-feature-store.md).
</details>

### Q14. Muted alerts (multiple choice)

A data quality platform runs about 280,000 checks a day, including 140,000 automatic anomaly tests. A 3-standard-deviation band gives a false alarm roughly 1 time in 370 even on healthy data, so about 380 false alarms a day. Teams have muted the alert channel. Which response is strongest?

- A. Widen every threshold to 5 standard deviations
- B. Route alerts by severity and table tier, group failures by root cause, and track each check's precision so noisy checks are fixed, demoted to warn, or retired automatically
- C. Ask teams to un-mute the channel and treat every alert as urgent
- D. Add more checks so real problems are more likely to be caught

<details markdown="1">
<summary>Answer</summary>

**B.** The arithmetic says the alerting design matters more than the checking design: 380 expected false alarms a day arrive before any real incident. Severity and tier decide who gets paged and who gets a ticket; grouping by root cause turns one broken upstream table into one alert instead of 40 downstream ones; and per-check precision (the share of a check's incidents that turned out real) gives you a number to manage. A check overridden three times a month is a broken check, so fix it or demote it. Block only on what is never acceptable (null keys, duplicates, zero rows) and warn on what is merely unusual.

A trades noise for blindness: it misses real incidents too. C blames people for a design flaw. D adds more false alarms.

Covered in [Data Quality Monitoring](09-data-quality-monitoring.md).
</details>

### Q15. Supply drops by a quarter

A surge pricing pipeline counts available drivers per hexagonal cell and publishes a per-city snapshot that the pricing service reads. A failure stops a quarter of the ping partitions. Within 30 seconds, drivers on those partitions expire everywhere, supply drops by a quarter in every city, and pricing surges all of them. How do you design so this cannot happen?

<details markdown="1">
<summary>Answer</summary>

A dashboard with a gap misleads a human who can check. A surge pipeline with a gap overcharges riders, so the pipeline must stop publishing rather than publish something wrong, and pricing must fall back to safe prices.
An `as_of` timestamp that pricing ignores when older than 15 seconds is the mid-level answer. It catches a stopped pipeline, not a partly stopped one: healthy partitions keep timestamps looking fresh.

The senior design has three layers:

1. **Expire on the pipeline's clock.** Make the 30-second driver expiry an event-time timer, so a stalled partition holds the watermark and its drivers wait instead of vanishing. Do not skip idle partitions: partitions keyed by driver always carry traffic, so silence means failure.
2. **Measure completeness.** Each gateway writes a heartbeat into every partition each second; completeness is the share of gateways heard from within 5 seconds. Pricing uses only snapshots above its threshold, otherwise it holds the last good prices or standard fares.
3. **Sanity-check the market.** Real supply does not fall 15% across a whole city in one tick. Mark such snapshots `suspect`.

Covered in [Surge Pricing](10-surge-pricing.md).
</details>
