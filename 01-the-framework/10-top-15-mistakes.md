# Top 15 Mistakes

Interviewers rarely reject a candidate for one wrong technology choice. They reject for a pattern: no numbers, no failure handling, no sense of who reads the data. This lesson lists the 15 patterns that cost the most points, so you can check your own answers against them.

## The Problem

Imagine two candidates given the same prompt: "Design the data pipeline behind a meal-kit company's analytics." Both know Kafka, Spark and a warehouse equally well.

Candidate A says "Kafka into Spark Streaming into Snowflake" within the first minute, draws it, and spends 40 minutes defending it. The interviewer asks what happens when the same event arrives twice, and the answer is "Kafka handles that". Asked how fresh the data needs to be, A says "real time".

Candidate B asks who reads the output and how soon they act on it, learns that marketing checks campaigns after lunch and finance needs exact-to-the-cent revenue, and designs two paths. B is less polished with tools and still gets the offer.

What separates them is a handful of habits. Here they are, grouped by where in the [delivery framework](02-delivery-framework.md) they bite:

| Mistakes | Framework steps | Theme |
|---|---|---|
| 1–5 | Before drawing anything | Answering the wrong question |
| 6–10 | Architecture and data model | Designing for the happy path and not the reader |
| 11–15 | Pipeline, deep dives, monitoring, time | Operating the system |

Each entry has the same shape: what it looks like, why it hurts, the fix, and the lesson that teaches the fix in full. This lesson does not re-teach those lessons. Follow the links when a fix is unfamiliar.

## Mistakes 1–5: Answering the Wrong Question

### 1. Treating it as a software engineering round

**Looks like:** Opening with APIs, load balancers, user-facing caches and database sharding.

**Why it hurts:** The interviewer is scoring data correctness, freshness, cost and consumers. A web-service design shows none of them, and you used your best minutes on the wrong axes.

**Fix:** Open with "who consumes this data, and how fresh and exact must it be?" See [How Interviews Work](01-how-interviews-work.md).

### 2. Naming tools in the first two minutes

**Looks like:** "I'd use Kafka, Spark and Snowflake" before any requirement exists.

**Why it hurts:** You committed to an answer before you knew the question. When a requirement later contradicts the tools (a 15-minute freshness target does not need Kafka), you either defend a bad fit or visibly backtrack.

**Fix:** Name the job each box does ("a durable log that can replay"), and name a product only when asked or after the requirements justify it. See [High-Level Architecture](05-high-level-architecture.md).

### 3. Accepting "real time" and other numberless requirements

**Looks like:** Writing "fast", "reliable", "accurate" on the board, or taking "real time" at face value.

**Why it hurts:** A streaming path costs more and is harder to run than an hourly batch, and "real time" often means "I look at it after lunch". Without a number you cannot justify any later choice.

**Fix:** Ask what decision is made with the number and how soon they act. Write "under 5 minutes", "99.9% complete", "exact to the cent". See [Requirements Gathering](03-requirements-gathering.md).

### 4. Not scoping the problem

**Looks like:** Trying to design ingestion, recommendations, fraud checks and the executive dashboard in one 45-minute round.

**Why it hurts:** You finish nothing, and the interviewer cannot tell which parts you think matter. Cutting scope is something they score.

**Fix:** State two to four core requirements and a "below the line" list of what you are deliberately leaving out, and get a nod. See [Requirements Gathering](03-requirements-gathering.md).

### 5. Skipping volume, or doing math that changes nothing

**Looks like:** Either no numbers at all ("it's big data"), or three minutes computing storage to three significant figures.

**Why it hurts:** 2,000 events a minute fits in one small database and a scheduled job. 200,000 events a second does not. Without the estimate you cannot say which side you are on; with too much precision you burn the clock on a number that moves no decision.

**Fix:** Estimate each source, round hard, and state the conclusion ("about 30 GB a day, so this is small"). Use the thresholds in [Key DE Numbers](../02-core-concepts/10-key-de-numbers.md). See [Sources and Volume](04-sources-and-volume.md).

## Mistakes 6–10: Designing for the Happy Path, Not the Reader

