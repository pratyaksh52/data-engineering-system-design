# Glossary

Every lesson defines its terms the first time it uses them. This page exists so those definitions stay the same across the whole course. If a lesson and this page ever seem to disagree, treat it as a bug. Each entry ends with the lesson that teaches the term most directly.

## A

**A/B test** — Showing a new version (such as a new ranking model) to a random slice of users and comparing outcomes with the current one. A model that wins offline and loses its A/B test often points to bad training data. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Access pattern** — How a dataset will be read: which queries, by whom, how often, scanning a lot or looking up a little. It decides table layout and the serving store. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

**Accumulating snapshot** — A fact table with one row per item moving through a fixed process (an order line from paid to shipped to delivered) and one timestamp column per milestone, filled in as each happens. It is the fact table you update in place. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

**Adaptive query execution (AQE)** — Spark's runtime re-optimization, on by default since 3.2: it uses real shuffle sizes to merge small partitions, switch a join to broadcast, and split skewed join partitions. It does not fix a skewed group-by. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Admission control** — Deciding, before a query or job starts, whether it may run now, must wait in a queue, or is refused, using limits such as per-tenant concurrency and an estimate of bytes to scan. It stops one tenant from taking a shared pool. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Affinity (feed ranking)** — A score for a (viewer, author) pair built from the viewer's past interactions with that author (views, reactions, comments), computed in batch and read by the feed ranker. See: [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)

**Alert fatigue** — What happens when a team gets so many alerts that it stops acting on them, including the real ones. Measure it by checking how many of the last 30 pages needed a human. See: [Monitoring and Alerting](02-core-concepts/06-monitoring-and-alerting.md)

**Allowed lateness** — Extra time a stream processor keeps a window's state after the watermark has passed it, so an event arriving in that period triggers a corrected result instead of being discarded. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Anomaly detection** — Automatically flagging a value that differs from its usual pattern, in its simplest useful form a same-weekday baseline with a tolerance. Reserve it for a few high-value metrics, because every threshold on a noisy number produces some false alarms. See: [Monitoring and Alerting](02-core-concepts/06-monitoring-and-alerting.md)

**Approximate nearest neighbour (ANN) index** — A structure built over many embeddings (HNSW, a layered graph, is the common algorithm) that returns the closest few hundred to a query vector in about a millisecond, accepting it may miss a few true neighbours. Rebuilt in full when the embedding version changes. See: [Design an E-Commerce Recommendation Engine That Stays Fresh](06-breakdowns-advanced/06-recommendation-engine.md)

**Asset (Airflow)** — A logical dataset that an Airflow task declares it updates; other DAGs can schedule on it instead of on a clock (data-aware scheduling). Called a dataset before Airflow 3. See: [Airflow](04-technology-deep-dives/03-airflow.md)

**Asset-centric orchestration** — An orchestrator model (Dagster's) where each node is a dataset that should exist plus the function that builds it, so lineage, freshness and partitioned backfills attach to data. Contrast task-centric tools (Airflow, Prefect), where a node is a step. See: [Orchestrator Comparison](04-technology-deep-dives/10-orchestrator-comparison.md)

**At-least-once** — A delivery guarantee where every event is delivered one or more times, so nothing is lost but duplicates can happen. Pair it with an idempotent write or a deduplication step to get correct results. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Attribution** — Deciding which ad or recommendation, if any, gets credit for a later action such as a purchase or a play, using a stated rule (for example last touch, clicks before views). See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Attribution window** — How long after an ad interaction a purchase can still be credited to it, such as 14 days after a click or 1 day after a viewed impression. Numbers reported by ad date keep growing until the window closes. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

## B

**Back-of-envelope estimate** — A quick, rounded calculation (events per second, TB per day, partitions needed) done aloud to see whether a design is feasible. Its job is to change a design decision, not to be precise. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

**Backfill** — Re-running a pipeline over a past time range to fill in missing data or to correct data that was wrong. A safe backfill relies on idempotent jobs so it can be repeated without double-counting. See: [Backfill and Reprocessing](02-core-concepts/03-backfill-and-reprocessing.md)

**Backpressure** — What happens when a stream operator cannot keep up: bounded buffers fill, upstream operators block, and the slowdown reaches the source, so lag rises instead of data being dropped. Fix the first busy operator, not the source. See: [Flink](04-technology-deep-dives/08-flink.md)

**Bad → Good → Great** — A way to compare options for one design decision: a Bad option that fails a requirement, a Good one that works with known gaps, and a Great one that closes the gaps at a stated cost. Choose the level your requirements justify, not the highest. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Below the line** — Explicitly out of scope. In the framework you list your requirements, draw a line under them, and write what you are deliberately not building beneath it. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

**Blast radius** — How much breaks when one thing breaks. A platform keeps it small by design, for example one generated DAG file per pipeline so a bad config takes out one pipeline, not thousands. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)

**Blocking check** — A data quality check whose failure stops a partition from being published (and holds what depends on it); a warning check publishes and flags instead. Block on what is never acceptable, warn on what is merely unusual. See: [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)

**Bloom filter** — A compact structure that answers "have I seen this key?" with "definitely not" or "probably yes". It never forgets a key but has a tunable false-positive rate, so it fits approximate dedup, not payments. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Bridge model** — A multi-tenant layout that pools most tenants on shared tables and compute and silos a few (the largest, or those whose contracts require it), with each tenant's tier kept as data in a registry so the code stays the same. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Broadcast join** — A join where the small table is copied to every executor so the big table is never shuffled. Fast, but the small side must fit in memory. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Broker** — A server in a Kafka cluster that stores partitions and serves producers and consumers. A cluster is several brokers, so a partition can be copied to more than one. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Budget pacing** — The feedback loop that sends each ad campaign's spend so far back to the ad server, so it stops serving the campaign when the daily budget is used up. Late or missing spend means ads served that cannot be billed. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Bundle manifest** — A record that deploys an ML model together with the exact data versions it was trained with (catalog snapshot, feature view versions, label version), so serving never mixes a model with data from another version. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Bus matrix** — A grid of which fact tables use which dimensions. It shows at a glance which dimensions must be conformed so numbers from different facts line up. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

## C

**Candidate generation** — The first stage of answering a recommendation request: cheaply picking a few hundred plausible items out of millions from several candidate sources (similar items, bought-together lists, trending), which a ranking model then scores. See: [Design an E-Commerce Recommendation Engine That Stays Fresh](06-breakdowns-advanced/06-recommendation-engine.md)

**Card testing** — A fraud attack where a script tries many stolen card numbers with small payments, usually from one device or IP, to find which still work. Per-card counts look normal; device and IP velocity features catch it. See: [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)

**Catchup** — The Airflow setting that makes the scheduler create a run for every missed interval since the start date. Off by default in Airflow 3. See: [Airflow](04-technology-deep-dives/03-airflow.md)

**CDC (change data capture)** — Reading a database's change log (inserts, updates and deletes) and streaming those changes to other systems, instead of repeatedly querying the tables. See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Change data feed (CDF)** — A Delta Lake option that records row-level changes (insert, update before and after, delete) on each write and exposes them for reading, so downstream jobs process only what changed. It starts from the version where it was enabled. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Chargeback** — A payment reversed by the cardholder's bank after a dispute, such as "I didn't make this payment". Fraud chargebacks are the main fraud label and arrive weeks to about four months after the payment. See: [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)

