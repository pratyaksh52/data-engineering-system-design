# Data Engineering System Design

A self-study course for the data engineering system design interview: the 45 to 60 minute round where you get a vague prompt ("design analytics for a music app") and have to design a data system out loud, defend your choices, and survive the follow-up questions.

## Who This Is For

Data engineers with roughly one to four years of experience who are heading into this round for the first time, or who have been in it and want a repeatable approach. You build pipelines at work. You have not yet had to design a large data system end to end in front of an interviewer.

**Assumed knowledge:** SQL, the basic difference between batch and streaming, and "used it at work" familiarity with Spark, Kafka, Airflow and a cloud warehouse. Everything beyond that is explained the first time it appears. Terms are collected in the [Glossary](GLOSSARY.md).

## What You Will Be Able to Do

- Take an open-ended prompt and run the conversation with a clear structure.
- Make choices you can defend with trade-offs and back-of-the-envelope numbers.
- Handle the deep-dive questions that decide the result.

The course is written from the interviewer's side of the table: what gets asked, what a strong answer sounds like, and what sinks candidates. It is cloud-neutral, so components are named generically first, with mainstream products mentioned in passing. It has no setup steps.

## How to Use It

**Full path.** Go in order. Module 1 gives you the framework. Modules 2 to 4 supply the building blocks. Modules 5 and 6 show the framework applied to twenty prompts. Attempt each breakdown yourself, on paper and against a timer, before you read it. Then take the module quiz.

**Short on time.** Read these eight lessons, in this order:

1. [The Delivery Framework](01-the-framework/02-delivery-framework.md)
2. [Requirements Gathering](01-the-framework/03-requirements-gathering.md)
3. [Top 15 Mistakes](01-the-framework/10-top-15-mistakes.md)
4. [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)
5. [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)
6. [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)
7. [Design CDC Replication from OLTP Databases into the Lake](05-breakdowns-core/05-cdc-replication.md)
8. [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)

**Targeted prep.** If the interview is about one tool or pattern, jump to that lesson in Module 3 or 4, then the breakdowns that link to it.

## How Each Lesson Is Built

- **Concept lessons** (Modules 1 to 3) open with a concrete problem, explain the idea with an example, show how to use it in the interview, list common mistakes, and end with key takeaways.
- **Technology deep dives** (Module 4) cover when to pick the tool and when not to, how it works inside, its key numbers, the follow-ups interviewers like, and alternatives.
- **Breakdowns** (Modules 5 and 6) follow the delivery framework step by step: requirements, sources and volume, high-level design, data model, pipeline design, deep dives, monitoring and SLAs. They finish with what is expected at mid-level, senior and staff+.
- **Quizzes** end each module with scenario and multiple-choice questions. Every answer is hidden until you open it and links back to the lesson that covers it.

> [!TIP]
> Company names in breakdown titles are only the familiar framing of an interview prompt. Nothing here claims to describe how any company actually built its systems.

## Table of Contents

Reference: [Glossary](GLOSSARY.md)

### [Module 1: The Framework](01-the-framework/index.md)

The structure of the round and the seven steps you follow in it.

1. [How Data Engineering Design Interviews Work](01-the-framework/01-how-interviews-work.md)
2. [The Delivery Framework](01-the-framework/02-delivery-framework.md)
3. [Requirements Gathering](01-the-framework/03-requirements-gathering.md)
4. [Sources and Volume](01-the-framework/04-sources-and-volume.md)
5. [High-Level Architecture](01-the-framework/05-high-level-architecture.md)
6. [Data Model Design](01-the-framework/06-data-model-design.md)
7. [Pipeline Design](01-the-framework/07-pipeline-design.md)
8. [Deep Dives](01-the-framework/08-deep-dives.md)
9. [Monitoring and SLAs](01-the-framework/09-monitoring-and-slas.md)
10. [Top 15 Mistakes](01-the-framework/10-top-15-mistakes.md)
11. [Module 1 Quiz: The Framework](01-the-framework/11-quiz.md)


### [Module 2: Core Concepts](02-core-concepts/index.md)

The ideas that come up inside almost every design.

1. [Partitioning](02-core-concepts/01-partitioning.md)
2. [Ingestion Patterns](02-core-concepts/02-ingestion-patterns.md)
3. [Backfill and Reprocessing](02-core-concepts/03-backfill-and-reprocessing.md)
4. [Data Lineage](02-core-concepts/04-data-lineage.md)
5. [Cost Optimization](02-core-concepts/05-cost-optimization.md)
6. [Monitoring and Alerting](02-core-concepts/06-monitoring-and-alerting.md)
7. [Data Contracts](02-core-concepts/07-data-contracts.md)
8. [Late-Arriving Data](02-core-concepts/08-late-arriving-data.md)
9. [Deduplication at Scale](02-core-concepts/09-deduplication-at-scale.md)
10. [Key DE Numbers](02-core-concepts/10-key-de-numbers.md)
11. [Module 2 Quiz: Core Concepts](02-core-concepts/11-quiz.md)