### 6. The happy-path diagram

**Looks like:** Every event arrives once, in order, on time, well-formed.

**Why it hurts:** Real data arrives twice, late and malformed, and the interviewer knows it. A design with no word about duplicates, late events or reruns is a design for a world that does not exist.

**Fix:** Say once, early, how each is handled: deduplicate on an event ID, recompute recent windows for late data, make reruns safe. See [Pipeline Design](07-pipeline-design.md), [Late-Arriving Data](../02-core-concepts/08-late-arriving-data.md) and [Deduplication at Scale](../02-core-concepts/09-deduplication-at-scale.md).

### 7. One pipeline for every consumer

**Looks like:** A single path, sized for "the data", feeding marketing, finance and data science.

**Why it hurts:** If finance needs exact numbers and marketing needs hourly ones, a path built for the strictest consumer wastes money on the other and a path built for the loosest fails finance.

**Fix:** List the consumers with their freshness and correctness needs, and give consumers with different needs their own path and serving table. See [High-Level Architecture](05-high-level-architecture.md).

### 8. No raw layer and no serving layer

**Looks like:** Data is cleaned on the way in and consumers query whatever tables the pipeline happens to produce.

**Why it hurts:** A bug in the cleaning logic is permanent, because the original data is gone. And consumers coupled to your intermediate tables break every time you change them.

**Fix:** Keep raw data as it arrived (cheap), and publish small stable tables shaped for each consumer. See [High-Level Architecture](05-high-level-architecture.md).

### 9. No stated grain

**Looks like:** Drawing a table and listing columns without saying what one row means.

**Why it hurts:** If you cannot say what a row is, you cannot say whether a SUM is correct. Order-level columns sitting next to line-level columns get counted once per line, and revenue doubles quietly.

**Fix:** Say "one row per order line" before listing a single column. See [Data Model Design](06-data-model-design.md).

### 10. Modeling the source, or erasing history

**Looks like:** Copying the application's normalized tables into the warehouse, or overwriting a customer's city in place when it changes.

**Why it hurts:** The first hands consumers a join puzzle. The second erases the history behind "revenue by region as it was last year".

**Fix:** Model the questions consumers ask. Ask "will anyone report by this attribute as it was?" before choosing between overwriting and keeping versions (a slowly changing dimension, or SCD, keeps old versions of a changed row). See [Data Model Design](06-data-model-design.md).

## Mistakes 11–15: Operating the System

### 11. Streaming everywhere

**Looks like:** Putting every path on a stream processor because it sounds modern.

**Why it hurts:** It adds cost, state to manage and failure modes. At 230 events a second with a 5-minute target, a micro-batch job (a small batch run every minute or two) is enough and far cheaper.

**Fix:** Decide batch or streaming path by path, from the freshness number, and say what the cheaper option would cost in staleness. See [Pipeline Design](07-pipeline-design.md).

### 12. "The scheduler retries it" as the whole failure story

**Looks like:** "If it fails, Airflow retries" with nothing about what the rerun does.

**Why it hurts:** A retry of a job that appends rows duplicates data. The retry is only safe because of the write pattern underneath, and that is the part the interviewer is asking about. Related slips: reading "everything up to now" so reruns give different answers, retrying forever, and crashing or silently dropping on one bad record.

**Fix:** Describe the write (overwrite the partition, or MERGE, which updates a row if its key exists and inserts it if not), pin each run's input range, cap retries with growing waits (backoff), and send bad records to a dead-letter store (a side table or topic for records that cannot be processed). See [Pipeline Design](07-pipeline-design.md) and [Backfill and Reprocessing](../02-core-concepts/03-backfill-and-reprocessing.md).

### 13. Diving into your favorite topic, or waiting to be asked

**Looks like:** Ten minutes on Kafka internals for a system that peaks at 7,000 events a second, or five topics in one sentence each.

**Why it hurts:** The first spends your best minutes on your safest topic. The second is a list of buzzwords with no mechanism, number or trade-off. If the first question about your design's weakness comes from the interviewer, you have told them you did not see it.