**Checkpoint** — Durable storage where a streaming job records its progress (source offsets and operator state), so a restart resumes from the last good point instead of starting over. See: [Micro-Batch vs Streaming](03-architecture-patterns/08-micro-batch-vs-streaming.md)

**Checkpoint barrier** — A marker Flink injects into the data stream; when an operator sees it, everything before belongs to that checkpoint, so the job gets a consistent snapshot without stopping. See: [Flink](04-technology-deep-dives/08-flink.md)

**Circuit breaker** — A switch that, after repeated failures against one dependency, stops sending it requests for a while and probes until it recovers, instead of letting every caller retry. It turns one outage into one alert and a controlled resume. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)

**Classification tag** — A label on a column saying what kind of data it holds (`pii.email`, `restricted.region`), set at onboarding, suggested by scanners and inherited through lineage, so access policies can be written against tags instead of tables. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Clustering** — Ordering rows inside each partition by another column (also called sorting) so that queries filtering on it can skip blocks using min/max statistics. It is the fine cut after partitioning's coarse one, and it decays as unsorted data arrives. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Co-occurrence list** — For each item, the other items most often bought or viewed in the same sessions, with a score; a precomputed "bought together" candidate source looked up by key at request time. See: [Design an E-Commerce Recommendation Engine That Stays Fresh](06-breakdowns-advanced/06-recommendation-engine.md)

**Column pruning** — Reading only the columns a query names, which a columnar format makes possible because each column is stored separately. `SELECT *` defeats it. See: [Cost Optimization](02-core-concepts/05-cost-optimization.md)

**Columnar format** — A file format (such as Parquet) that stores each column's values together instead of one row at a time. It compresses well and lets a query read only the columns it needs. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

**Compaction** — Rewriting many small files of a table into fewer, larger ones so queries open fewer files. Table formats such as Iceberg and Delta Lake provide it as a maintenance operation that you schedule, or that a managed service runs for you. Kafka's log compaction is a different thing. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Compatibility mode** — The rule a schema registry enforces when a new schema version is registered. BACKWARD means new-schema readers can read old data, FORWARD means old-schema readers can read new data, FULL means both, and the transitive variants check against every earlier version instead of only the latest. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Completeness** — The share of the data you expected that has actually arrived, for example "99.9% of yesterday's events are loaded". One of the three common data SLAs, next to freshness and quality. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Config-driven pipeline** — A pipeline a team describes in a short declarative file (inputs, steps, checks, outputs, schedule, owner) that a framework compiles into a running, monitored pipeline, so the team writes no orchestration code. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)

**Conformed** — Made consistent across sources: the same currency format, UTC timestamps and one customer ID wherever the concept appears. It is the main job of the silver layer. See: [Medallion Architecture](03-architecture-patterns/03-medallion-architecture.md)

**Conformed dimension** — A dimension table shared, with the same keys and meanings, by several fact tables, so "category" means the same thing for sales, returns and deliveries. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

**Consumer** — Whoever reads the output of a data system: an analyst, a dashboard, an ML model or another team's pipeline. A data design is judged by how well it serves its consumers. See: [How Data Engineering Design Interviews Work](01-the-framework/01-how-interviews-work.md)

**Consumer group** — Consumers sharing one `group.id` that split a topic's partitions between them, each partition going to exactly one consumer. Different groups read the same topic independently. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Consumer lag** — For a Kafka partition, the latest offset minus the group's committed offset: how far behind the consumers are. Rising lag is the main health signal of a streaming pipeline. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Control plane / data plane** — A platform's control plane is the services that create and change things (CI, provisioner, registry); its data plane is what stores, moves and serves data. Keeping them separate means a control-plane outage blocks changes but not queries. See: [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)

**Copy-on-write** — Handling an update or delete by rewriting every data file that holds an affected row, so reads stay plain and fast but writes are expensive. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Cost attribution** — Working out what each tenant or team costs: direct costs from resources tagged to them, shared costs split by metered usage, and the unallocated rest reported as its own number. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Count-Min Sketch** — A small grid of counters for estimating how often each key appears in a huge stream: each key increments one counter per row, and its estimate is the smallest of them. It never undercounts and may overcount by a bounded amount; paired with a heap it gives approximate top-K in fixed memory. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Credential vending** — A catalog checking a user's permission on a table and handing the engine short-lived storage credentials scoped to that table's files, so no one needs broad bucket access. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Credit** — Snowflake's billing unit for compute: the smallest virtual warehouse burns 1 credit per running hour and each size up doubles it, at roughly $2 to 4 per credit. See: [Snowflake: How a Modern Cloud Warehouse Works](04-technology-deep-dives/05-snowflake.md)

**Crypto-shredding** — Deleting data by deleting the encryption key it was stored under, so every remaining copy, including backups and unexpired snapshots, becomes unreadable. Practical when a tenant has its own key. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Cube** — Pre-computed aggregates for every combination of a set of dimensions, so any filter-and-group question becomes a lookup. With many dimensions or high-cardinality ones (merchant, issuer) the combinations explode, which is why live dashboards aggregate unplanned questions at query time instead. See: [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)

## D

**DAG (directed acyclic graph)** — The set of tasks in a pipeline with arrows meaning "must finish before" and no loops. An orchestrator runs it and tracks which tasks succeeded. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Data contract** — An explicit, versioned agreement between a data producer and its consumers about a dataset's schema, meaning, quality and delivery expectations. Its purpose is to make breaking changes visible before they reach consumers. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Data diff** — A comparison of a changed pipeline's output with production's output for the same interval (row counts, keys added or lost, column sums and null rates), shown on the pull request so reviewers see the effect of a change, not only the code. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)

**Data fabric** — A metadata-driven layer across existing data systems that gives one place to discover, understand, access and govern data where it lives. Its parts (catalog, automated lineage, federated query, central policy) are useful; the name is largely vendor packaging. See: [Data Fabric](03-architecture-patterns/07-data-fabric.md)

**Data interval** — The slice of event time an orchestrator run is responsible for (for example Oct 31 00:00 to Nov 1 00:00), independent of when the run actually starts. Reading it, not the clock, keeps reruns and backfills correct. See: [Airflow](04-technology-deep-dives/03-airflow.md)

**Data lake** — Tables stored as open files (usually Parquet) in object storage, organized by a table format and read by several query engines. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Data leakage** — Training rows that contain information the model could not have had at prediction time, such as joining last year's labels to today's feature values. Offline metrics look better and production gets worse. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Data lineage** — A record of where data came from and what was built from it: which sources feed which tables, which jobs produced them and which dashboards and models read them. Walk it downstream for impact analysis and upstream for debugging. See: [Data Lineage](02-core-concepts/04-data-lineage.md)

**Data mesh** — An organisational pattern where domain teams own their analytical data as products, a self-serve platform makes that cheap, and federated governance keeps the products combinable. Worth it only with many domains and a bottlenecked central team. See: [Data Mesh](03-architecture-patterns/06-data-mesh.md)

