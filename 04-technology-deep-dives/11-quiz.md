# Module 4 Quiz: Technology Deep Dives

Fifteen questions on the tools you are most likely to be asked about in depth: when to pick each one, what breaks, and what the interviewer probes next. Answer each one out loud first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. One task, one hour

A nightly Spark job joins 800 GB of events to a 5 GB customers table and then aggregates by `customer_id`. The Spark UI shows 2,000 tasks that finish in about 20 seconds each and one task that has been running for an hour. Walk through what you do.

<details>
<summary>Answer</summary>

This is skew: one key holds far more rows than the others, so one shuffle partition is huge and the stage waits for it. Confirm it in the UI (one task far above the median, with heavy spill or shuffle read), then find the key. If it is `NULL` or a placeholder like `unknown`, filter it out or process it separately; it usually carries no business meaning. If it is a real hot customer, check that adaptive query execution's skew handling is on, since it splits oversized join partitions. For the `groupBy`, AQE does not help, so salt the key: aggregate by `(customer_id, salt)` first, then aggregate the partial results by `customer_id`.

The tempting answer is "add more executors" or "raise the shuffle partition count". Neither helps: all rows of one key still land in one partition, and the other 2,000 tasks were already fast.

A 5 GB customers table is a broadcast candidate only if it fits in executor memory with headroom; the 10 MB default cutoff will not pick it automatically.

Covered in [Spark Internals](01-spark-internals.md).
</details>

### Q2. Choosing the key and the partition count

You are designing a Kafka topic for order events. Downstream consumers need each order's events (created, paid, shipped, refunded) in the order they happened. Peak load is 35 MB/s. A teammate proposes `user_id` as the key and 1 partition "so ordering is guaranteed". What do you say?

<details>
<summary>Answer</summary>

Kafka orders messages only within a partition, so key by the entity whose order matters: `order_id`. One order's events hash to one partition and stay in sequence, while different orders spread out. Keying by `user_id` also keeps an order's events together, but a hot user becomes a hot partition, and it still does not give the global order the teammate wants.

One partition gives global order but caps the topic at roughly 10 MB/s and lets only one consumer per group read it. At 35 MB/s you need at least 4 partitions; about 12 gives consumer parallelism and headroom. Choose the count up front, because adding partitions later changes the key-to-partition mapping and breaks ordering for keys that are already in flight. Do not overshoot to 1,000 "just in case"; partitions cost memory, open files and recovery time.

The tempting answer is to chase total order. Almost no pipeline needs it; per-entity order is enough and scales.

Covered in [Kafka](02-kafka.md).
</details>

### Q3. Delete or compact (multiple choice)

A topic carries change events from a `customers` table, keyed by primary key. One team reads it to rebuild a "current customer" cache after restarts. Another team wants to replay the last 30 days of changes to recompute a metric. What is the right setup?

- A. `cleanup.policy=compact` on the topic, which serves both teams
- B. `cleanup.policy=delete` with 7-day retention, which serves both teams
- C. Compaction for the cache topic; a delete policy with 30-day retention, or a raw copy in object storage, for the replay
- D. Compaction with `retention.ms` set to 30 days, because compaction keeps every message for that long

<details>
<summary>Answer</summary>

**C.** Compaction keeps at least the latest message per key and eventually discards older ones. That is state: right for rebuilding a cache, wrong for replaying history.

A is the tempting answer because the cache team is happy, but the replay team would see only the final value per customer, so any metric built from the sequence of changes would be wrong. B fails the other way: 7 days is too short for a 30-day replay, and customers who have not changed recently would age out, so the cache could not be rebuilt. D misreads compaction: it is not a time-based hold, and it runs eventually, not on a schedule you can rely on.

In practice, run two outputs: a compacted topic for state, and a longer-retention topic or object-storage copy for history.

Covered in [Kafka](02-kafka.md).
</details>

### Q4. The rerun that doubled revenue

A daily Airflow task loads orders with `WHERE order_date = current_date - 1` and appends them to a reporting table. A worker crashes after the insert but before the task is marked successful, and Airflow retries it. Two days later the team backfills a week. What goes wrong, and how do you fix the design?

<details>
<summary>Answer</summary>

Two bugs. The retry appends the same rows again, so that day's revenue doubles: the task is not idempotent. The backfill then loads the wrong data: `current_date` is the day the task runs, not the day it is for, so every backfilled run reloads yesterday.

The fix is to tie each run to its data interval. Read `data_interval_start` and `data_interval_end` from the task context, and write by interval: delete that slice and insert it in one transaction, or overwrite the partition, or MERGE on a key. Then a retry replaces the partial output, and a backfill processes exactly the slice each run is for. Put non-repeatable effects (an email, a payment call) in their own task with a dedup key.