### [Module 3: Architecture Patterns](03-architecture-patterns/index.md)

Named ways to put a data platform together, and when each one fits.

1. [Lambda Architecture](03-architecture-patterns/01-lambda-architecture.md)
2. [Kappa Architecture](03-architecture-patterns/02-kappa-architecture.md)
3. [Medallion Architecture](03-architecture-patterns/03-medallion-architecture.md)
4. [CDC Patterns](03-architecture-patterns/04-cdc-patterns.md)
5. [Event Sourcing](03-architecture-patterns/05-event-sourcing.md)
6. [Data Mesh](03-architecture-patterns/06-data-mesh.md)
7. [Data Fabric](03-architecture-patterns/07-data-fabric.md)
8. [Micro-Batch vs Streaming](03-architecture-patterns/08-micro-batch-vs-streaming.md)
9. [Reverse ETL](03-architecture-patterns/09-reverse-etl.md)
10. [Module 3 Quiz: Architecture Patterns](03-architecture-patterns/10-quiz.md)


### [Module 4: Technology Deep Dives](04-technology-deep-dives/index.md)

How the common tools work, to the depth interviewers probe.

1. [Spark Internals](04-technology-deep-dives/01-spark-internals.md)
2. [Kafka](04-technology-deep-dives/02-kafka.md)
3. [Airflow](04-technology-deep-dives/03-airflow.md)
4. [dbt](04-technology-deep-dives/04-dbt.md)
5. [Snowflake: How a Modern Cloud Warehouse Works](04-technology-deep-dives/05-snowflake.md)
6. [Delta Lake](04-technology-deep-dives/06-delta-lake.md)
7. [Apache Iceberg](04-technology-deep-dives/07-iceberg.md)
8. [Flink](04-technology-deep-dives/08-flink.md)
9. [Debezium and CDC Tools](04-technology-deep-dives/09-debezium-and-cdc-tools.md)
10. [Orchestrator Comparison](04-technology-deep-dives/10-orchestrator-comparison.md)
11. [Module 4 Quiz: Technology Deep Dives](04-technology-deep-dives/11-quiz.md)


### [Module 5: Question Breakdowns, Core](05-breakdowns-core/index.md)

Ten full worked designs of classic prompts.

1. [Design a Log Aggregation Platform](05-breakdowns-core/01-log-aggregation.md)
2. [Design Click Analytics for a URL Shortener](05-breakdowns-core/02-url-shortener-analytics.md)
3. [Design an E-Commerce Analytics Warehouse](05-breakdowns-core/03-e-commerce-warehouse.md)
4. [Design a Real-Time Operations Dashboard](05-breakdowns-core/04-real-time-dashboard.md)
5. [Design CDC Replication from OLTP Databases into the Lake](05-breakdowns-core/05-cdc-replication.md)
6. [Design a Company-Wide Medallion Data Lake](05-breakdowns-core/06-medallion-data-lake.md)
7. [Design a Config-Driven ETL Framework](05-breakdowns-core/07-etl-framework.md)
8. [Design a Feature Store for ML](05-breakdowns-core/08-feature-store.md)
9. [Design a Data Quality Monitoring Platform](05-breakdowns-core/09-data-quality-monitoring.md)
10. [Design the Data Pipeline Behind Uber-Style Surge Pricing](05-breakdowns-core/10-surge-pricing.md)
11. [Module 5 Quiz: Core Breakdowns](05-breakdowns-core/11-quiz.md)


### [Module 6: Question Breakdowns, Advanced](06-breakdowns-advanced/index.md)

Ten harder prompts with more moving parts.

1. [Design Spotify-Style Listening Analytics and Royalty Counts](06-breakdowns-advanced/01-music-streaming-analytics.md)
2. [Design the Data Platform Behind Netflix-Style Video Recommendations](06-breakdowns-advanced/02-video-recommendations.md)
3. [Design a Real-Time Payment Fraud Detection Pipeline](06-breakdowns-advanced/03-fraud-detection.md)
4. [Design Twitter/X-Style Engagement Analytics](06-breakdowns-advanced/04-social-media-analytics.md)
5. [Design a Multi-Tenant Analytics Platform](06-breakdowns-advanced/05-multi-tenant-platform.md)
6. [Design an E-Commerce Recommendation Engine That Stays Fresh](06-breakdowns-advanced/06-recommendation-engine.md)
7. [Design the Data Pipeline Behind a LinkedIn-Style Activity Feed](06-breakdowns-advanced/07-activity-feed.md)
8. [Design an Ad Impression and Click Pipeline for Billing and Attribution](06-breakdowns-advanced/08-ad-clickstream.md)
9. [Design a Data Mesh Platform](06-breakdowns-advanced/09-data-mesh-platform.md)
10. [Design an IoT Sensor Data Pipeline](06-breakdowns-advanced/10-iot-sensor-pipeline.md)
11. [Module 6 Quiz: Advanced Breakdowns](06-breakdowns-advanced/11-quiz.md)