**Data product** — A dataset published by a domain team as a product: a named owner, a contract, a catalog entry and a service level, for consumers who can rely on it. See: [Data Mesh](03-architecture-patterns/06-data-mesh.md)

**Data product descriptor** — One declarative file per data product (owner, tier, inputs, build step, output ports with contracts, classification, retention) that a mesh platform validates and compiles into storage, pipeline, policies, checks and a catalog entry. See: [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)

**Data profile** — Summary metrics for one partition (row count, null rate per column, approximate distinct counts, min, max and mean), computed in one query and stored as history so rule and anomaly checks compare against it instead of re-reading data. See: [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)

**Data swamp** — A data lake nobody can trust or navigate: files dumped into folders with no transactions, schemas, owners or catalog. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Data virtualization** — Querying data in place across several systems through one SQL interface (a federated query) instead of copying it first. Good for exploration and light joins; heavy or frequent joins should be materialised. See: [Data Fabric](03-architecture-patterns/07-data-fabric.md)

**Dead-letter queue (DLQ)** — A separate topic or table where records that cannot be processed are set aside, with the error reason, so the main flow keeps running. Alert on its rate, fix the cause, then replay the records. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Dead man's switch** — An alert that fires when an expected signal stops arriving (a heartbeat, a stream of check results), so monitoring that silently stopped running is noticed. Run it from outside the system it watches. See: [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)

**Debezium** — An open-source set of CDC connectors that read a database's transaction log and publish one change event per row change, usually through Kafka Connect. See: [Debezium and CDC Tools](04-technology-deep-dives/09-debezium-and-cdc-tools.md)

**Dedup key** — The column or columns that identify one real-world event, so two records with the same key count as one. Best created at the source before any retry. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Deduplication (dedup)** — Collapsing records that describe the same real-world event into one. In batch it is a window function or MERGE; in a stream it needs state sized by window length times event rate. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Deep dive** — A stretch of the interview where you go one level below the architecture diagram on a single topic, such as how to avoid double-counting after a replay. See: [The Delivery Framework](01-the-framework/02-delivery-framework.md)

**Deferrable operator** — An Airflow operator or sensor that hands its waiting to a single async process (the triggerer) so it holds no worker slot while it waits. See: [Airflow](04-technology-deep-dives/03-airflow.md)

**Degenerate dimension** — An identifier kept on a fact row with no dimension table of its own, such as `order_id` on an order line, so lines can be grouped without a join. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

**Deletion vector** — In Delta Lake, a small side file marking rows of a data file as deleted, so DELETE, UPDATE and MERGE avoid rewriting the whole file; a later OPTIMIZE purges the marked rows. Availability is version-dependent. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Delta Lake** — An open table format that adds a transaction log beside Parquet files in object storage, giving atomic commits, versions, schema enforcement and row-level updates. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Dimension** — A table describing the things an event involved (customer, product, delivery slot). Dimensions are small and descriptive; you filter and group by their columns. Compare with fact table. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Downsampling** — Storing lower-resolution summaries of older time-series data (one row per device per 5 minutes or per hour instead of every reading), so long-range charts stay fast and cheap. The summaries must be recomputed when late data touches them. See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

## E

**Effectively-once** — Another name for exactly-once effect: messages may travel twice, but an idempotent write or transaction makes the result as if each was processed once. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Egress** — Data leaving a cloud provider, region or zone, billed per GB (about $0.05 to 0.09 for internet egress, about $0.01 across zones). It is invisible in a diagram and obvious on the bill. See: [Cost Optimization](02-core-concepts/05-cost-optimization.md)

**ELT (extract, load, transform)** — Loading raw source data into the warehouse first and transforming it there with SQL, instead of transforming it before loading. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

**Embedding** — A list of numbers (often about 128) a model learns for each item, such as a title, so that similar items get similar numbers. Values from different training runs are not comparable, so embeddings must be versioned. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Engagement** — Any action a user takes on a post or item: a like, reply, repost, quote or bookmark. On a social network each one is usually a row in a product table, so CDC from that table gives you likes and unlikes in commit order. See: [Design Twitter/X-Style Engagement Analytics](06-breakdowns-advanced/04-social-media-analytics.md)

**Error budget** — The amount of failure an SLO allows: a 99% target over 365 days permits about 3 to 4 misses a year. Once it is spent, you pause risky changes and fix reliability. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Event sourcing** — Storing every change as an immutable, business-named event and treating the current state as something calculated from those events. CDC derives events from state; event sourcing derives state from events. See: [Event Sourcing](03-architecture-patterns/05-event-sourcing.md)

**Event time** — The moment an event actually happened, as recorded by the source (for example, when a user tapped "buy"). Compare with processing time. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Exactly-once** — The effect of processing each event once, with no loss and no duplicates. In practice it is built from at-least-once delivery plus idempotent writes or transactions, not from a network that never repeats itself. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Executor** — A Spark worker process with a few cores and some memory that runs tasks and holds cached and shuffle data. The driver schedules work onto executors. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Expand and contract** — A way to ship a breaking change safely: add the new field or version beside the old one, migrate every consumer, then remove the old one. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Exponential decay** — Keeping a count whose old contributions lose weight over time: each update multiplies the stored value by 2^(−elapsed / half-life) and adds the new weight, where the half-life is how long a contribution takes to lose half its weight. Two numbers per key replace a window of buckets, and decay can be applied lazily on the next update or read. See: [Design Twitter/X-Style Engagement Analytics](06-breakdowns-advanced/04-social-media-analytics.md)

## F

**Fact table** — A table with one row per event at a chosen grain (an order line, a click), holding numeric measures to add up plus keys that point to dimensions. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Fail open / fail closed** — What a gate does when it cannot get an answer: fail open lets the data or request through unchecked, fail closed blocks it. Choose per consumer: fail closed where wrong is worse than late. See: [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)

**Fan-out** — One input feeding many consumers or many downstream tasks, for example one Kafka topic read by five independent services. It multiplies reads, so plan capacity for the total, not for the single input. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Fan-out on write / fan-out on read** — The two ways to deliver an activity to its audience's feeds. On write (push), a copy of its ID goes into every audience member's inbox when it is created, so reads are one lookup; on read (pull), each reader fetches recent activity from everyone they follow when they open the feed. See: [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)

**Feature (ML)** — An input value a model uses, describing an entity, such as a user's order count over the last 7 days. Each training example is a row of features plus a label. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Feature logging** — Recording the exact feature values the serving path returned for each prediction (or a sample), so they can be checked against the offline store or joined to labels as training data. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Feature registry** — The catalog of a feature store: every feature view's definition, entity, source, schedule, owner, version and consuming models. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Feature store** — A shared system that defines each ML feature once and keeps two stores in agreement: an offline store of timestamped history for training and an online store of latest values for low-latency serving. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Feature view** — A group of features on one entity, from one source, computed and materialized together; the unit of scheduling and storage in a feature store. Also called a feature group. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Federated governance** — Shared rules (identifier formats, privacy classes, contract standards) agreed by domain representatives and the platform team, and enforced automatically by the platform so data from different domains can be joined. See: [Data Mesh](03-architecture-patterns/06-data-mesh.md)

