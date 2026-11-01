# Module 3 Quiz: Architecture Patterns

Fourteen questions on Lambda, Kappa, medallion, CDC, event sourcing, data mesh, data fabric, micro-batch versus streaming, and reverse ETL. Answer each one out loud or on paper first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. "Real time and exact"

A food-delivery app produces about 500 million events a day. City operations want orders per city per minute within 30 seconds, and a small error is fine. Finance wants yesterday's revenue exact to the cent by 06:00. The interviewer asks, "So, Lambda?" What do you say?

<details>
<summary>Answer</summary>

Not yet. Split the requirement by consumer first: ops has a speed contract, finance has a correctness contract. Then test the simpler options out loud. If the stream job can be exact (event-time windows, idempotent writes), run one stream job and fix history by replay. If ops would accept five minutes, one micro-batch job meets both contracts with one codebase.

Choose Lambda only if a constraint forces two paths: the fast and exact computations really differ (a sketch-based unique count live, an exact one daily), the stream cannot hold the state the exact version needs, or the log cannot be replayed far enough. Then say what each layer owns. The speed layer covers the time since the last batch cutoff and may be approximate. The batch layer recomputes each day from raw and owns the history.

The tempting answer is "real-time plus exact, so Lambda". It names the three boxes but pays for two copies of every business rule, plus reconciliation, without showing the cost was necessary.

Covered in [Lambda Architecture](01-lambda-architecture.md).
</details>

### Q2. The merge at the serving layer (multiple choice)

In a Lambda system, the serving layer shows revenue per city per minute. The batch layer has covered everything up to midnight, and it is now 14:03. How should the serving layer build the answer for a dashboard spanning yesterday and today?

- A. Sum the batch view and the speed view so no event is missed
- B. Use the batch view before the cutoff and the speed view after it
- C. Use the speed view everywhere, and keep the batch view only as a backup
- D. Use whichever view has the larger number, since the other missed events

<details>
<summary>Answer</summary>

**B.** Each time range comes from exactly one layer. Before the cutoff the batch view is complete and exact. After it, only the speed layer has data. When the nightly result lands, it replaces the speed layer's copy of that day, which is then discarded.

A is the tempting answer because both layers read the same events, so their time ranges overlap. Summing counts the overlap twice. C makes the approximate layer the source of truth, so a speed-layer bug stays in the history and the batch layer's work is wasted. D invents a rule with no basis: the larger number may come from duplicates the batch layer removed.

A gap between the two layers for a finished day is a signal to investigate, so do not feed it into the merge. About 0.2 percent from late events is normal. 3 percent means the two codebases have drifted.

Covered in [Lambda Architecture](01-lambda-architecture.md).
</details>

### Q3. The bug that is older than the log

A ride-hailing pipeline runs one stream job (Kappa style) on a Kafka topic that keeps 3 days. The team finds the job has counted trips cancelled within 10 seconds as completed for 11 days. How do you fix the data? You decide to recompute the last 30 days, which is 30 TB. How long will that take?

<details>
<summary>Answer</summary>

The log no longer holds the first 8 days, so "just replay Kafka" fails. Replay from a second source: either tiered storage on the log, or the raw copy in object storage that a sink writes anyway. Reading the raw copy through a source connector lets the same job logic run, so you keep one codebase.

Procedure: deploy the fixed job as v2 with its own checkpoint and its own output table, replay from the earliest affected day while v1 keeps serving, check v2 against an independent total (payments), then switch consumers and delete v1's table. Never replay into the live table, or old and new results interleave.

The time is arithmetic. 30 TB throttled to 100 MB/s so it does not starve live consumers is 300,000 seconds, about 3.5 days. Unthrottled at 360 MB/s it is about 23 hours but competes with live traffic. Say "I'd plan the replay", not "we replay".

The tempting answer treats replay as free and the log as infinite.

Covered in [Kappa Architecture](02-kappa-architecture.md).
</details>

### Q4. Why the replay disagrees (multiple choice)

After a Kappa replay finishes, the new table matches the old one for most days. But some days the bug never touched differ, with slightly different driver-rating averages. What is the most likely cause?

- A. Kafka reordered events across partitions during the replay
- B. The replay used event time, which the live job did not
- C. Log compaction removed some trips
- D. The live job enriched each trip with the driver's rating at that moment by calling a service, and the replay used today's rating

<details>
<summary>Answer</summary>