The tempting fix is "set retries to 0 so it can't double". That turns every transient failure into a page, and does nothing for the backfill.

Version caveat: in Airflow 3 a bare cron string defaults to a timetable with no real interval, so name an interval timetable explicitly.

Covered in [Airflow](03-airflow.md).
</details>

### Q5. What an asset update means (multiple choice)

A downstream Airflow DAG is scheduled on an asset that an upstream DAG updates. The upstream task succeeded, yet the dashboard shows wrong numbers because the load had a bug. A colleague says the asset trigger is broken. What is the accurate statement?

- A. The trigger is broken: assets only fire when the data passes quality checks
- B. The trigger worked as designed: an asset update means the producer task succeeded, not that the data is correct
- C. The downstream DAG should have used a sensor, because assets cannot express data dependencies
- D. The trigger is broken: assets fire on the clock, so they cannot know the upstream outcome

<details>
<summary>Answer</summary>

**B.** Assets let a DAG run when upstream data was updated instead of at a clock time, and the signal is "the producer succeeded". Correctness is separate: add validation tasks in the producer, a gate before the consumer, or tests in the transform layer.

A is the tempting answer because "updated" sounds like "good". Airflow has no idea what is in the table. C is wrong because assets are the preferred way to express cross-DAG dependencies; the older options (a sensor on another DAG's task, an explicit trigger) couple DAGs to the clock or to each other's internals. D is wrong because assets exist precisely to avoid clock coupling.

Orchestration decides when and in what order; quality is its own step. Put the check before the signal, so a bad load fails the producer and never publishes the asset.

Covered in [Airflow](03-airflow.md).
</details>

### Q6. The incremental model that drifted

Your `fct_orders` dbt model is incremental with `unique_key = order_id` and a filter `updated_at > (select max(updated_at) from this)`. Three weeks in, finance finds it is 0.4 percent off a full rebuild. List the causes you would check and the design that prevents them.

<details>
<summary>Answer</summary>

This is drift, the known weakness of incremental models. Check, roughly in order of likelihood: late or backdated rows with an `updated_at` older than the current max, which the filter never sees; hard deletes in the source, which an incremental filter cannot detect; a logic change in the model that only applies to new rows while old rows keep the old logic; and a `unique_key` that is not actually unique in the incoming batch, so the merge picks arbitrary rows.

Diagnose by full-refreshing into a scratch schema and diffing against production. Prevent it with a lookback window (re-read the last 1 to 3 days, sized to the 99th percentile of lateness), a `unique` test on the key, a plan for deletes (soft deletes or CDC), and a scheduled full refresh, say weekly, so drift is bounded instead of permanent.

The tempting answer is "ignore it, 0.4 percent is small". For finance it is a reconciliation failure, and silent drift is worse than a loud failure.

Covered in [dbt](04-dbt.md).
</details>

### Q7. Nine o'clock at the dashboard

Your company runs everything on one large Snowflake warehouse. At 9 a.m., 200 analysts open dashboards and queries queue; at the same time the ETL load slows down, and finance asks why the bill is so high. What do you change?

<details>
<summary>Answer</summary>

Separate the workloads, because storage and compute are decoupled: give ETL its own warehouse and BI its own, over the same tables. There is no data copy and no contention. Make the BI warehouse multi-cluster, sized for a typical query and scaled out for concurrency, with a short auto-suspend.

Queueing is a concurrency problem (about 8 concurrent queries per cluster by default), so scale out with more clusters. Scaling up helps one heavy or spilling query, not a crowd of light ones. For the bill, compute credits dominate: look at credits per warehouse per hour for idle time and oversized warehouses, add resource monitors and timeouts, and move full rebuilds to incremental. Materializing the heaviest dashboard model makes each query light and lets the result cache work.

The tempting answer is "make the warehouse bigger". Each size up doubles the cost, does not reduce queueing, and keeps ETL and BI fighting for the same compute.

Covered in [Snowflake](05-snowflake.md).
</details>

### Q8. A clustering key on every table (multiple choice)

A new engineer proposes adding a clustering key to every Snowflake table "to make queries fast". For which table is it clearly the wrong choice?

- A. A multi-terabyte table filtered daily on `customer_id`, where the query profile shows most micro-partitions scanned
- B. A multi-terabyte events table filtered by `region` and `event_type`, with poor pruning in the profile
- C. A multi-terabyte clickstream table filtered by `event_date`, loaded out of order by backfills and late data, with poor pruning
- D. An append-only fact table loaded by day and always filtered by load date

<details>
<summary>Answer</summary>

**D.** Data arrives in load-date order, so micro-partitions are already ordered by the column everyone filters on. Pruning is already excellent, and a clustering key would only add continuing re-clustering credits for no gain.

A, B and C are the textbook cases from the lesson: very large tables, regular filters on columns that do not match the load order, and measured poor pruning. The tempting wrong pick is A, because `customer_id` sounds like a high-cardinality column to avoid. The warning is about unique IDs, which make re-clustering never stop; a repeated customer key on a scattered table is a fair candidate. The rule: add a key only to large tables with measured poor pruning, choose low-to-moderate cardinality filter columns, and measure before and after.

Covered in [Snowflake](05-snowflake.md).
</details>

### Q9. The two-hour MERGE and the 60-day question

An hourly job MERGEs 50,000 changed orders into a 2 TB Delta table partitioned by day. It now takes two hours. Separately, an auditor asks to read the table as it was 60 days ago. What do you do about each?

<details>
<summary>Answer</summary>

For the MERGE: Delta rewrites every file containing a matching row, and without a partition predicate it checks the statistics of all files. Changed orders are in the last couple of days, so add a predicate such as `t.order_date >= current_date() - 2` to the `ON` clause. Then only a few GB are candidates and the MERGE rewrites a handful of files. Also deduplicate the source on the merge key (duplicates make a MERGE fail), compact small files first, and consider deletion vectors so updates do not rewrite whole files.

For the audit: not by default. Time travel lasts as long as the data files do, 7 days, and VACUUM deletes the removed files after that. Raising `deletedFileRetentionDuration` and the log retention to 60 days works but costs storage on a table that rewrites a lot. For a recurring need, keep dated snapshots instead.

The tempting answer to the MERGE is "add more compute". That hides a design problem: cost follows the files touched, not the number of changed rows.

Covered in [Delta Lake](06-delta-lake.md).
</details>

### Q10. Slower every month

A self-managed Iceberg table was fast at launch. Three months later, queries take much longer, planning takes seconds, and the storage bill has grown faster than the data. Nobody changed the queries. Diagnose and fix.

<details>
<summary>Answer</summary>

Almost always maintenance nobody scheduled. Frequent commits create many small data files, row-level changes pile up delete files, each commit adds manifests, and unexpired snapshots keep old files alive. Check the `.files` and `.manifests` metadata tables: an average file size well below about 32 MB, thousands of manifests or many delete files confirms it.

The fix is the four maintenance jobs, on a schedule: compact data files toward 128 MB to 1 GB, rewrite manifests, expire snapshots (decide how far back time travel must go), and remove orphan files left by failed writes. Also review the commit frequency: more commits mean more small files and manifests, and even one commit a minute needs scheduled compaction.

The tempting answer is "the format is the problem, move to another one". Delta has the same duties in open-source form (OPTIMIZE, VACUUM). Format choice does not remove maintenance; only a managed service takes it over.

Covered in [Iceberg](07-iceberg.md).
</details>

### Q11. Delta or Iceberg (multiple choice)

A company has Spark jobs on a lakehouse, a separate SQL engine for analysts, and a streaming engine for features. All three must read and write the same tables, and the company does not want to depend on one vendor. Which choice and reasoning is best?

- A. Iceberg, with a REST catalog, because engine neutrality is the deciding factor and the catalog is now where lock-in lives
- B. Delta Lake, because it is always faster than Iceberg for MERGE
- C. Hudi, because it is the default for all multi-engine setups
- D. Neither; keep raw Parquet files and let each engine manage its own copy

<details>
<summary>Answer</summary>

**A.** Iceberg was designed for engine neutrality. With several engines, the catalog is the coordination point (the commit is an atomic swap of its pointer), and a neutral REST catalog keeps that point from tying you to one vendor. Delta is a strong pick for Spark and Databricks stacks, and with UniForm it can be read as Iceberg, but these constraints point to Iceberg.

B is a false general claim; performance depends on engine, layout and maintenance, and the question is about neutrality. C overstates: Hudi's niche is upsert-heavy streaming ingestion. D throws away ACID and consistent reads, and per-engine copies would diverge.

Add the cost: someone must schedule compaction, snapshot expiry and orphan cleanup, and each engine must support the spec version you use.

Covered in [Iceberg](07-iceberg.md) (see its Delta vs Iceberg vs Hudi comparison); UniForm is in [Delta Lake](06-delta-lake.md).
</details>

### Q12. The windows that never close

A Flink job reads a 12-partition Kafka topic and computes per-minute counts with event-time tumbling windows. It runs fine for hours, then results stop appearing, though CPU is idle and the source is still receiving data on most partitions. What happened, and what is the tradeoff in the fix?

<details>
<summary>Answer</summary>

One or more Kafka partitions went quiet. Each source subtask tracks its own watermark, and an operator with several inputs uses the minimum of them. A partition with no events does not advance its watermark, so it holds back the whole job, and no window can fire because the watermark never passes the window end. This is the idle-partition stall.

The fix is an idle timeout on the watermark strategy: an input silent for, say, 30 seconds is ignored when computing the minimum. The cost is that when the partition wakes up, its events may arrive behind the watermark and count as late. Pair it with allowed lateness and a side output for late events instead of silently dropping them, the failure interviewers probe for.

The tempting answer is "the job is stuck, restart it". A restart restores the same state, and the quiet partition would stall it again. Backpressure is another wrong guess; it shows a busy bottleneck operator, not idle CPU.

Covered in [Flink](08-flink.md).
</details>

### Q13. Is the Flink job exactly-once (multiple choice)

An interviewer asks, "Is your Flink job exactly-once?" The job reads Kafka and writes counts to a key-value store with plain `INSERT` calls. Which answer is most accurate?

- A. Yes, checkpointing makes the whole pipeline exactly-once
- B. No, Flink can only offer at-least-once
- C. State is exactly-once via checkpoints; output is only exactly-once if the sink is idempotent or joins a two-phase commit tied to the checkpoint, so this sink will show duplicates after a restart
- D. Yes, as long as the checkpoint interval is under one minute

<details>
<summary>Answer</summary>

**C.** Checkpoints make Flink's own state reflect each input record exactly once: on failure it restores the last complete checkpoint and rewinds the source to the saved offsets. Output written between that checkpoint and the crash is written again on replay, and plain inserts are neither idempotent nor transactional, so duplicates appear. Fix it with an upsert on a key, or a two-phase commit sink, where output becomes visible only when the checkpoint completes.

A is the answer the interviewer is fishing for; it stops at the engine boundary. B undersells Flink, which does offer exactly-once with the right sink. D confuses latency with correctness: the interval changes how much is replayed, not whether duplicates occur.

Add the consequence: with a two-phase commit sink, the checkpoint interval is your latency floor.

Covered in [Flink](08-flink.md).
</details>

### Q14. The healthy connector and the full disk

A Debezium Postgres connector shows `RUNNING` and no errors, but the primary database is losing disk space steadily. The connector captures only a few small, quiet tables; other tables in the same instance are written heavily. Why is the disk filling, and how do you prevent it?

<details>
<summary>Answer</summary>

The replication slot only advances when the connector confirms a position, and the connector only learns positions from events on tables it captures. When the captured tables are idle, nothing is confirmed while the rest of the instance keeps writing WAL, and Postgres must retain all of it behind the slot. At a 5 MB/s write rate that is about 430 GB a day, so a 100 GB free disk lasts under 6 hours. The connector looks fine while this happens.

Defences, in order: enable heartbeats (`heartbeat.interval.ms` plus an action query that writes to a small table), so the connector produces its own events and the slot advances; alert on slot lag in bytes, not only connector status; set `max_slot_wal_keep_size` so the database sacrifices the slot rather than itself, accepting a re-snapshot; and drop slots left by deleted connectors.

The tempting diagnosis is "the connector is broken" and the fix a restart. Status checks pass, so the monitoring that matters is freshness and slot lag.

Covered in [Debezium and CDC Tools](09-debezium-and-cdc-tools.md).
</details>

### Q15. Two engineers, sixty pipelines

A startup with two data engineers has about 60 dated batch pipelines (Spark, dbt, SQL) on one cloud. They have no platform team and ask which orchestrator to use. The interviewer then asks what would change your answer.

<details>
<summary>Answer</summary>

Default to managed Airflow. The workload is dated batch work, and Airflow's time model (data intervals, catchup, backfills) and ecosystem fit it; managed removes the scheduler, database and worker operations that two people should not carry. Say the cost: an always-on environment fee in the hundreds of dollars a month, version lag, and no cure for bad DAG design. Keep tasks thin and idempotent so the orchestrator only decides when and in what order, which also makes a later move possible.

What would change it: a greenfield team that thinks in datasets, lineage and checks leans Dagster; a few event-driven glue steps between cloud services point to a cloud workflow service, which is weak at dated backfills; a Python-first team with few pipelines might take Prefect. If it were one warehouse with SQL only, a scheduled dbt run may need no orchestrator at all.

The tempting answer is to self-host the most flexible tool. For two people, running the scheduler, database and workers is the wrong use of time.

Covered in [Orchestrator Comparison](10-orchestrator-comparison.md), with the Airflow details in [Airflow](03-airflow.md).
</details>