**Feed inbox** — A per-member list of activity IDs waiting to be ranked, newest first, filled by fan-out on write and kept in a key-value store. It holds IDs, not scores, so a ranking change never rewrites it. See: [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)

**Feedback loop (recommendations)** — A model deciding what is shown, so training data contains only what it chose, so it keeps choosing the same things. Correcting for it needs logged positions, candidate samples and an exploration slice. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Freshness** — How old the newest data in a table or dashboard is compared with now, for example "no more than 15 minutes behind the source". One of the three common data SLAs, next to completeness and quality. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Freshness budget** — The end-to-end delay of a pipeline split into each hop's share (producer, stream job, store ingestion, cache refresh, browser push), so you can see where the time goes and which hop to change. See: [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)

**Full load** — Reading the whole source on every run and replacing your copy. Simple and handles deletes for free, but the work grows with the table. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)

**Functional requirement** — Something the system must produce or do, stated from the consumer's side, such as "marketing sees conversions per campaign". In a data system it is usually an output table, metric or feed. Compare with non-functional requirement. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

## G

**Geo-bucketing** — Mapping every location (latitude, longitude) to a fixed cell of a map grid, so "per area" becomes a key you can group and partition by. The cell size trades local detail against counts too small to be stable. See: [Design the Data Pipeline Behind Uber-Style Surge Pricing](05-breakdowns-core/10-surge-pricing.md)

**Geohash** — A public scheme that encodes a latitude-longitude rectangle as a short string, with longer strings for smaller rectangles. Cheap and stable, but cells change real size with latitude and neighbours sit at uneven distances. See: [Design the Data Pipeline Behind Uber-Style Surge Pricing](05-breakdowns-core/10-surge-pricing.md)

**Global type** — A company-wide identifier or unit (`customer_id`, `currency_code`, amounts in minor units) with a fixed format and an owning domain, referenced by contracts and checked at publish so products from different domains can be joined. See: [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)

**Grain** — What exactly one row in a table represents, such as "one order line" or "one user per day". Decide the grain first; every column and every join follows from it. See: [Data Model Design](01-the-framework/06-data-model-design.md)

## H

**H3** — An open-source grid that covers the Earth in hexagonal cells at 16 resolutions (resolution 8 averages about 0.74 km²), with a 64-bit ID per cell. Almost every cell has 6 edge-sharing neighbours at equal distance (12 per resolution are pentagons), and an approximate parent at the next coarser resolution. See: [Design the Data Pipeline Behind Uber-Style Surge Pricing](05-breakdowns-core/10-surge-pricing.md)

**Heartbeat (CDC)** — A small table in the source database that a job updates every few seconds and the CDC pipeline captures, so the replication slot keeps advancing on quiet databases and the row's arrival downstream measures end-to-end freshness. See: [Design CDC Replication from OLTP Databases into the Lake](05-breakdowns-core/05-cdc-replication.md)

**Hidden partitioning** — Iceberg partitioning by a transform of a real column (such as `days(event_ts)`), so users filter on the real column and still get pruning, with no derived partition column to remember. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**HMAC** — A short signature computed from a message and a secret key; only a holder of the key can produce a valid one, so any change to the message is detected. Used to make ad tokens tamper-proof. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Hot key** — A key that receives far more traffic than the others, so the one worker or partition that owns it becomes the bottleneck. Check each stage of a pipeline separately, since each is keyed differently; often the fix is to aggregate by an even key first and key by the skewed one only afterwards. See: [Design the Data Pipeline Behind Uber-Style Surge Pricing](05-breakdowns-core/10-surge-pricing.md)

**Hot partition** — A partition that receives far more traffic or data than the others, usually because the partition key is skewed (one huge customer, one viral item). It becomes the bottleneck for the whole system. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Hot set** — The few thousand keys currently getting the most traffic (for example, the most-viewed posts this second), detected by the stream job that counts them and pushed to every serving instance so their reads never reach the shared store. See: [Design Twitter/X-Style Engagement Analytics](06-breakdowns-advanced/04-social-media-analytics.md)

**Hot, warm and cold tiers** — Storing data at different price and speed points by age: the newest, most-read data on fast, expensive storage (a search index on SSD), older data on cheaper, slower storage (object storage, then an archive tier). Per-use retention requirements set the boundaries. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Hybrid fan-out** — Pushing activities from ordinary authors into inboxes while pulling the few very large accounts' recent activities at read time, because that pulled set is small enough to keep in memory. See: [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)

**HyperLogLog (HLL)** — A sketch that estimates the number of distinct values in a stream (unique visitors) from per-bucket maxima of hashed leading zeros. About 12 KB gives roughly 0.8% standard error at any scale, and two sketches merge into the sketch of their union, so daily counts combine over any range. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Hysteresis** — Using two thresholds instead of one (switch on above 100,000, back off only below 80,000) so a value hovering near the line does not flip a system between modes. See: [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)

## I

**Idempotent** — An operation that gives the same end result whether it runs once or many times. Idempotent pipeline steps can be retried or replayed safely. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Identity map** — A silver table that maps every identifier a person has across sources (app user ID, payment customer ID, CRM contact, email) to one internal surrogate key. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Impression** — One item shown to one user at one position on one page, at one moment. Impressions that were played or clicked become positive training examples; those ignored become negatives. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**In-sync replicas (ISR)** — The Kafka partition leader plus the followers that are caught up with it. A message counts as committed once all of them have it, and only an ISR member can become the new leader. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Incremental load** — Reading only the rows that are new or changed since the last run, usually with a watermark column. Cheaper per run than a full load, but it misses hard deletes unless handled. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)

**Incremental model** — A dbt model that keeps its table between runs and processes only new or changed rows, writing them in with an incremental strategy (append, merge, delete+insert, insert_overwrite or microbatch). Cheaper than a rebuild, but it can drift and miss hard deletes. See: [dbt](04-technology-deep-dives/04-dbt.md)

**Incremental snapshot** — A Debezium snapshot that reads a table in primary-key chunks while streaming continues, using watermark markers in the log to drop chunk rows that changed meanwhile. It lets you backfill one table without a lock or a full restart. See: [Debezium and CDC Tools](04-technology-deep-dives/09-debezium-and-cdc-tools.md)

**Inferred member** — A placeholder dimension row, with the natural key and "Unknown" attributes, inserted when a fact arrives before its dimension row; it is filled in when the real row arrives. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Ingest-time rollup** — A rollup the serving store maintains itself as rows arrive (Druid rollup at ingestion, a ClickHouse materialized view into a summing table), so no separate aggregation job is needed. Pinot's star-tree index is a related query accelerator built per segment, not a rollup table. See: [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)

**Interval join** — A stream-to-stream join where a record matches records from the other stream whose timestamps fall within a fixed range of its own (a click up to 30 minutes after its impression), so state is kept only for that range. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Invalid traffic (IVT)** — Ad impressions and clicks not made by a real person with real interest: bots, click farms, a competitor draining a budget. Advertisers are never charged for it, and some is only found days or weeks later. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Inverted index** — A map from every word to the list of documents that contain it, like the index at the back of a book. It lets a search engine find any word in seconds, at a storage cost close to the size of the raw text. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