**Fix:** Choose the dive from the requirements and the volume math, offer the risk yourself, and go two levels deep on two topics. Show the naive option, why it fails, and what the fix costs. See [Deep Dives](08-deep-dives.md).

### 14. Monitoring that the job ran, not that the data is right

**Looks like:** "We'd use Prometheus, Grafana and PagerDuty", or no monitoring at all because time ran out.

**Why it hurts:** A job that succeeds with zero rows is the most common silent failure in data work, and tool names say nothing about "what number counts as a problem?". Skipping the step costs you at any level.

**Fix:** In three minutes, give freshness, completeness and quality SLAs with numbers, the one check that matters most, and what happens when it fails. See [Monitoring and SLAs](09-monitoring-and-slas.md) and [Monitoring and Alerting](../02-core-concepts/06-monitoring-and-alerting.md).

### 15. Losing control of the clock

**Looks like:** Forty minutes of beautiful architecture, then a rushed or missing pipeline, model and monitoring. Or, in the other direction, silence for two minutes while thinking.

**Why it hurts:** The steps you drop are exactly where correctness and operations live. And the interviewer cannot score what they cannot hear.

**Fix:** Say your plan out loud, check the clock at the end of the architecture step, and compress rather than skip. If you need to think, say "give me thirty seconds" and then take thirty seconds. See [The Delivery Framework](02-delivery-framework.md).

## In the Interview

You cannot hold 15 rules in your head under pressure, so do not try. Use the list in two ways.

**Before the interview, rehearse with it.** Pick a practice prompt, answer it out loud, and afterwards go through the 15 as a checklist. Mark which ones you committed. Most people have two or three habitual ones. Those are the only ones to drill, and you will find that they usually cluster in one theme: tools first, no numbers, or no failure handling.

**During the interview, use the five questions that prevent most of them:**

- Who reads this, and what do they do with it? (prevents 1, 3, 7)
- What number makes this good enough? (prevents 3, 5, 11)
- What does one row mean? (prevents 9, 10)
- What happens when this runs twice, or late? (prevents 6, 12)
- How would I know it broke? (prevents 14)

> [!TIP]
> If you realize mid-answer that you made one of these mistakes, say so and fix it: "I skipped the grain; let me state it." Interviewers score recovery well. They score defending the mistake poorly, and a silent fix they never see scores nothing.

## Common Mistakes

> [!WARNING]
> **Memorizing the list as a script.** Reciting "I'll now handle idempotency" with no connection to the prompt is its own mistake. Each fix works because it uses the prompt's actual numbers and consumers.

> [!WARNING]
> **Over-correcting.** A candidate who fixes mistake 3 by asking twelve questions has made a different mistake (see [Requirements Gathering](03-requirements-gathering.md)). Offer assumptions, confirm in bulk, move on.

> [!WARNING]
> **Fixing the symptom, not the habit.** If you keep skipping failure handling, adding a sentence about retries will not help. Ask which framework step you tend to rush when nervous, and protect that step.

## Key Takeaways

- Most failures are habits, not knowledge gaps: tools before requirements, no numbers, happy-path designs, and no failure or monitoring story.
- The mistakes cluster by phase: wrong question (1–5), wrong design for the reader (6–10), unoperated system (11–15).
- Each fix is small and specific: a number, a stated grain, a write pattern, a check with a threshold.
- Rehearse by scoring your own practice answers against the list, and drill your two or three personal habits only.
- Recover out loud. Naming and fixing a mistake mid-answer scores better than hoping nobody noticed.

## Where to Go Next

- [The Delivery Framework](02-delivery-framework.md): the structure that prevents most of these by design.
- [Deep Dives](08-deep-dives.md): where the strongest candidates separate themselves.
- [Key DE Numbers](../02-core-concepts/10-key-de-numbers.md): the thresholds that make volume estimates quick.
- [Module 1 quiz](11-quiz.md): test whether you can spot these mistakes in a sample answer.
- Related breakdowns: [Log Aggregation](../05-breakdowns-core/01-log-aggregation.md) and [Ad Impression and Click Pipeline](../06-breakdowns-advanced/08-ad-clickstream.md), for how the mistakes are avoided in a full answer.
