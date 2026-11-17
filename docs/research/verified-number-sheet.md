# Verified number sheet: research for issue #2

Question (issue #2): which real, published limits, throughputs, latencies and prices should
`course/02-core-concepts/10-key-de-numbers.md` hold as the course's single verified number
reference, and what is each one's current rounded value?

Checked: 2026-11-17, against vendor docs, price lists and project docs. Prices are US list
prices (AWS us-east-1, GCP us-central1 or US multi-region) unless stated. The source URLs live
only in this file; the course itself carries no citations.

How to read the tables:

- **Published** is what the owning source states, close to verbatim.
- **Course value** is the rounded figure to memorize (as of 2026).
- **Status** says whether the current lesson figure is **OK**, **Adjust** (right ballpark, wording
  or range should change), **Wrong** (contradicts the source) or **Rule of thumb** (no vendor
  publishes this number, so keep it but call it an assumption).

---

## 1. Object storage

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| S3 Standard storage | $0.023/GB-mo first 50 TB, $0.022 next 450 TB, $0.021 over 500 TB | ~$23 per TB-month | Storage is the cheap line; keep raw data | 10-key-de-numbers, 05-cost-optimization, 04-sources-and-volume, 03-backfill, 02-kappa, 03-medallion, most breakdowns | OK | AWS Price List API, AmazonS3 us-east-1: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json |
| GCS Standard storage (regional) | $0.000027397/GiB-hour, about $0.020/GiB-mo (us-central1) | ~$20 per TB-month | Same as above; GCS and S3 are interchangeable at this precision | same | OK (the "$20 to 25" range covers both) | https://cloud.google.com/storage/pricing |
| S3 Standard-IA | $0.0125/GB-mo | ~$12.50 per TB-month | Middle tier for rarely read data | 05-cost-optimization | Missing (add) | AWS Price List API, S3 (above) |
| S3 Glacier Instant Retrieval | $0.004/GB-mo | ~$4 per TB-month | Archive that still reads in ms | 05-cost-optimization, 01-log-aggregation | OK (inside "$1 to 5") | AWS Price List API, S3 |
| S3 Glacier Flexible Retrieval | $0.0036/GB-mo | ~$3.60 per TB-month | Archive, retrieval in minutes to hours | same | OK | AWS Price List API, S3 |
| S3 Glacier Deep Archive | about $0.00099/GB-mo; standard retrieval $0.02/GB, bulk $0.0025/GB | ~$1 per TB-month, retrieval in hours plus a per-GB fee | Compliance retention | same | OK | AWS Price List API, S3 (retrieval rows); storage rate from https://aws.amazon.com/s3/pricing/ |
| GCS Archive (regional) | $0.000001644/GiB-hour, about $0.0012/GiB-mo | ~$1.20 per TB-month | same | same | OK | https://cloud.google.com/storage/pricing |
| S3 write requests (PUT, COPY, POST, LIST) | $0.005 per 1,000 | **$5 per million writes** | Small files cost money per file, not per byte | 10-key-de-numbers, 01-partitioning, 05-cost-optimization | OK | AWS Price List API, S3 |
| S3 read requests (GET and others) | $0.0004 per 1,000 ($0.004 per 10,000) | **$0.40 per million reads** | same | same | OK | AWS Price List API, S3 |
| GCS Class A / Class B (regional Standard, flat namespace) | $0.005 / $0.0004 per 1,000 | Same as S3: $5 / $0.40 per million | same | same | OK | https://cloud.google.com/storage/pricing |
| S3 request rate per prefix | "at least 3,500 PUT/COPY/POST/DELETE or 5,500 GET/HEAD requests per second per partitioned prefix"; scales gradually, 503 Slow Down while it scales | **3,500 writes/s, 5,500 reads/s per prefix**; more prefixes multiply it | Spread hot write paths over prefixes; expect 503s on sudden ramps | 10-key-de-numbers | OK | https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html |
| GCS initial request rate per bucket | about 1,000 writes/s and 5,000 reads/s; ramp no faster than doubling every 20 minutes | ~1,000 writes/s, 5,000 reads/s per bucket to start | Same small-files and ramp-up argument on GCP | 10-key-de-numbers | Missing (add as the GCS twin) | https://docs.cloud.google.com/storage/docs/request-rate |
| S3 first-byte latency | "consistent small object latencies (and first-byte-out latencies for larger objects) of roughly 100–200 milliseconds"; for requests under 512 KB "median latencies are often in the tens of milliseconds"; retry a small GET/PUT after 2 s | **Tens of ms median, 100 to 200 ms at the tail** | Every small read pays a fixed floor; 100 serial reads is seconds | 10-key-de-numbers, 01-partitioning, 05-cost-optimization, 07-iceberg, 06-medallion-data-lake | Adjust: course says "10 to 100 ms (tail to ~200 ms)"; say "tens of ms typical, 100 to 200 ms tail" | https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html and https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance-design-patterns.html |
| S3 aggregate throughput | single instance can saturate its NIC, "up to 100 Gb/s on a single instance"; aggregate "multiple terabits per second" | Per instance: limited by its network card; cluster: Tb/s | Object storage is slow per request but nearly unlimited in aggregate | 10-key-de-numbers | OK | https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html |
| Object storage, one connection | Not published by AWS or Google | 50 to 100 MB/s | Restore and replay time per reader | 10-key-de-numbers, 08-flink, 05-event-sourcing | Rule of thumb (no vendor figure) | none |
| S3 Express One Zone | single-digit ms; "up to 10x faster" and request costs "80 percent lower" than Standard; storage $0.11/GB-mo; PUT $0.00113 per 1,000, GET $0.00003 per 1,000 | **Single-digit ms, ~$110 per TB-month (about 5x Standard)** | Hot, small, latency-sensitive reads only | 10-key-de-numbers | OK ("several times more per GB" is right; add ~5x) | https://docs.aws.amazon.com/AmazonS3/latest/userguide/directory-bucket-high-performance.html; prices from AWS Price List API, S3 |

## 2. Network, block storage and compute

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Internet egress (EC2/S3 to internet) | $0.09/GB first 10 TB/mo, $0.085 next 40 TB, $0.07 next 100 TB, $0.05 over 150 TB | **$0.05 to 0.09 per GB**, ~$90 per TB for small volumes | Don't copy big data out of the cloud | 10-key-de-numbers, 05-cost-optimization, 05-snowflake | OK | AWS Price List API, AWSDataTransfer us-east-1: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-1/index.json |
| Cross-AZ transfer | $0.010/GB "in/out/between EC2 AZs" (charged each direction) | **$0.01 per GB each way** | RF 3 across zones pays on every replicated byte | 10-key-de-numbers, 05-cost-optimization, 02-kafka | OK | AWS Price List API, AWSDataTransfer |
| AZ distance and latency | AZs "all within 100 km (60 miles) of each other", "low-latency networking", fast enough for synchronous replication; no ms figure published | ~1 to 2 ms round trip across AZs | Synchronous replication across zones is affordable; across regions it isn't | 10-key-de-numbers, 02-kafka | Rule of thumb for the ms value (distance is published) | https://aws.amazon.com/about-aws/global-infrastructure/regions_az/ |
| Same-AZ and cross-region RTT | Not published as a vendor figure | 0.1 to 0.5 ms same AZ; 20 to 200 ms cross region | Fan-out and geo-replication budgets | 10-key-de-numbers, 08-feature-store | Rule of thumb | none |
| EBS gp3 | 3,000 IOPS and 125 MiB/s baseline included; up to 80,000 IOPS and **2,000 MiB/s** provisioned; 1 GiB to 64 TiB; "single-digit millisecond latency"; price $0.08/GB-mo, $0.005 per extra IOPS-mo, $0.06 per extra MB/s-mo | **125 MB/s default, up to 2 GB/s; ~$80 per TB-month; single-digit ms** | Network disk throughput is provisioned and easy to bottleneck | 10-key-de-numbers, 01-log-aggregation | OK (course says "125 MB/s to 1 to 2 GB/s"; the max is now exactly 2 GB/s) | https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html and https://aws.amazon.com/ebs/pricing/ |
| Instance network bandwidth (m7i) | m7i.large 0.781 Gbps baseline / 12.5 burst; m7i.2xlarge 3.125 / 12.5; m7i.4xlarge 6.25 / 12.5; m7i.8xlarge 12.5; m7i.16xlarge 25 Gbps | An 8 vCPU VM sustains ~3 Gbit/s (~400 MB/s) and only bursts to 12.5 | Caps per-broker and per-executor throughput; small instances only burst | 10-key-de-numbers, 02-kafka | Adjust: course says "mid-size instances: 10 to 25 Gbit/s"; mid-size baseline is 3 to 6 Gbit/s, 10 to 25 is 8xlarge and up | https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html |
| General-purpose VM price | m7i.2xlarge (8 vCPU, 32 GiB) $0.4032/hr on-demand us-east-1; Graviton m7g.2xlarge about $0.33/hr | **~$0.40/hr for 8 vCPU / 32 GB, ~$0.05 per vCPU-hour** | Batch compute is cheap; idle always-on compute is not | 10-key-de-numbers, 05-cost-optimization, 03-backfill, 08-micro-batch | OK | AWS Price List API, AmazonEC2 (price confirmed by multiple pricing mirrors); https://aws.amazon.com/ec2/pricing/on-demand/ |
| Spot discount and notice | "up to 90%" off On-Demand; interruption notice "two minutes" before stop/terminate | **Up to 90% off (60 to 70% typical), 2-minute warning** | Spot suits retryable batch, not stateful streaming | 10-key-de-numbers, 05-cost-optimization | Adjust: add the 2-minute notice; "60 to 70 percent" is a typical outcome, not the published figure | https://aws.amazon.com/ec2/spot/ and https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html |
| Memory, NVMe, HDD throughput and latency | No single vendor figure | Keep 10-key-de-numbers ranges | Where state lives | 10-key-de-numbers, 08-flink | Rule of thumb | none |

## 3. Kafka

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Per-partition producer throughput | Confluent: partitions = max(t/p, t/c) where p is measured per-partition producer throughput; their worked example puts one partition at "10s of MB/sec" (50 MB/s produce, 25 MB/s consume) | **Plan 10 MB/s per partition; tens of MB/s is achievable** | Partition count = max(peak MB/s / 10, consumer parallelism) | 10-key-de-numbers, 02-kafka, 01-partitioning, 04-sources-and-volume, 08-flink, all breakdowns | OK (10 MB/s is a deliberately conservative planning number; say so) | https://docs.confluent.io/kafka/operations-tools/partition-determination.html |
| Managed Kafka throughput unit | Confluent Cloud per eCKU: Basic 5 MB/s in, Standard 25 MB/s in, Enterprise 60 MB/s in; Dedicated per CKU 60 MB/s in / 180 MB/s out, 4,500 partitions | **~60 MB/s ingress per managed capacity unit** | Converts MB/s into a managed-Kafka bill | 02-kafka, 10-key-de-numbers ("Managed Kafka" row) | Missing (add) | https://docs.confluent.io/cloud/current/clusters/cluster-types.html |
| Managed cluster ceilings | Confluent Cloud max per cluster: Basic/Standard 250 MB/s in, Enterprise 1,920 MB/s, Dedicated 9,120 MB/s; partitions 1,500 / 2,500 / 96,000 / 100,000; max message 8 MB (Basic/Standard), 20 MB (Enterprise/Dedicated) | Hundreds of MB/s to ~9 GB/s per managed cluster | When to split clusters | 01-log-aggregation, 05-multi-tenant-platform | Missing (add) | same |
| Per-broker ingress | Confluent benchmark: Kafka held 200 MB/s at p99 ~5 ms, peak 605 MB/s, on a testbed with a 300 MB/s disk limit (older hardware, fsync off) | **100 to 300 MB/s per broker** | Brokers = peak ingress x RF / per-broker rate | 10-key-de-numbers, 02-kafka, 03-backfill, 02-kappa | OK (vendor benchmark, not a guarantee; network baseline in section 2 is the usual cap) | https://www.confluent.io/blog/kafka-fastest-messaging-system/ |
| Partitions per broker | MSK recommends (leaders plus followers) 300 for t3.small; **1,000** for m5/m7g large and xlarge; **2,000** for 2xlarge; **4,000** for 4xlarge and up; keep broker CPU under 60% | **~1,000 replicas per small broker, up to ~4,000 on large brokers** | Partition-heavy designs (one topic per table) need more or bigger brokers | 10-key-de-numbers, 02-kafka, 05-cdc-replication | Adjust: course says "~2,000 to 4,000 comfortable"; that is only true of 2xlarge and larger | https://docs.aws.amazon.com/msk/latest/developerguide/bestpractices.html |
| Produce latency, acks=all | Confluent benchmark p99 ~5 ms at 200 MB/s | **p99 ~5 ms on a tuned cluster, 5 to 50 ms in practice** | Floor for streaming end-to-end latency | 10-key-de-numbers, 02-kafka, 08-micro-batch, 03-fraud-detection, 06-recommendation-engine | OK (lower bound is published; upper bound is a rule of thumb) | https://www.confluent.io/blog/kafka-fastest-messaging-system/ |
| Max message size | broker `message.max.bytes` 1048588; producer `max.request.size` 1048576 | **~1 MB** | Large payloads go to object storage plus a pointer | 10-key-de-numbers | OK | https://kafka.apache.org/41/configuration/broker-configs/ and https://kafka.apache.org/41/configuration/producer-configs/ |
| Producer defaults (4.x) | `linger.ms` 5, `batch.size` 16384, `acks` all, `enable.idempotence` true, `compression.type` none | linger 5 ms, 16 KB batches, acks=all, idempotent by default, no compression | Why batching and compression must be set explicitly | 02-kafka | OK (lesson already says 5 ms from 4.0) | https://kafka.apache.org/41/configuration/producer-configs/ |
| Broker defaults | `log.retention.hours` 168, `log.segment.bytes` 1 GiB, `num.partitions` 1, `default.replication.factor` 1 | **7-day default retention**, 1 GB segments | Retention is a cost choice; RF must be set to 3 explicitly | 02-kafka, 10-key-de-numbers | Missing (add the 7-day default) | https://kafka.apache.org/41/configuration/broker-configs/ |
| KRaft only | Kafka 4.0 is "the first major release to operate entirely without Apache ZooKeeper"; 3.9 is the last bridge release | ZooKeeper gone since 4.0 | No separate coordination cluster to size | 10-key-de-numbers, 02-kafka | OK | https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/ and https://kafka.apache.org/41/operations/kraft/ |
| MSK prices | m7g.large $0.204, m7g.xlarge $0.408, m7g.2xlarge $0.816 per broker-hour; broker storage $0.10/GB-mo; tiered storage $0.06/GB-mo | **3 small brokers ~$450/month before storage; broker disk ~$100 per TB-month** | Long retention on broker disk costs ~4x object storage | 10-key-de-numbers, 02-kappa, 01-log-aggregation | Adjust: "Managed Kafka, small: hundreds to low thousands" is right; add the ~$100/TB-month disk figure | AWS Price List API, AmazonMSK us-east-1: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonMSK/current/us-east-1/index.json |
| Compression ratios (lz4 3x, zstd 4 to 6x on JSON) | Not published by Kafka or Confluent as fixed ratios | Keep as stated | Broker disk and network | 10-key-de-numbers | Rule of thumb | none |

## 4. Spark

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Input split size | `spark.sql.files.maxPartitionBytes` default 128 MB | **128 MB per input task** | Task count = input / 128 MB | 10-key-de-numbers, 01-spark-internals | OK ("128 to 256 MB" is fine; 128 is the default) | https://spark.apache.org/docs/latest/sql-performance-tuning.html (Spark 4.3 docs) |
| Shuffle partitions | `spark.sql.shuffle.partitions` default 200 | 200 by default, too few for TB jobs | Set high and let AQE coalesce | 10-key-de-numbers, 01-spark-internals | OK | same |
| AQE | on by default since Spark 3.2.0; `advisoryPartitionSizeInBytes` 64 MB; `coalescePartitions.minPartitionSize` 1 MB | AQE on; it targets **64 MB** post-shuffle partitions | Post-shuffle partition size | 10-key-de-numbers, 01-spark-internals | Adjust: course says "100 to 200 MB each after the shuffle"; the shipped AQE target is 64 MB. Either cite 64 MB as the default or say "raise the advisory size to 128 to 256 MB" | same |
| Skew detection | partition is skewed if > 5x median **and** > 256 MB | 5x median and over 256 MB | When AQE splits a skewed join partition | 01-spark-internals, 01-partitioning | Missing (add) | same |
| Broadcast join threshold | `spark.sql.autoBroadcastJoinThreshold` 10 MB | **10 MB** auto-broadcast | When a join avoids a shuffle | 01-spark-internals, GLOSSARY | Missing (add) | same |
| Tasks per core | "we recommend 2-3 tasks per CPU core in your cluster"; tasks as short as 200 ms are fine | **2 to 3 tasks per core** | Total partitions for a stage | 10-key-de-numbers, 01-spark-internals | Adjust: course says "2 to 4 times"; Spark docs say 2 to 3 | https://spark.apache.org/docs/latest/tuning.html |
| Executor memory overhead | `memoryOverheadFactor` 0.10 (0.40 for non-JVM on Kubernetes), minimum 384 MiB; `spark.memory.fraction` 0.6 of (heap - 300 MiB) | +10% (min 384 MB) off-heap per executor | Container size = heap x 1.1 | 10-key-de-numbers, 01-spark-internals | Missing (add) | https://spark.apache.org/docs/latest/configuration.html |
| Cores per executor (4 to 5) and memory per core (4 to 8 GB) | Not in Spark docs; Spark defaults to 1 core per executor on YARN | Keep as a rule of thumb | Executor shape | 10-key-de-numbers, 01-spark-internals | Rule of thumb (well known, not vendor-published) | none |
| Throughput per core (10 to 50 MB/s) | Not published | Keep, labelled a guess | Cluster size from a deadline | 10-key-de-numbers, 01-spark-internals, 03-backfill, 08-micro-batch, many breakdowns | Rule of thumb | none |

## 5. Files and table formats

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Parquet row group | "We recommend large row groups (512MB - 1GB)"; page size 8 KB | Row groups 512 MB to 1 GB | Files should be at least one large row group | 10-key-de-numbers, 01-partitioning | Missing (add as the source of "big files") | https://parquet.apache.org/docs/file-format/configurations/ |
| Iceberg target file size | `write.target-file-size-bytes` 512 MB; `write.parquet.row-group-size-bytes` 128 MB; `read.split.target-size` 128 MB | **512 MB files** | Compaction target | 07-iceberg, 10-key-de-numbers | OK | https://iceberg.apache.org/docs/latest/configuration/ |
| Delta OPTIMIZE output | `spark.databricks.delta.optimize.maxFileSize` default 1 GB; OSS auto compaction targets 128 MB | **~1 GB** after OPTIMIZE | Compaction target | 06-delta-lake | OK | https://delta.io/blog/2023-01-25-delta-lake-small-file-compaction-optimize/ and https://docs.delta.io/latest/optimizations-oss.html |
| Databricks autotuned file size | 256 MB below 2.56 TB table size, growing linearly to 1 GB at 10 TB, 1 GB above | **256 MB to 1 GB, scaling with table size** | Small tables want smaller files | 06-delta-lake, 10-key-de-numbers | Missing (add) | https://docs.databricks.com/aws/en/delta/tune-file-size |
| Good file size range | Follows from the rows above | **128 MB to 1 GB per file** | Small-files problem threshold | 10-key-de-numbers, 04-sources-and-volume, 06-delta-lake | OK | rows above |
| JSON to Parquet ratio (~5x) | Not published | Keep, labelled a rule of thumb | Lake storage sizing | most lessons | Rule of thumb | none |

## 6. Cloud warehouses and scan-priced engines

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Snowflake warehouse sizes (Gen1 standard) | XS 1, S 2, M 4, L 8, XL 16, 2XL 32, 3XL 64, 4XL 128, 5XL 256, 6XL 512 credits/hr | **XS = 1 credit/hr, doubling per size** | Bigger is the same cost if it finishes proportionally faster | 05-snowflake, 10-key-de-numbers, 05-cost-optimization | OK | https://docs.snowflake.com/en/user-guide/warehouses-overview |
| Snowflake billing granularity | "per-second billing (with a 60-second minimum each time the warehouse starts)" | Per second, 60 s minimum per resume | Very short auto-suspend can cost more than it saves | 05-snowflake | Missing (add) | same |
| Snowflake credit price | On-demand, AWS US East: Standard $2, Enterprise $3, Business Critical $4 (Service Consumption Table, effective 2025-05-13) | **$2 to 4 per credit, ~$3 typical** | Warehouse $/hour | 05-snowflake, 10-key-de-numbers, 05-cost-optimization, 03-backfill | OK | https://www.snowflake.com/content/dam/snowflake-site/legal/legal-files/CreditConsumptionTable.pdf (Snowflake docs use "$2/credit" in examples: https://docs.snowflake.com/en/user-guide/cost-understanding-overall) |
| Snowflake storage | Flat rate per TB of compressed data; varies by capacity vs on-demand and region; docs example uses $23/TB; consumption table US East on-demand rate about $23/TB-month (table layout made this hard to confirm) | **~$23 per TB-month compressed (capacity); on-demand can be higher** | Warehouse storage is near object storage | 05-snowflake, 10-key-de-numbers | OK ("$20 to 40" covers it) | https://docs.snowflake.com/en/user-guide/cost-understanding-data-storage and the consumption table above |
| Snowflake cloud services | charged only if daily cloud services usage exceeds 10% of daily warehouse usage | First 10% free | Metadata-heavy workloads can add cost | 05-snowflake | Missing (optional) | https://docs.snowflake.com/en/user-guide/cost-understanding-overall |
| BigQuery on-demand | **$6.25 per TiB** scanned; first 1 TiB/month free; minimum 10 MB per table referenced and per query | **$6.25 per TiB scanned** | Partition pruning and column selection pay back directly | 10-key-de-numbers, 01-partitioning, 05-cost-optimization, 08-deep-dives, 05-snowflake, 09-data-quality-monitoring | OK | https://cloud.google.com/bigquery/pricing |
| BigQuery capacity (Editions) | Enterprise $0.06 per slot-hour pay-as-you-go ($0.054 1-yr, $0.048 3-yr); Standard about $0.04, Enterprise Plus about $0.10 | ~$0.04 to 0.10 per slot-hour | When steady load should move off on-demand | 05-snowflake | Missing (add Enterprise $0.06) | same |
| BigQuery storage | active logical $0.000031507/GiB-hour (~$0.023/GiB-mo); long-term (90 days unmodified) ~$0.016/GiB-mo, us-central1 | ~$23 per TB-month active, ~$16 long-term | Old partitions get cheaper on their own | 05-snowflake, 05-cost-optimization | OK | same |
| BigQuery partition limits | 10,000 partitions per table; 4,000 partitions modified per job | **10,000 partitions per table** | Daily partitions last ~27 years; hourly partitions ~14 months | 01-partitioning | Missing (add) | https://docs.cloud.google.com/bigquery/quotas |
| Athena | $5 per TB scanned (example "3 * $5/TB"); 10 MB minimum per query; provisioned capacity $0.30 per DPU-hour | **$5 per TB scanned** | Same pruning argument as BigQuery | 10-key-de-numbers, 01-partitioning, 05-cost-optimization | OK | https://aws.amazon.com/athena/pricing/ |

## 7. Flink

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Default state backend | HashMapStateBackend if nothing configured; "state size is limited by available memory within the cluster" | Heap by default, capped by memory | Big state needs RocksDB | 08-flink | OK | https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/state_backends/ (Flink 2.3 docs) |
| RocksDB state limits | "maximum supported size per key and per value is 2^31 bytes each"; total state "only limited by the amount of disk space available" | **2 GB per key and per value; total capped by local disk** | Don't keep unbounded lists under one key | 08-flink | Missing (add the 2 GB per-value cap) | same |
| ForSt (disaggregated) | marked experimental; state files on remote storage, "the amount of state that you can keep is unlimited"; same 2^31-byte per-key/value cap | Remote state, no local-disk cap; experimental | Very large state or fast rescaling | 08-flink | Adjust: lesson says "Newer; part of Flink 2.x"; add "experimental" | same |
| Incremental checkpoints and local recovery | incremental checkpoints "should be one of the first considerations"; local recovery "deactivated by default"; RocksDB managed memory fraction default 0.4 | Turn on incremental checkpoints; local recovery is opt-in | Checkpoint and recovery time for big state | 08-flink | OK | https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/large_state_tuning/ |
| Checkpoint interval "1 minute is a common default" | Flink has no default interval (checkpointing is off unless enabled); docs only advise a minimum pause between checkpoints | 10 s to 5 min, chosen by you | Exactly-once output latency floor | 08-flink | Adjust: "common choice", not "default" | same |
| Events/s per core with RocksDB (5,000 to 20,000), state per TaskManager (tens to hundreds of GB) | Not published by Flink | Keep, labelled a rule of thumb | Parallelism and TaskManager sizing | 08-flink | Rule of thumb (invented-looking precision; soften) | none |

## 8. CDC and replication lag

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Postgres slot WAL retention | `max_slot_wal_keep_size` default -1: "replication slots may retain an unlimited amount of WAL files"; `max_replication_slots` default 10 | **Unlimited by default**: a dead slot fills the disk | Alert on slot lag, set a cap | 09-debezium, 04-cdc-patterns, 05-cdc-replication | OK | https://www.postgresql.org/docs/current/runtime-config-replication.html (PostgreSQL 18) |
| Debezium defaults | Debezium 3.7: `heartbeat.interval.ms` 0 (no heartbeats), `max.batch.size` 2048, `max.queue.size` 8192, `snapshot.fetch.size` 10240 rows, `poll.interval.ms` 500 | Heartbeats off by default; 0.5 s poll | Quiet tables hold WAL unless heartbeats are on; poll interval sets a small lag floor | 09-debezium | OK (lesson already says set heartbeats) | https://debezium.io/documentation/reference/stable/connectors/postgresql.html |
| In-cluster replica lag | Aurora: lag "usually much less than 100 milliseconds", rising under heavy writes | **Under 100 ms** for managed physical replicas | Read replicas are near-real-time; CDC to a lake adds seconds | 04-cdc-patterns, 05-cdc-replication | Missing (add as the published lag reference) | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Replication.html |
| Log-based CDC end-to-end lag | Debezium publishes the `MilliSecondsBehindSource` metric but no typical value | Seconds when healthy | Freshness SLA for CDC pipelines | 04-cdc-patterns, 05-cdc-replication | Rule of thumb |
| Snapshot rate (~20 MB/s per connection) | Not published | Keep, labelled an assumption | Initial load time | 09-debezium, 04-cdc-patterns, 05-cdc-replication, 02-ingestion-patterns | Rule of thumb |

## 9. Search index storage

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Shard size and count | "Aim for shard sizes between 10GB and 50GB"; under 200 million docs per shard; at most 1,000 non-frozen shards per node by default | **10 to 50 GB per shard, ≤1,000 shards per node** | Shard count for a log index | 01-log-aggregation | Missing (add) | https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/size-shards |
| Index size vs raw | Elastic publishes no raw-to-index ratio. logsdb index mode cuts log storage "by up to 60%" (docs) / 65% (launch) vs a standard index, with a 10 to 20% indexing cost | Index ~1x raw per copy for a standard index (rule of thumb); one replica doubles it; logsdb roughly halves it | Hot search tier is the expensive tier | 01-log-aggregation | Rule of thumb: the course's "~2x raw" is defensible only as "1 primary + 1 replica at about 1x each"; say that | https://www.elastic.co/docs/manage-data/data-store/data-streams/logs-data-stream and https://ir.elastic.co/News--Events/news/news-details/2024/Elastic-Announces-Elasticsearch-Logsdb-Index-Mode-to-Reduce-Log-Data-Storage-Footprint-by-Up-to-65/default.aspx |

## 10. Serving stores (latency floors used by breakdowns)

| Figure | Published | Course value | Decision it drives | Lessons | Status | Source |
|---|---|---|---|---|---|---|
| Key-value store reads | DynamoDB markets "single-digit millisecond performance at any scale" | **Single-digit ms** per read | Online feature and counter stores meet 10 ms p99 budgets; warehouses do not | 08-feature-store, 03-fraud-detection, 04-social-media-analytics, 09-reverse-etl | Missing (add one serving-store row) | https://aws.amazon.com/dynamodb/ |
| Block volume latency | gp3 "single-digit millisecond"; io2 Block Express "under 500 microseconds" | ms for network disks, sub-ms for premium | Where stream state should not live | 10-key-de-numbers, 08-flink | OK | https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html |

---

## Current lesson figures that are wrong, imprecise or invented

Wrong or out of date (contradict the source):

1. **Kafka partitions per broker** (`10-key-de-numbers`, `02-kafka`): "~2,000 to 4,000 comfortable". MSK's published guidance counts leader and follower replicas: about 1,000 on large/xlarge brokers, 2,000 on 2xlarge, 4,000 on 4xlarge and up. Use "about 1,000 replicas per small broker, up to 4,000 on large ones".
2. **CDC replication breakdown** (`05-cdc-replication`, line ~99): "10,500 replicas ... at 2,000 to 4,000 replicas per broker that's 3 to 6 brokers". On the brokers that 60 MB/s actually needs (small ones), the published figure is about 1,000 replicas per broker, so 10,500 replicas need about 10 small brokers, or 3 large ones. The conclusion "partition count, not throughput, sizes this cluster" gets stronger.
3. **Instance network** (`10-key-de-numbers`): "Mid-size instances: 10 to 25 Gbit/s". The published baseline for an 8 vCPU general-purpose instance is about 3 Gbit/s (12.5 burst); 10 to 25 Gbit/s sustained starts around 32 vCPU.
4. **Post-shuffle partition size** (`10-key-de-numbers`, `01-spark-internals`): "100 to 200 MB each after the shuffle" with AQE. AQE's shipped advisory size is 64 MB. Either state the 64 MB default or tell readers to raise it.
5. **Tasks per stage** (`10-key-de-numbers`): "2 to 4 times the core count". The Spark tuning guide says 2 to 3.
6. **Flink checkpoint interval** (`08-flink`): "1 minute is a common default". Flink has no default interval; checkpointing is off until you set one. Say "a common choice".

Imprecise (right ballpark, should be reworded):

7. **Object storage first byte** (`10-key-de-numbers` and lessons that quote "10 to 100 ms"): AWS says tens of ms median for small requests and 100 to 200 ms for consistent small-object latency. Use "tens of ms typical, 100 to 200 ms tail".
8. **BigQuery unit**: lessons say "$5 to 6.25 per TB". BigQuery is $6.25 per **TiB** (first TiB each month free, 10 MB minimum per table); Athena is $5 per TB. Fine at interview precision, but name which is which once in the number sheet.
9. **Spot** (`10-key-de-numbers`, `05-cost-optimization`): "60 to 70 percent cheaper". AWS publishes "up to 90%". Keep 60 to 70 as typical and add the published 2-minute interruption notice.
10. **ForSt** (`08-flink`): call it experimental, as the Flink docs do.
11. **Broker disk**: lessons say long retention is expensive but never give the price. MSK broker storage is $0.10/GB-month (about 4x S3), tiered storage $0.06/GB-month.

Invented-looking figures where no vendor publishes a number (keep, but label as assumptions):

12. Kafka compression ratios (lz4 3x, zstd 4 to 6x), JSON to Parquet ~5x.
13. Spark throughput per core (10 to 50 MB/s; 5 to 20 with shuffle), 4 to 5 cores per executor, 4 to 8 GB per core.
14. Flink 5,000 to 20,000 events/s per core with RocksDB; "tens to a few hundred GB" of RocksDB state per TaskManager.
15. CDC initial snapshot "about 20 MB/s through one connection" (`09-debezium`, `04-cdc-patterns`, `05-cdc-replication`, `02-ingestion-patterns`).
16. Search index "~2x raw" (`01-log-aggregation`): no published ratio; justify it as primary + one replica, and mention logsdb.
17. Object storage "50 to 100 MB/s per connection", same-AZ and cross-region RTTs, memory/NVMe/HDD figures.

Confirmed as correct (no change): S3/GCS storage and request prices, archive tier range, egress and cross-AZ prices, gp3 price and 125 MB/s default, 8 vCPU VM ~$0.40/hr, S3 3,500/5,500 per prefix, S3 Express single-digit ms, Kafka 1 MB message limit, `linger.ms` 5 since 4.0, KRaft only since 4.0, Kafka per-partition 10 MB/s planning figure, Spark 128 MB splits, 200 shuffle partitions and AQE on since 3.2, Iceberg 512 MB target, Delta 1 GB OPTIMIZE target, Snowflake credit ladder and $2 to 4 per credit, Athena $5/TB, Postgres unlimited slot WAL by default.

## Missing figures worth adding to the number sheet

- Kafka default retention 7 days; Confluent capacity unit ~60 MB/s ingress; managed broker disk ~$100/TB-month.
- Spark: 10 MB broadcast threshold, skew = 5x median and > 256 MB, executor overhead 10% (min 384 MB).
- Parquet row groups 512 MB to 1 GB; Databricks autotuned 256 MB to 1 GB by table size.
- Snowflake 60-second minimum per resume; BigQuery 10,000 partitions per table and 1 TiB free; BigQuery Enterprise ~$0.06/slot-hour.
- GCS 1,000 writes/s and 5,000 reads/s per bucket initially, doubling every 20 minutes.
- Flink 2 GB per key and per value in RocksDB.
- Aurora replica lag under 100 ms as the published "replication lag" reference.
- Elasticsearch 10 to 50 GB per shard, 1,000 shards per node.
- Key-value store reads in single-digit ms.
- S3 Standard-IA ~$12.50/TB-month; S3 Express ~$110/TB-month.

## Method and caveats

- AWS prices come from the public AWS Price List API JSON for us-east-1 (S3, AWSDataTransfer, AmazonMSK), which is the machine-readable form of the pricing pages. Deep Archive storage ($0.00099/GB) and the m7i.2xlarge rate were not in the files pulled; they match the AWS pricing pages and several mirrors.
- GCP prices come from the HTML of the BigQuery and Cloud Storage pricing pages; hourly GiB rates were converted at 730 hours per month.
- Snowflake's consumption table is a PDF that could not be text-extracted locally; the $2/$3/$4 per-credit figures and the $23/TB storage figure come from a search snapshot of that PDF and Snowflake's own docs examples. Re-check before quoting an exact edition price.
- Kafka throughput and latency figures are vendor benchmarks and planning guides, not guarantees. The Confluent benchmark predates current hardware.
- Project docs read: Spark 4.3, Flink 2.3, Kafka 4.1 config pages, Debezium 3.7, PostgreSQL 18, Iceberg latest.