## K

**Kafka Connect** — The framework that runs source and sink connectors for Kafka as a cluster of workers, configured through a REST API and tracking progress in Kafka topics. Debezium runs on it. See: [Debezium and CDC Tools](04-technology-deep-dives/09-debezium-and-cdc-tools.md)

**Kappa architecture** — One streaming pipeline over a replayable message log, with no batch layer; to fix history you replay the log through a new version of the job into a separate output and then switch consumers. Limited by log retention and replay cost. See: [Kappa Architecture](03-architecture-patterns/02-kappa-architecture.md)

**Keyed state** — Per-key memory a stream operator keeps (last value, list, map) after a `keyBy`, stored locally on the subtask that owns that key. See: [Flink](04-technology-deep-dives/08-flink.md)

**KRaft** — Kafka's built-in metadata layer, where a few controller nodes agree on cluster metadata using the Raft protocol. It replaced ZooKeeper, which Kafka 4.0 no longer supports. See: [Kafka](04-technology-deep-dives/02-kafka.md)

## L

**Label (ML)** — The outcome a model learns to predict (was this payment fraud?), attached to each training example with the entity keys and the time the prediction would have been made. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Label maturity** — The age after which a prediction's label is treated as settled, set from the measured label arrival curve (for fraud chargebacks, about 90 days). Training on younger rows mislabels recent positives as negatives. See: [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)

**Label window** — How long after a prediction or impression you wait before its label is final (such as "played within 24 hours"). Until it closes, a negative only means "not yet". It sets when a training partition can be built. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Lakehouse** — A data lake with warehouse-style tables, transactions and governance on top, provided by a table format and a catalog. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Lambda architecture** — Running a slow, exact batch layer and a fast, approximate speed layer over the same events, with a serving layer that merges them at a cutoff time. It buys correctness and freshness at the price of the same logic in two codebases. See: [Lambda Architecture](03-architecture-patterns/01-lambda-architecture.md)

**Landing zone** — A plain object-storage area where files are kept exactly as received, before any loading, so a failed parse can always be retried from the original. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Late-arriving dimension** — A fact that references a dimension row (for example a customer) which has not been loaded yet. Handle it with an inferred placeholder member or a quarantine-and-retry table, not a join that silently drops the fact. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Late data** — An event that arrives after the system has already moved past its event time, for example a mobile event uploaded two hours after it happened. You must decide whether to drop it, include it in a correction, or hold results back to wait for it. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Latency budget** — A request's time limit split into a share per step (store reads, candidate lookups, model), with independent steps run in parallel so the budget is the longest path, not the sum. The request-time counterpart of a freshness budget. See: [Design an E-Commerce Recommendation Engine That Stays Fresh](06-breakdowns-advanced/06-recommendation-engine.md)

**Ledger (append-only)** — A table where each row is one posting (+1 stream, or -1 for a reversal) tagged with the period it is reported in, and rows are never updated or deleted. A period's total is the sum of its rows, so corrections land in later periods and closed ones never change. See: [Design Spotify-Style Listening Analytics and Royalty Counts](06-breakdowns-advanced/01-music-streaming-analytics.md)

**Liquid clustering** — A Delta Lake layout feature (`CLUSTER BY`) that clusters data incrementally on chosen keys and lets you change the keys later without rewriting the table; it replaces partitioning and Z-order on new tables. Availability is version-dependent. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Local-global aggregation** — Pre-aggregating partial results (counts, sketches) on each upstream worker for a short interval before sending them to the worker that owns the key, so one hot key receives a few partials instead of every event. Works only for mergeable aggregates. Also called two-phase aggregation. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Log agent** — A small program on every host (Fluent Bit, Vector, the OpenTelemetry Collector) that tails log files and container output, adds metadata, buffers to local disk and ships lines on, so services never block on logging. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Log compaction (Kafka)** — A Kafka topic cleanup policy (`cleanup.policy=compact`) that keeps at least the latest message per key and eventually discards older ones, so the topic holds current state, not full history. A tombstone tells it to forget a key. Unrelated to compacting small table files. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Log sampling** — Keeping a representative fraction of repetitive log lines (say 1 in 20 INFO lines from one service) plus a count of what was skipped, while never sampling errors. It caps volume without hiding the shape of what happened. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Logs-to-metrics** — Counting log lines as they flow past (per service, level and minute) and storing the counts, so trends and alerts read a tiny table instead of scanning raw logs. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

## M

**Manifest** — In Iceberg, a metadata file listing data files with their partition values, row counts and per-column min/max bounds, so a query can skip files without opening them. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Masking policy** — A rule, enforced by the query engine, that rewrites a column's values at query time (a hash or `***`) for users who are not allowed to see them. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Materialization** — In dbt, how a model's query result is stored: as a view, a table, an incremental table, or a warehouse-maintained materialized view. Choosing it is a cost and freshness decision. See: [dbt](04-technology-deep-dives/04-dbt.md)

**Materialization (feature store)** — Computing feature values and loading them into the offline and online stores. Distinct from dbt's materialization, which is how a model's result is stored. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Medallion layers** — A way to organize a lakehouse into stages of increasing quality: bronze (raw as received), silver (cleaned and conformed) and gold (modeled for consumers). See: [Medallion Architecture](03-architecture-patterns/03-medallion-architecture.md)

**Merge-on-read** — Handling an update or delete by writing a small delete file beside the untouched data file, so writes are cheap and readers apply the deletes until compaction. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Mergeable aggregate** — A summary value that smaller buckets can be combined into exactly, without the raw data: min, max, sum, count, and sketches built to merge. An average or a percentile is not mergeable, so store its parts instead. See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

**Message log** — A durable, ordered, replayable queue of events (Kafka is the common one). Consumers read at their own pace and can re-read from an earlier point, which makes recovery and reprocessing possible. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Metadata catalog** — A searchable inventory of datasets with their schemas, owners and descriptions, often also storing the lineage graph. It is where people and tools look up what a table is and what depends on it. See: [Data Lineage](02-core-concepts/04-data-lineage.md)

**Micro-batch** — Processing a stream as a series of small batch jobs, one every few seconds or minutes, each picking up where the last stopped. Trades a latency floor for simplicity and easy recovery. See: [Micro-Batch vs Streaming](03-architecture-patterns/08-micro-batch-vs-streaming.md)

**Micro-partition** — Snowflake's automatic, immutable columnar file holding tens to hundreds of MB of rows, with min/max statistics per column that let queries skip it. See: [Snowflake: How a Modern Cloud Warehouse Works](04-technology-deep-dives/05-snowflake.md)

**MQTT** — A lightweight publish/subscribe protocol for constrained devices on unreliable networks: each device holds one long-lived connection to a broker. Its quality-of-service level 1 delivers at least once, so duplicates must be removed downstream. See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

## N

