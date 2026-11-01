# Glossary

Every lesson defines its terms the first time it uses them. This page exists so those definitions stay the same across the whole course. If a lesson and this page ever seem to disagree, treat it as a bug. Each entry ends with the lesson that teaches the term most directly.

## A

**Access pattern** — How a dataset will be read: which queries, by whom, how often, scanning a lot or looking up a little. It decides table layout and the serving store. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

**At-least-once** — A delivery guarantee where every event is delivered one or more times, so nothing is lost but duplicates can happen. Pair it with an idempotent write or a deduplication step to get correct results. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

## B

**Backfill** — Re-running a pipeline over a past time range to fill in missing data or to correct data that was wrong. A safe backfill relies on idempotent jobs so it can be repeated without double-counting. See: [Backfill and Reprocessing](02-core-concepts/03-backfill-and-reprocessing.md)

**Back-of-envelope estimate** — A quick, rounded calculation (events per second, TB per day, partitions needed) done aloud to see whether a design is feasible. Its job is to change a design decision, not to be precise. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

**Bad → Good → Great** — A way to compare options for one design decision: a Bad option that fails a requirement, a Good one that works with known gaps, and a Great one that closes the gaps at a stated cost. Choose the level your requirements justify, not the highest. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Below the line** — Explicitly out of scope. In the framework you list your requirements, draw a line under them, and write what you are deliberately not building beneath it. See: [The Delivery Framework](01-the-framework/02-delivery-framework.md)

## C

**CDC (change data capture)** — Reading a database's change log (inserts, updates and deletes) and streaming those changes to other systems, instead of repeatedly querying the tables. See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Clustering** — Ordering rows inside each partition by another column (also called sorting) so that queries filtering on it can skip blocks using min/max statistics. It is the fine cut after partitioning's coarse one, and it decays as unsorted data arrives. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Columnar format** — A file format (such as Parquet) that stores each column's values together instead of one row at a time. It compresses well and lets a query read only the columns it needs. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

**Compaction** — Rewriting many small files into fewer, larger ones so queries open fewer files. Table formats such as Iceberg and Delta Lake provide it as a maintenance operation that you schedule, or that a managed service runs for you. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Completeness** — The share of the data you expected that has actually arrived, for example "99.9% of yesterday's events are loaded". One of the three common data SLAs, next to freshness and quality. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Consumer** — Whoever reads the output of a data system: an analyst, a dashboard, an ML model or another team's pipeline. A data design is judged by how well it serves its consumers. See: [How Interviews Work](01-the-framework/01-how-interviews-work.md)

## D

**DAG (directed acyclic graph)** — The set of tasks in a pipeline with arrows meaning "must finish before" and no loops. An orchestrator runs it and tracks which tasks succeeded. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Data contract** — An explicit, versioned agreement between a data producer and its consumers about a dataset's schema, meaning, quality and delivery expectations. Its purpose is to make breaking changes visible before they reach consumers. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Dead-letter queue (DLQ)** — A separate topic or table where records that cannot be processed are set aside, with the error reason, so the main flow keeps running. Alert on its rate, fix the cause, then replay the records. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Deep dive** — A stretch of the interview where you go one level below the architecture diagram on a single topic, such as how to avoid double-counting after a replay. See: [The Delivery Framework](01-the-framework/02-delivery-framework.md)

## E

**Dimension** — A table describing the things an event involved (customer, product, delivery slot). Dimensions are small and descriptive; you filter and group by their columns. Compare with fact table. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Error budget** — The amount of failure an SLO allows: a 99% target over 365 days permits about 3 to 4 misses a year. Once it is spent, you pause risky changes and fix reliability. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Event time** — The moment an event actually happened, as recorded by the source (for example, when a user tapped "buy"). Compare with processing time. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Exactly-once** — The effect of processing each event once, with no loss and no duplicates. In practice it is built from at-least-once delivery plus idempotent writes or transactions, not from a network that never repeats itself. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