**D.** Kappa needs a deterministic job. If the live job called an external service or read "current" reference data, a replay a month later reads different values, so history changes without any bug. Fix it by keeping reference data versioned and joining by event time, or accept that the replay is a new interpretation of history.

A is unlikely: order within a partition is preserved, and an event-time job does not depend on cross-partition order. B reverses the requirement. Event-time windows are what make a replay correct; processing time would put weeks of events into a few minutes of windows. C describes a topic that keeps only the latest record per key, which suits state and would lose trips, but a compacted topic would not be your event history in the first place.

The diagnosis method: compare per day, find the first day that differs, and ask what that day's inputs had in common.

Covered in [Kappa Architecture](02-kappa-architecture.md).
</details>

### Q5. A cleaning bug and a seven-day bronze

An online shop lands 1 TB a day of JSON. A silver job converted timezone offsets wrongly, so about 2% of orders landed on the wrong day. It was found after 14 days. Bronze keeps raw files for 7 days. What do you do now, and what do you change?

<details>
<summary>Answer</summary>

Fix the conversion, then rerun silver for the affected dates from bronze as idempotent partition overwrites, then rerun every gold table downstream (lineage tells you which). Consumers keep reading the old gold tables until the rebuilt ones are verified.

With 7-day retention you can recover only the last 7 days from bronze. For the older 7 days you need another copy, such as the source system if it can resend, or any longer-lived archive. This is the real finding: bronze retention must cover the longest bug you expect to find. 1 TB of JSON is about 200 GB as Parquet, so a year is about 73 TB, roughly $1,700 a month, so "keep everything" is the sensible default.

The tempting answer is to patch the wrong rows in gold. That leaves silver wrong for every other consumer and gives you no repeatable fix.

Covered in [Medallion Architecture](03-medallion-architecture.md).
</details>

### Q6. Where does it belong? (multiple choice)

Finance defines "net revenue" as gross minus refunds. Growth wants gross orders. Orders arrive twice about 3% of the time, and some contain email addresses. Which placement is right?

- A. Net revenue in silver, deduplication in gold, email masking in bronze
- B. Deduplication in silver, net revenue in gold (one definition per team), email masking in silver with bronze access restricted
- C. Everything in silver so there is one trusted table
- D. Deduplication in bronze so bronze is clean

<details>
<summary>Answer</summary>

**B.** The rule is to push shared work down and opinionated work up. Everyone needs deduplication, so silver does it once. Net revenue is a business definition two teams disagree on, so it lives in gold, once per team. Masking happens in silver, and bronze holds the raw value, so lock its access down.

A has all three reversed. C is the junk-drawer failure: finance's definition is forced on growth, and silver becomes a second gold. D is the most tempting wrong answer and the most damaging. Cleaning on the way into bronze means your replay source no longer matches what the source sent, so a cleaning bug becomes unrecoverable. Bronze is append-only and unjudged, duplicates included.

Covered in [Medallion Architecture](03-medallion-architecture.md).
</details>

### Q7. Cancelled orders still count

The analytics team copies a Postgres `orders` table (20 million rows, 200 writes a second) into the warehouse with `WHERE updated_at > :last_run` every minute. Finance reports that cancelled orders are still counted as revenue. Explain the bug and redesign the pipeline, including how it starts.

<details>
<summary>Answer</summary>

A hard-deleted row has no `updated_at` to find, so the poll never sees the delete. The same poll also collapses intermediate states (`placed`, `packed`, `shipped` inside one minute) and queries the primary that serves checkout. The poll sees current state, but you need the history of changes.

Use log-based CDC: a connector reads the write-ahead log, sees deletes and every intermediate state in commit order, and adds little load. To start, record the log position P, snapshot a consistent view of the table as of P, load it, then stream from P. Nothing is missed or double counted, and because the target applies changes by key, any overlap is harmless.

Land raw change events in a change table (bronze), then MERGE into a current-state table (silver) with deletes as soft deletes. Partition Kafka by primary key and keep the highest log position per key so an old event cannot overwrite a new one. Alert on replication slot lag: a dead connector makes the primary keep every log file, and its disk fills.

The tempting fix is a shorter poll interval, which fixes none of the three problems.

Covered in [CDC Patterns](04-cdc-patterns.md).
</details>

### Q8. Writing the order and publishing the event

An order service must save an order row and publish an `OrderPlaced` message to Kafka. The current code saves to Postgres, then publishes. Sometimes downstream systems never hear about an order. Swapping the order does not help either. Why, and what is the fix?

<details>
<summary>Answer</summary>