**Natural key** — The identifier the source system uses for a thing (`customer_id`). It stays the same across all of a dimension's SCD Type 2 versions. Compare surrogate key. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Negative sampling** — Keeping every positive training example but only a deterministic sample of negatives, each with a weight that undoes the sampling, so training sets stay a manageable size. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Noisy neighbour** — One tenant of a shared system using so much of it (slots, queries, I/O) that other tenants slow down. Fixed with per-tenant quotas, priorities and separating heavy work such as backfills. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)

**Non-functional requirement (NFR)** — A measurable quality of how well a system does its job: freshness, completeness, correctness, retention, query speed, cost. It only counts as a requirement once it has a number. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

## O

**Object storage** — Cheap, durable storage that holds files as objects in flat buckets and is accessed over an API (S3, GCS, Azure Blob). It is the usual base layer of a data lake. Objects are written whole and are not edited in place. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Observability** — Being able to answer "why is this unhealthy?" without guessing, using per-stage metrics, run history, lineage and logs. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Offline store** — The half of a feature store that keeps the full history of feature values with timestamps, in cheap storage such as lake tables, for building training sets. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Offset** — The sequential number of a message within a Kafka partition; its address in that log. A consumer's progress is the offset it has read up to. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**OLAP (online analytical processing)** — Workloads that scan and aggregate large amounts of data to answer questions, such as "revenue by region by month". Column-oriented warehouses are built for it. Compare with OLTP, which handles many small reads and writes to individual rows. See: [Snowflake: How a Modern Cloud Warehouse Works](04-technology-deep-dives/05-snowflake.md)

**OLTP (online transaction processing)** — The workload of an application's own database: many small reads and writes of individual rows as users act. It is why analytics data is copied out rather than queried in place. See: [Design CDC Replication from OLTP Databases into the Lake](05-breakdowns-core/05-cdc-replication.md)

**Online store** — The half of a feature store that keeps only the latest feature values per entity in a fast key-value store, read by models at inference time in milliseconds. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Optimistic concurrency control** — Letting writers work without locks and checking for conflicts only at commit time; a writer retries if the winning commit touched nothing it read, and fails if it did. Delta Lake uses it. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Orchestrator** — The tool (Airflow, Dagster, Prefect and similar) that runs a DAG of tasks, waits on dependencies, retries failures and records what ran. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Outbox pattern** — Writing a business event into an `outbox` table in the same database transaction as the data change, and letting CDC publish it. It avoids the dual write, where a crash between the database and the message queue loses or invents events. See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Output port** — The part of a data product that consumers may read (a table, view or topic), each with its own contract and major version. Everything else the domain builds stays private, so it can change without asking anyone. See: [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)

## P

**Partition** — A slice of a dataset or stream, chosen by a key or a range, that can be stored and processed independently. Partitions are how data systems spread work across machines and skip data they don't need. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Partition evolution** — Changing a table's partitioning as a metadata-only change: old files keep their old layout, new writes use the new one. An Iceberg feature. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Partition overwrite** — Making a run replace exactly one partition of the output (for example one date) instead of appending to it, so a rerun gives the same result. The default idempotent write for dated batch outputs. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

**Partition pruning** — The engine dropping every partition that cannot match a query's filter before reading any data. It only works when the filter is on the partition column itself, not a function of it. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Point-in-time join** — Attaching to each label row the newest feature value that was already available at the label's timestamp, bounded by a TTL. It prevents data leakage. Also called an as-of join. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Policy as code** — Governance rules written as versioned, testable code in a repository, run automatically by the platform at CI, publish and nightly scans, with each rule marked blocking or warning. See: [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)

**Pooled model** — A multi-tenant layout where all tenants share the same tables and compute, and a `tenant_id` column on every row says whose it is. Cheapest to run; isolation depends on row-level security and per-tenant quotas. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Posting period** — The accounting month a financial event is booked in: its own month if still open, otherwise the current open month, so a closed month never changes. See: [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)

**Pro-rata payout** — A royalty model where each month's money in a market is split by stream share, so a counting error on one track moves money away from every other rights holder in that market. See: [Design Spotify-Style Listening Analytics and Royalty Counts](06-breakdowns-advanced/01-music-streaming-analytics.md)

**Processing time** — The moment a system handles an event, as opposed to when it happened. Processing time is almost always later than event time, and the gap is what makes late data possible. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Projection** — A read-optimised table calculated from an event log by a process that subscribes to it. It is disposable: fix the logic, empty it and replay the log to rebuild. See: [Event Sourcing](03-architecture-patterns/05-event-sourcing.md)

**Pseudonymization** — Replacing identifying values with a key that only a separate, protected table can link back to a person, so deleting that link cuts the connection in every other table. The data may still count as personal data in law, so confirm with legal. See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

## Q

**Quarantine table** — A side table that holds records which failed validation, with the reason attached, so bad rows are visible and fixable instead of silently dropped. See: [Medallion Architecture](03-architecture-patterns/03-medallion-architecture.md)

## R

**Rate limit** — A cap a pull API puts on how many requests you may make per minute. It sets how fast you can read or backfill history from that source, whatever your own cluster could do. See: [Sources and Volume](01-the-framework/04-sources-and-volume.md)

**Raw layer** — The first stored copy of data, kept close to how it arrived (also called bronze). It lets you rerun cleaning logic after a bug without asking the source to resend. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Read replica** — A copy of a database kept in sync with the primary and used for reading, so heavy extracts or CDC do not slow the live application. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Read-your-writes** — A guarantee that after you write something, your own next read sees it, even if other readers see it later. A client that shows its own change locally often removes the need for the pipeline to provide it. See: [Design Twitter/X-Style Engagement Analytics](06-breakdowns-advanced/04-social-media-analytics.md)

**Real-time OLAP store** — A columnar database (ClickHouse, Druid, Pinot) that ingests a stream continuously and answers many small aggregate queries in tens to hundreds of milliseconds, used to serve user-facing dashboards. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Rebalance** — Redistributing a Kafka topic's partitions among the consumers in a group when one joins, leaves or is declared dead. With the classic protocol the whole group pauses during it. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Reconciliation** — Comparing your output with an independent source of truth (for example daily revenue against the payments provider's totals) and investigating any gap beyond a set tolerance. See: [Deep Dives](01-the-framework/08-deep-dives.md)

**Reconnect storm** — Many devices reconnecting at once after an outage, each with buffered backlog, overloading connection brokers and burying live data. Handled with jittered backoff, newest-first upload and a throttled, separate backlog path. See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

**Replay** — Re-reading stored events (from a message log offset or the raw layer) and processing them again with the same or fixed logic. Safe only when the writes are idempotent. See: [Backfill and Reprocessing](02-core-concepts/03-backfill-and-reprocessing.md)

**Replication slot** — A bookmark in a database such as Postgres that makes it keep its change log until a CDC reader confirms it has consumed it. A stopped reader makes the log pile up and can fill the source's disk, so alert on slot lag. See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Reprocessing** — Running already-stored data through new or corrected logic, whether the trigger is a bug, a new rule or a new column. A backfill is its date-range form. See: [Backfill and Reprocessing](02-core-concepts/03-backfill-and-reprocessing.md)

**Request coalescing** — When many identical requests arrive while a cached result is missing or expired, running the query once and giving every waiting caller that one result, so a cache expiry does not become a burst of identical queries. See: [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)