## F

**Fact table** — A table with one row per event at a chosen grain (an order line, a click), holding numeric measures to add up plus keys that point to dimensions. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Fan-out** — One input feeding many consumers or many downstream tasks, for example one Kafka topic read by five independent services. It multiplies reads, so plan capacity for the total, not for the single input. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Freshness** — How old the newest data in a table or dashboard is compared with now, for example "no more than 15 minutes behind the source". One of the three common data SLAs, next to completeness and quality. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Full load** — Reading the whole source on every run and replacing your copy. Simple and handles deletes for free, but the work grows with the table. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)

**Functional requirement** — Something the system must produce or do, stated from the consumer's side, such as "marketing sees conversions per campaign". In a data system it is usually an output table, metric or feed. Compare with non-functional requirement. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

## G

**Grain** — What exactly one row in a table represents, such as "one order line" or "one user per day". Decide the grain first; every column and every join follows from it. See: [Data Model Design](01-the-framework/06-data-model-design.md)

## H

**Hot partition** — A partition that receives far more traffic or data than the others, usually because the partition key is skewed (one huge customer, one viral item). It becomes the bottleneck for the whole system. See: [Partitioning](02-core-concepts/01-partitioning.md)

## I

**Idempotent** — An operation that gives the same end result whether it runs once or many times. Idempotent pipeline steps can be retried or replayed safely. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Incremental load** — Reading only the rows that are new or changed since the last run, usually with a watermark column. Cheaper per run than a full load, but it misses hard deletes unless handled. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)

## L

**Late data** — An event that arrives after the system has already moved past its event time, for example a mobile event uploaded two hours after it happened. You must decide whether to drop it, include it in a correction, or hold results back to wait for it. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

## M

**Medallion layers** — A way to organize a lakehouse into stages of increasing quality: bronze (raw as received), silver (cleaned and conformed) and gold (modeled for consumers). See: [Medallion Architecture](03-architecture-patterns/03-medallion-architecture.md)

**Message log** — A durable, ordered, replayable queue of events (Kafka is the common one). Consumers read at their own pace and can re-read from an earlier point, which makes recovery and reprocessing possible. See: [Kafka](04-technology-deep-dives/02-kafka.md)

## N

**Non-functional requirement (NFR)** — A measurable quality of how well a system does its job: freshness, completeness, correctness, retention, query speed, cost. It only counts as a requirement once it has a number. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

## O

**Object storage** — Cheap, durable storage that holds files as objects in flat buckets and is accessed over an API (S3, GCS, Azure Blob). It is the usual base layer of a data lake. Objects are written whole and are not edited in place. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Observability** — Being able to answer "why is this unhealthy?" without guessing, using per-stage metrics, run history, lineage and logs. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**OLAP (online analytical processing)** — Workloads that scan and aggregate large amounts of data to answer questions, such as "revenue by region by month". Column-oriented warehouses are built for it. Compare with OLTP, which handles many small reads and writes to individual rows. See: [Snowflake and Cloud Warehouses](04-technology-deep-dives/05-snowflake.md)

**Orchestrator** — The tool (Airflow, Dagster, Prefect and similar) that runs a DAG of tasks, waits on dependencies, retries failures and records what ran. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

## P

**Partition** — A slice of a dataset or stream, chosen by a key or a range, that can be stored and processed independently. Partitions are how data systems spread work across machines and skip data they don't need. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Partition overwrite** — Making a run replace exactly one partition of the output (for example one date) instead of appending to it, so a rerun gives the same result. The default idempotent write for dated batch outputs. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Partition pruning** — The engine dropping every partition that cannot match a query's filter before reading any data. It only works when the filter is on the partition column itself, not a function of it. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Processing time** — The moment a system handles an event, as opposed to when it happened. Processing time is almost always later than event time, and the gap is what makes late data possible. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

## R