This is a dual write: two systems, no shared transaction, so no ordering is safe. Save then publish: a crash in between leaves an order with no event. Publish then save: a rollback leaves an event for an order that does not exist.

Use the outbox pattern. Add an `outbox` table in the same database. In one transaction, write the order row and an outbox row holding the event. A CDC connector reads the log, sees the outbox insert and publishes it. The database's atomic commit gives you either both or neither.

Three details: key events by the entity ID so one order's events stay in order; clean old outbox rows with a scheduled delete; and expect at-least-once delivery, so give every event a unique ID and deduplicate on it. For consumers this is also better than row-level CDC, because an outbox event is a deliberate versioned interface and not a leak of the table's internal schema.

The tempting fix, a retry loop around the publish, still fails when the process itself dies.

Covered in [CDC Patterns](04-cdc-patterns.md#the-outbox-pattern).
</details>

### Q9. "Isn't that just CDC?"

A payments app stores wallet events (`ToppedUp`, `PaymentMade`, `PaymentRefunded`, `FeeCharged`) as the source of truth. A candidate says, "So it's CDC with nicer event names." A customer asks why their balance is 40.00 and not 90.00. Correct the candidate and explain how the events answer the customer.

<details>
<summary>Answer</summary>

The difference is the source of truth. CDC reconstructs events from state: the table is the truth, and the log tells you a row went from 90 to 40, with no reason. Event sourcing derives state from events: the event log is the truth, events are written deliberately with business names and intent, and the balance is a projection you can throw away and rebuild. Test: if you can delete the log and lose nothing, it is not event sourcing.

To answer the customer, fold the wallet's events in order. 100 (top-up) - 60 (payment) + 60 (refund) - 10 (refund fee) - 50 (payment) = 40.00, and the last event shows a 50.00 payment to a named merchant. A state table that only stores `balance = 40.00` cannot say that.

Mention the costs unprompted: reads from projections lag the log, event schemas evolve forever (upcast on read, never edit stored events), a full rebuild takes time (5.5 TB at 50 MB/s is about 30 hours, about 1.5 hours across 20 key-partitioned readers), and erasure requests need crypto-shredding. For ordinary CRUD, plain tables with CDC are the better answer.

Covered in [Event Sourcing](05-event-sourcing.md).
</details>

### Q10. A mesh for 25 people

A startup with 25 employees, three product teams and one data engineer asks you to design its data platform. The CTO has read about data mesh and wants it. What do you say?

<details>
<summary>Answer</summary>

Ask the diagnostic questions first: how many domain teams produce data, is the central team a bottleneck, and can domains staff data ownership? Here the answers are three, no queue and one data engineer, so mesh is overkill. It is an organisational change that needs roughly 10 or more domains, a long central queue, domains with data skills, and a platform team of several engineers.

Offer the in-between: a central warehouse and platform with medallion layers, plus domain-owned models and tests, data contracts at team boundaries, and a catalog with named owners. That is where most of the benefit lives at this size, and you can grow towards mesh if the organisation does.

Show you know the four principles and why each exists: domain ownership puts knowledge next to the pipeline; data as a product (owner, contract, discoverability, service levels) stops the leftovers problem; a self-serve platform stops each domain building its own stack; federated governance, enforced by the platform, keeps products joinable.

The tempting answer is to agree, which signals you treat mesh as a product to buy and not as an ownership change.

Covered in [Data Mesh](06-data-mesh.md).
</details>

### Q11. Fabric versus the real problem (multiple choice)

A retailer's analysts spend two days finding which of five systems hold the data for a question, and then discover nobody knows who owns half the tables. A vendor pitches a data fabric that "makes all data queryable in place, with no pipelines". Which response shows the best judgment?

- A. Adopt it in full: federated queries remove the need for pipelines
- B. Reject it: fabric is only marketing
- C. Take the catalog, automated lineage and central policy, with owners attached. Use federation for exploration and light joins, and materialise heavy or repeated joins into the warehouse
- D. Build a data mesh instead, since fabric and mesh are alternatives

<details>
<summary>Answer</summary>

**C.** The useful parts are a catalog covering all systems, automatically captured metadata and policy defined once. Build the catalog first, with owners on every entry; it is cheap, it helps immediately, and it exposes which datasets nobody owns.

A overtrusts the pitch. Federated joins move data over the network on every query, load operational systems built for other work, read each source at a slightly different moment, and policy is bypassed by anyone with a direct connection. A 60 TB lake joined to a 4 TB warehouse belongs in a pipeline and a stored table. B is the opposite error: "it's just marketing" ends the conversation, and the underlying goals are sound. D is wrong because the two are complements. Mesh answers who is accountable; fabric answers how data is found and reached.

Covered in [Data Fabric](07-data-fabric.md), with the contrast in [Data Mesh](06-data-mesh.md).
</details>

### Q12. "It has to be real time"

A product manager says the orders-per-minute dashboard for a retailer "must be real time". It carries 1 billion events a day. Operations glance at it during sales and phone a warehouse if a region spikes. Which processing model do you pick, and roughly what does it cost compared with an always-on stream?

<details>
<summary>Answer</summary>

First turn "real time" into a number: ask what a person does with it and what happens if it is two minutes late. A human glancing at a screen does not need sub-second updates, so a freshness target of a few minutes to 15 is realistic. That points to micro-batch: a Spark Structured Streaming job with a fixed 5-minute trigger, or an available-now trigger every 10 to 15 minutes, with a checkpoint on object storage. Reserve record-at-a-time streaming (Flink) for cases where an action must follow a single event, such as a fraud block at checkout.

Cost comes from waiting. On 16 vCPUs an always-on stream is roughly $470 to 700 a month. A 5-minute micro-batch is idle over 90 percent of the time but costs the same if the cluster stays up. A 15-minute available-now job that releases the cluster between runs exists for about 3 of every 15 minutes, roughly $95 to 140 a month, about a fifth.

Say the upgrade trigger: if the target falls under a minute for some output, only that path moves to a stream processor.

The tempting answer, "streaming, because real time", pays for an idle cluster.

Covered in [Micro-Batch vs Streaming](08-micro-batch-vs-streaming.md).
</details>

### Q13. The one-second trigger (multiple choice)

To make a lake-table dashboard "fresher", an engineer sets a Spark micro-batch trigger of 1 second on 12 MB/s of JSON that lands as Parquet. What is the most likely consequence?

- A. Latency drops to milliseconds, because micro-batch becomes true streaming
- B. Compute cost falls, because each batch is smaller
- C. Tens of thousands of tiny files a day, slower reads and a need for compaction
- D. Exactly-once guarantees are lost, because the batches are too small

<details>
<summary>Answer</summary>

**C.** At about 2.4 MB per cycle, a 1-second trigger writes at least 86,400 files a day, against a target of 128 MB to 1 GB per file. Readers slow down, request costs climb, and every commit adds table metadata. A 5-minute trigger writes about 720 MB per cycle and the problem largely disappears. Treat a trigger under about a minute on a lake table as a smell: either the freshness is not that tight, or the sink should be a store built for small fast writes.

A is wrong: micro-batch has a latency floor around a second, and Spark's continuous mode is experimental and narrow. B is wrong because an idle cluster costs the same as a busy one; savings come from releasing compute between runs. D is wrong: the checkpoint plus a repeatable batch and an idempotent sink give exactly-once at any batch size.

Covered in [Micro-Batch vs Streaming](08-micro-batch-vs-streaming.md).
</details>

### Q14. Churn flags in the CRM

A subscription company has an `account_health` table (40,000 accounts) rebuilt nightly. Customer success managers want the score on the CRM account page and a task created when `churn_risk` flips to true. The CRM allows 100 requests a minute, 10 records per request. Design the sync and say what would make it break.

<details>
<summary>Answer</summary>

Use reverse ETL: read the model, diff against the last synced rows, map columns to CRM fields, write only changed rows in batches, record successes and failures. Upsert by the CRM's own account ID, not an email people can edit. For accounts that leave the model, set an inactive flag instead of deleting history.

Rate limit arithmetic: 100 x 10 = 1,000 records a minute. A nightly delta of about 1,200 records takes about 1.2 minutes; the first full load of 40,000 takes about 40 minutes. The first run is the problem because nothing is in the diff, so use the bulk endpoint for anything bigger and never resend everything each night. Retry 429 and 5xx with backoff, quarantine permanent failures with the reason, and alert on failed-row count.

The task needs an event, but reverse ETL syncs state. Detect the flip by diffing the new row against the last synced row and create one task. A model that says "all at-risk accounts" creates a new task every night. Make the write idempotent (an idempotency key from `(account_id, flag, changed_at)`), and save sync state after the push, so a crash causes a harmless re-push.

Add a guard that halts the run if more than about 20% of rows change, so a null column cannot overwrite good scores.

Covered in [Reverse ETL](09-reverse-etl.md).
</details>