**REST catalog** — An open HTTP API for table catalogs that any engine can speak, giving engine-neutral access, server-side commits and centrally vended storage credentials. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Retention** — How long data is kept before it is deleted or moved to cheaper storage, including any rule to delete a person's data on request. Raw volume times retention is the storage bill. See: [Requirements Gathering](01-the-framework/03-requirements-gathering.md)

**Reverse ETL** — Reading a warehouse table or query result and writing it into operational tools (CRM, ad platform, email tool) through their APIs, usually as a scheduled diff-and-upsert sync. See: [Reverse ETL](03-architecture-patterns/09-reverse-etl.md)

**Rollup** — A pre-computed aggregate at a fixed grain (clicks per link per minute or per day), so a dashboard reads a few rows instead of scanning raw events. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Row filter** — A rule, enforced by the query engine, that adds a condition to every query on a table so each user sees only the rows they are allowed to (for example, their own region). See: [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)

**Row-level security (RLS)** — The query engine enforcing, row by row, who may read what, usually through a row filter; on a pooled multi-tenant table, one filter such as `tenant_id = current_tenant()`, with the tenant taken from the session rather than the query. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Runbook** — A short document tied to one alert: what it means, how to confirm it, likely causes, fixes and who to escalate to. It lets a tired on-call engineer act without reading code. See: [Monitoring and Alerting](02-core-concepts/06-monitoring-and-alerting.md)

## S

**Salting** — Adding a small random suffix to a hot key so its records spread over several partitions. Readers must then merge those slices, and ordering across them is lost. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Savepoint** — A manually triggered, portable snapshot of a Flink job's state, used for upgrades, rescaling and migrations. Unlike a checkpoint, you own it and it is not auto-deleted. See: [Flink](04-technology-deep-dives/08-flink.md)

**SCD (slowly changing dimension)** — A technique for keeping a dimension table correct when its attributes change over time, such as a customer moving city. Type 1 overwrites the old value; Type 2 adds a new row with validity dates so history is preserved. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Schema evolution** — Changing a dataset's schema (adding, dropping, renaming or retyping columns) while existing data and readers keep working. Adding an optional column is usually safe; renaming or retyping often breaks consumers. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Schema history topic** — A single-partition, infinite-retention Kafka topic where connectors such as Debezium MySQL record every DDL statement, so they can decode old log entries with the table structure of that moment. Losing it breaks the connector. See: [Debezium and CDC Tools](04-technology-deep-dives/09-debezium-and-cdc-tools.md)

**Schema registry** — A service that stores every version of each schema and rejects a new version that violates the configured compatibility mode. Producers and consumers look schemas up from it instead of hard-coding them. See: [Data Contracts](02-core-concepts/07-data-contracts.md)

**Self-serve data platform** — Shared tooling run by a platform team (storage, templates, catalog, access control, observability) that lets a domain team publish a data product without being an infrastructure expert. See: [Data Mesh](03-architecture-patterns/06-data-mesh.md)

**Sensor** — An orchestrator task whose only job is to wait for a condition, such as a file landing or a partition appearing, before downstream tasks run. See: [Airflow](04-technology-deep-dives/03-airflow.md)

**Series cardinality** — The number of distinct series (one metric of one device or entity) a time-series database tracks. Tag-indexed stores slow down as it grows, so tags must be stable identifiers, never per-trip or per-reading values. See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

**Serving layer** — The final tables or stores that consumers read, kept small and shaped for their questions so internal changes do not break them. See: [High-Level Architecture](01-the-framework/05-high-level-architecture.md)

**Sessionization** — Grouping one user's events into sessions, closing a session after a gap of inactivity (such as 30 minutes), so raw heartbeats or clicks become one row per visit or viewing. See: [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)

**Settlement (billing day)** — The batch run that makes one billing day final once its late events and fraud verdicts are in: it dedups, removes invalid traffic, applies the budget cap and posts charges. Afterwards the day's charges can only be credited, never raised. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Showback** — Reporting each team its own share of a shared platform's cost (for example GB of logs per service per day, priced), without billing them. It reduces volume because teams find their own waste. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Shuffle** — Redistributing data across a cluster so rows with the same key land together; it writes to disk and crosses the network, so it is the costliest step in a Spark job and the boundary between stages. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Siloed model** — A multi-tenant layout where a tenant gets its own tables, compute and sometimes encryption key. Strong isolation and simple deletion, but too costly to give every small tenant. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Sketch** — A small, fixed-size data structure that summarizes a large stream and answers one question approximately, such as HyperLogLog for distinct counts or Count-Min Sketch for frequencies, trading a known error for far less memory. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Skew** — Uneven load across partitions or workers, such as one city producing a third of the orders, so one slow task decides how long the whole job takes. Fix it with a different or compound key. See: [Partitioning](02-core-concepts/01-partitioning.md)

**SLA / SLO** — An SLO (service level objective) is a target you set for a measurable quality, such as "the daily table is ready by 07:00 on 99% of days". An SLA (service level agreement) is an SLO that has been promised to someone and usually has consequences if it is missed. See: [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)

**Small-files problem** — Too many tiny files in storage (often from frequent streaming writes), which makes listing and opening them dominate query time. The fix is to write bigger files or run compaction. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Snapshot (dbt)** — A dbt feature that builds an SCD Type 2 table by comparing a mutable source to its own previous state on every run. It records only the changes it observes, so run frequency sets the history's resolution. See: [dbt](04-technology-deep-dives/04-dbt.md)

**Snapshot generation** — A counter stamped on CDC events and rows that increases each time a table is re-snapshotted on a new log position, so data from the new snapshot always wins over leftovers whose log positions cannot be compared. See: [Design CDC Replication from OLTP Databases into the Lake](05-breakdowns-core/05-cdc-replication.md)

**Software-defined asset** — Dagster's unit: a decorated Python function that declares the one named dataset it produces and which assets it reads, so dependencies come from its inputs. See: [Orchestrator Comparison](04-technology-deep-dives/10-orchestrator-comparison.md)

**Source** — Any system a pipeline reads from but does not control: an operational database, an event stream, files, a pull API or a webhook. The type of source decides how the data can be read and how it can fail. See: [Sources and Volume](01-the-framework/04-sources-and-volume.md)

**Speed layer** — The streaming half of a Lambda design: it computes approximate results for the recent past, until the batch layer's exact result replaces them. See: [Lambda Architecture](03-architecture-patterns/01-lambda-architecture.md)

**Spill** — A task writing intermediate data to local disk because it ran out of execution memory. The job still finishes, slowly. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Spot capacity** — Spare cloud machines sold at a large discount (often 60 to 70 percent) that the cloud can reclaim at short notice. Suits retryable batch jobs, not state you cannot rebuild. See: [Cost Optimization](02-core-concepts/05-cost-optimization.md)

**Stage** — A run of Spark tasks that needs no data movement between them; a new stage starts at every shuffle. See: [Spark Internals](04-technology-deep-dives/01-spark-internals.md)