**Rate limit** — A cap a pull API puts on how many requests you may make per minute. It sets how fast you can read or backfill history from that source, whatever your own cluster could do. See: [Sources and Volume](01-the-framework/04-sources-and-volume.md)

**Raw layer** — The first stored copy of data, kept close to how it arrived (also called bronze). It lets you rerun cleaning logic after a bug without asking the source to resend. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Read replica** — A copy of a database kept in sync with the primary and used for reading, so heavy extracts or CDC do not slow the live application. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Reconciliation** — Comparing your output with an independent source of truth (for example daily revenue against the payments provider's totals) and investigating any gap beyond a set tolerance. See: [Deep Dives](01-the-framework/08-deep-dives.md)

**Retention** — How long data is kept before it is deleted or moved to cheaper storage, including any rule to delete a person's data on request. Raw volume times retention is the storage bill. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

## S

**Salting** — Adding a small random suffix to a hot key so its records spread over several partitions. Readers must then merge those slices, and ordering across them is lost. See: [Partitioning](02-core-concepts/01-partitioning.md)

**SCD (slowly changing dimension)** — A technique for keeping a dimension table correct when its attributes change over time, such as a customer moving city. Type 1 overwrites the old value; Type 2 adds a new row with validity dates so history is preserved. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Schema evolution** — Changing a dataset's schema (adding, dropping, renaming or retyping columns) while existing data and readers keep working. Adding an optional column is usually safe; renaming or retyping often breaks consumers. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Serving layer** — The final tables or stores that consumers read, kept small and shaped for their questions so internal changes do not break them. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Skew** — Uneven load across partitions or workers, such as one city producing a third of the orders, so one slow task decides how long the whole job takes. Fix it with a different or compound key. See: [Partitioning](02-core-concepts/01-partitioning.md)

**SLA / SLO** — An SLO (service level objective) is a target you set for a measurable quality, such as "the daily table is ready by 07:00 on 99% of days". An SLA (service level agreement) is an SLO that has been promised to someone and usually has consequences if it is missed. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Small-files problem** — Too many tiny files in storage (often from frequent streaming writes), which makes listing and opening them dominate query time. The fix is to write bigger files or run compaction. See: [Partitioning](02-core-concepts/01-partitioning.md)

## T

**Source** — Any system a pipeline reads from but does not control: an operational database, an event stream, files, a pull API or a webhook. The type of source decides how the data can be read and how it can fail. See: [Sources and Volume](01-the-framework/04-sources-and-volume.md)

**Star schema** — A model with one central fact table surrounded by dimension tables, joined at query time. It keeps each descriptive value in one place. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Table format** — A metadata layer (Iceberg, Delta Lake, Hudi) that turns a pile of files in object storage into a table with transactions, schema changes and snapshots. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Throughput** — How much data a component moves per unit of time, such as MB/s per Kafka partition or events/s per pipeline. Compare with latency, which is how long one operation takes. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

## U

**Upsert (MERGE)** — Writing a row if its key is new and updating it if the key already exists. Applying the same batch twice changes nothing, which makes it an idempotent write for tables of entities. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Z-order** — A layout that interleaves the sort order of several columns so rows close in all of them sit near each other, giving moderate data skipping on any of those columns. See: [Partitioning](02-core-concepts/01-partitioning.md)

## W

**Wide table (OBT)** — A table that joins facts and dimensions ahead of time so every row carries all the columns a consumer needs and queries need no joins. Also called one big table. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Watermark** — A stream processor's running estimate of how far event time has progressed, which says "I don't expect events older than this anymore". It decides when a time window can be closed and its result emitted. Not the same as an ingestion "watermark column", which is the last value a batch load has already copied. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)


**Watermark column** — A column that only moves forward (usually `updated_at`) whose largest loaded value is stored, so the next incremental run asks only for rows beyond it. Misses hard deletes and late commits unless you add an overlap window. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)