**Star schema** — A model with one central fact table surrounded by dimension tables, joined at query time. It keeps each descriptive value in one place. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**State backend** — The component that decides how a stream job stores its keyed state while running: in memory (heap), on local disk (RocksDB), or on remote storage with a local cache (disaggregated, Flink 2.x). See: [Flink](04-technology-deep-dives/08-flink.md)

**Storage tier** — A price and speed class of object storage: standard is instant and costs more, archive is much cheaper per TB but slow or fee-bearing to read. Lifecycle rules move data between tiers by age. See: [Cost Optimization](02-core-concepts/05-cost-optimization.md)

**Structured logging** — Writing each log line as a record with named fields (usually JSON) instead of free text, so it parses cheaply and reliably and sensitive fields can be dropped by name. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Surrogate key** — An ID the warehouse makes up for each row of a dimension (one per SCD Type 2 version), separate from the source's natural key. Facts store it to point at the version that was true at the time. See: [Data Model Design](01-the-framework/06-data-model-design.md)

## T

**Table format** — A metadata layer (Iceberg, Delta Lake, Hudi) that turns a pile of files in object storage into a table with transactions, schema changes and snapshots. See: [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)

**Task-centric orchestration** — An orchestrator model (Airflow's, Prefect's) where each node is a unit of work and you define the order between steps; the datasets they change are implicit unless you add metadata. See: [Orchestrator Comparison](04-technology-deep-dives/10-orchestrator-comparison.md)

**Tenant** — One customer (or team) of a shared platform whose data, access and costs must be kept separate from every other's. A platform serving many from shared infrastructure is multi-tenant. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Throughput** — How much data a component moves per unit of time, such as MB/s per Kafka partition or events/s per pipeline. Compare with latency, which is how long one operation takes. See: [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)

**Tiered storage** — A message-log feature that offloads older segments to object storage and reads them back on demand, so replay can reach further back than broker disks allow, at slower read speed. See: [Kappa Architecture](03-architecture-patterns/02-kappa-architecture.md)

**Time-series database (TSDB)** — A store built for timestamped measurements that keeps each series sorted by time, compresses it heavily, and answers "this series, this time range" in milliseconds (TimescaleDB, InfluxDB, or ClickHouse with time-ordered tables). See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

**Time travel** — Reading a table as of an earlier version or timestamp, possible while the old log entries and data files still exist (about 7 days by default in Delta Lake). See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Time-weighted average** — An average where each value counts for how long it held, not once per sample. Required for sensors that report only on change, such as a door that reports "opened" and "closed". See: [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)

**Token bucket** — A rate limiter: a counter that refills at the allowed rate up to a maximum burst, where each request takes a token and an empty bucket means throttle. Used for per-tenant ingest quotas. See: [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)

**Tombstone** — A message with a key and an empty value, which tells a compacted Kafka topic to eventually forget that key. CDC tools emit one after a delete event. See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Top-K** — The K items with the largest counts (the 100 most-clicked links in the last hour). Merging per-worker top-K lists is exact only when each key's full count lives on one worker. See: [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)

**Topic** — A named stream of messages in Kafka, split into partitions. Producers append to it and consumer groups read from it. See: [Kafka](04-technology-deep-dives/02-kafka.md)

**Trace ID** — An identifier attached to one user request as it passes through many services, so every log line that request produced can be pulled together. See: [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)

**Training-serving skew** — Any difference between the feature values a model saw in training and those it receives in production, from two implementations, leakage, different freshness or bugs. It fails silently. See: [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)

**Transaction log** — In Delta Lake, the ordered `_delta_log` of JSON commits (plus periodic checkpoints) listing which data files are added and removed; replaying it defines the table. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Trigger** — In Spark Structured Streaming, the setting that decides when the next micro-batch starts (as soon as possible, every N minutes, or once for everything available and then stop). See: [Micro-Batch vs Streaming](03-architecture-patterns/08-micro-batch-vs-streaming.md)

**Two-phase commit** — A sink protocol for exactly-once output: stage writes and pre-commit at the checkpoint, then commit only after the whole checkpoint succeeds, so output appears only at checkpoint time. See: [Flink](04-technology-deep-dives/08-flink.md)

## U

**Upsert (MERGE)** — Writing a row if its key is new and updating it if the key already exists. Applying the same batch twice changes nothing, which makes it an idempotent write for tables of entities. See: [Pipeline Design](01-the-framework/07-pipeline-design.md)

## V

**VACUUM** — The Delta Lake command that physically deletes data files no longer referenced by the current version and older than the retention period (7 days by default). It ends time travel to the deleted versions. See: [Delta Lake](04-technology-deep-dives/06-delta-lake.md)

**Velocity feature** — A count or sum over a recent time window per entity, such as payment attempts on this card in the last 10 minutes. The shortest windows may need computing inside the request so they include the previous event. See: [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)

**View-through attribution** — Crediting a sale to an ad the shopper saw on screen but did not click, within a short window (such as 1 day). Clicks normally take precedence over views. See: [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Virtual warehouse** — In Snowflake, a rented compute cluster that runs queries over shared storage; many can read the same tables without competing. See: [Snowflake: How a Modern Cloud Warehouse Works](04-technology-deep-dives/05-snowflake.md)

## W

**Watermark** — A stream processor's running estimate of how far event time has progressed, which says "I don't expect events older than this anymore". It decides when a time window can be closed and its result emitted. Not the same as an ingestion "watermark column", which is the last value a batch load has already copied. See: [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)

**Watermark column** — A column that only moves forward (usually `updated_at`) whose largest loaded value is stored, so the next incremental run asks only for rows beyond it. Misses hard deletes and late commits unless you add an overlap window. See: [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)

**Wide table (OBT)** — A table that joins facts and dimensions ahead of time so every row carries all the columns a consumer needs and queries need no joins. Also called one big table. See: [Data Model Design](01-the-framework/06-data-model-design.md)

**Windowed dedup** — Streaming deduplication that remembers each key for a fixed period and then forgets it. State stays bounded, but duplicates arriving after the window pass through. See: [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)

**Workflow service (cloud-native)** — A managed state-machine or pipeline service from a cloud (for example Step Functions, Cloud Workflows, Data Factory) that calls other services with nothing to host. Strong for glue between services, weak at dated backfills and lineage. See: [Orchestrator Comparison](04-technology-deep-dives/10-orchestrator-comparison.md)

**Write-ahead log (WAL)** — The file where a database records every change before applying it, so it can recover after a crash and feed replicas. Log-based CDC reads it (Postgres: WAL, MySQL: binlog). See: [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)

**Write-audit-publish (WAP)** — Writing new data where consumers cannot see it (a staging location, a branch or a staged snapshot), running quality checks on it there, and publishing it in one atomic step only if they pass. See: [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)

**Write-if-newer** — A write rule for derived values: each value carries a timestamp or version, and the store ignores a write older than what it already holds, so replays and late retries cannot move a value backwards. See: [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)

## Z

**Z-order** — A layout that interleaves the sort order of several columns so rows close in all of them sit near each other, giving moderate data skipping on any of those columns. See: [Partitioning](02-core-concepts/01-partitioning.md)

**Zero-copy clone** — A new table that shares the original's data files until either side changes, so a full-size copy for testing costs almost nothing to create. Offered by several warehouses and table formats. See: [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)
