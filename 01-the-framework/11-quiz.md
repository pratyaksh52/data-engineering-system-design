# Module 1 Quiz: The Framework

Fifteen questions on the interview round and the seven-step delivery framework. Answer each one out loud or on paper first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. The wrong opening

The prompt is: "Design a pipeline that powers a daily revenue dashboard for an online marketplace." A candidate spends ten minutes on a REST service that accepts orders, with a cache and a load balancer in front. The interviewer asks, "What happens when payments corrects an order from three days ago?" and the candidate has no answer. What went wrong, and what should the first two minutes have sounded like?

<details>
<summary>Answer</summary>

The candidate prepared for a software engineering round (serving requests quickly) instead of a data engineering round (moving and shaping data so consumers can trust it). Nothing in the design was built to change numbers that had already been published, because the candidate never asked who reads the dashboard, how fresh it must be, or whether published numbers can change.

A strong opening restates the problem and asks about consumers: "Before I draw anything, who reads this dashboard, how fresh must it be, and can yesterday's numbers change after we publish them?" The four themes of a DE round are correctness, freshness, cost and consumers, and the correction question touches the first and last of them.

The tempting fix is "learn more tools", but the candidate already knew the tools. What was missing was knowing what the round tests.

Covered in [How Data Engineering Design Interviews Work](01-how-interviews-work.md).
</details>

### Q2. Silence while thinking (multiple choice)

A candidate with strong knowledge thinks silently for four minutes at a stretch. On which rubric dimension does the interviewer mark them down?

- A. Communication and ownership only
- B. Technical depth only, because they never showed the mechanism
- C. Several dimensions at once, including breadth and depth
- D. None, as long as the final diagram is correct

<details>
<summary>Answer</summary>

**C.** Communication is scored on every dimension. The interviewer cannot see breadth, depth or trade-off reasoning that happens in your head, so silence costs you on all of them at once.

A is the tempting answer because silence feels like a communication problem. It undercounts the damage. B is wrong because it has the same blind spot from the other side: the interviewer cannot see depth you never say aloud, and it ignores the breadth and communication marks. D is wrong because the conversation is the product: a perfect diagram you cannot explain scores lower than a rougher one you can defend. The fix is one sentence of reasoning per decision, or "give me thirty seconds to think" followed by exactly that.

Covered in [How Data Engineering Design Interviews Work](01-how-interviews-work.md).
</details>

### Q3. Minute 27 and no model

You have a 50-minute round. At minute 27 you finish the architecture diagram and realize you have not touched the data model, the pipeline, or monitoring. What do you do?

<details>
<summary>Answer</summary>

Compress what is left instead of finishing anything perfectly. An 80% architecture plus a model, a pipeline and a monitoring step beats a polished architecture and nothing else. Say it aloud: "I'm at the halfway mark, so I'll move to the data model and keep each remaining step short."

Then protect the right steps. Pipeline design and monitoring are where correctness and operations live, and they separate senior from mid-level answers, so shorten the model before you drop either of them. If the prompt is itself about a warehouse or reporting model, flip it: spend the minutes on the model and sketch the pipeline after.

The tempting answer is to add a few more details to the architecture first. Step 3 is the easiest to overrun because drawing is fun, and the interviewer can pull detail out later in the deep dives.

Covered in [The Delivery Framework](02-delivery-framework.md).
</details>

### Q4. Why the model comes later (multiple choice)

In most data prompts the framework puts the data model (step 4) after the architecture (step 3), the opposite of many software design rounds. Why?

- A. Interviewers prefer to see diagrams before schemas
- B. Data systems have several models, one per layer, and you cannot model a layer you have not decided exists
- C. The architecture determines the cloud vendor, which determines the schema syntax
- D. Table design is not part of a data engineering round

<details>
<summary>Answer</summary>

**B.** A data system has a raw layer (one row per event as received), a cleaned layer (deduplicated and typed) and a serving layer (shaped for a consumer, for example one city per five-minute window). Each has its own grain, key and partitioning, and each only makes sense once it is on the board. If you model first, you tend to design one table that tries to be all three.

A describes a preference, not a reason. C is wrong because the schema syntax follows the engine you pick, not the other way round, and the vendor is a late decision anyway. D is false: the model is where an interviewer finds out whether you build tables people can use. The order flips when the prompt is itself about a warehouse or reporting model, or when the consumers' query constraints drive the storage choice. In that case say that you are flipping.

Covered in [The Delivery Framework](02-delivery-framework.md), with the modeling decisions in [Data Model Design](06-data-model-design.md).
</details>

### Q5. "We need it real time"

The interviewer, playing a marketing stakeholder, says the campaign dashboard must be "real time". How do you respond, and what does your answer change in the design?

<details>
<summary>Answer</summary>

Ask what decision is made with the number and how soon they act on it: "When someone sees a campaign underperforming, what do they do, and how quickly?" "Real time" is a word, not a requirement. If the answer is "we check campaigns after lunch", the real requirement is hourly freshness. A courier-dispatch screen that reroutes drivers, by contrast, really does need seconds.

Write the number down ("freshness: 1 hour") and point at it later when you justify an hourly batch instead of a stream processor. Anchoring with two options helps: "within a minute, or within an hour?" The cost difference between those designs is large, which is why the number matters.

The tempting response is to accept "real time" and start drawing a streaming system. That commits you to the most expensive path before you know it is needed. Also remember freshness is not query latency: a dashboard can answer in 50 ms and still show yesterday's data.

Covered in [Requirements Gathering](03-requirements-gathering.md).
</details>

### Q6. The rate-limited history

Finance wants two years of payments history. You will load it from the payments provider's pull API, which allows 100 requests a minute with up to 100 records each. The company has 300,000 payments a day. Roughly how long does the backfill take, and what do you propose?

<details>
<summary>Answer</summary>

Two years is 730 days at 300,000 records a day, about 219 million records. At 100 requests a minute with 100 records each you read 10,000 records a minute, or 14.4 million a day. That is about **15 days** of continuous pulling, and it competes with the daily sync for the same quota.

So the rate limit, not the data volume, decides the backfill. Propose asking the provider for a bulk export of the history and using the API only for new data. Say the implication in one sentence: "Volume is small, but the quota makes the API the wrong tool for history."

The tempting answer is "219 million rows is small, so it's trivial". It is small for object storage and a batch engine, but the bottleneck is how fast the source lets you read it. This is why you name sources by how they are read, and do the math that changes a decision.

Covered in [Sources and Volume](04-sources-and-volume.md).
</details>

### Q7. What justifies the message log? (multiple choice)

In the meal-kit design, app events peak at about 3.5 MB/s and the total is about 33 GB a day. Ops needs orders by delivery slot within 15 minutes. Which fact most justifies adding a message log and continuous delivery of orders and events?

- A. The 3.5 MB/s peak, which is too much for a scheduled job
- B. The 33 GB a day, which is too large for batch
- C. The 15-minute freshness requirement, which needs continuous delivery with replay if a job fails
- D. The two-year retention requirement

<details>
<summary>Answer</summary>

**C.** The volume is small. 3.5 MB/s is well under the roughly 10 MB/s planning figure for a single Kafka partition, and 33 GB a day takes a small machine under an hour. Volume does not force the log. Freshness does: orders must arrive continuously instead of nightly, and a log lets a failed job resume where it stopped.

A and B are the tempting answers because big-sounding numbers feel like a reason. Do the math and they point the other way. D is handled by cheap object storage, not a log. The sentence to say in the interview is "volume does not force streaming; freshness does".

Covered in [Sources and Volume](04-sources-and-volume.md) and [High-Level Architecture](05-high-level-architecture.md).
</details>

### Q8. Getting orders out of the database

Ops needs orders from the production orders database within 15 minutes, about 30 row changes a second, and the orders table is about 200 GB. Compare querying production on a schedule, an incremental extract, and CDC. Which do you pick for ops alone, and what would make you change your mind?

<details>
<summary>Answer</summary>

**Bad: query production directly** (`SELECT *` every 10 minutes). Reading 200 GB at 100 MB/s takes about 35 minutes, so a run never finishes inside its interval. It also competes with customers placing orders, and it keeps no history.

**Good: incremental extract on `updated_at` from a read replica.** Every 5 minutes it reads only rows changed since the last high-water mark. At 30 changes a second each run reads a few thousand rows, and the primary is untouched. Its gaps: it cannot see deleted rows, it shows only the last state of a row that changed twice between runs, and it silently misses data if any code path forgets to update `updated_at`.

**Great: CDC into the message log.** It captures every insert, update and delete in order and is replayable. It costs a connector to operate, a careful initial snapshot, and schema-change handling.

For ops alone, take Good. What moves you to CDC is the combination: finance needs every cancellation reconciled exactly, ops wants status timings, and data science wants a faithful history. Choosing the most advanced option with no reason is a mistake too.

Covered in [High-Level Architecture](05-high-level-architecture.md); CDC itself is in [CDC Patterns](../03-architecture-patterns/04-cdc-patterns.md).
</details>

### Q9. Priya moves to Bristol

A customer dimension is updated in place when a customer moves from Leeds to Bristol in March. In January, finance asks for last year's revenue by city, and Leeds revenue has quietly moved to Bristol. What is the fix, and how do you decide which columns it applies to?

<details>
<summary>Answer</summary>

The dimension was handled as a **Type 1** (overwrite) change, which loses history. Use **Type 2** for the city: close the old row with an end date and insert a new row for the new value, each version with its own surrogate key. Orders placed before the move carry the old key and report Leeds; later orders carry the new key and report Bristol. Finance's question then needs no special query.

Decide per column, not per table, by asking "will anyone report by this attribute as it was?" City and customer tier are Type 2. A corrected typo in a name is Type 1, because the old value was a mistake. The cost of Type 2 is a growing dimension (about 75,000 new rows a year at 1.5 million customers with 5 percent moving, which is trivial) and a load that must close old rows and open new ones idempotently.

The tempting answer is Type 2 everywhere. That adds complexity on attributes nobody reports over time.

Covered in [Data Model Design](06-data-model-design.md).
</details>

### Q10. What does a SUM mean? (multiple choice)

A table has one row per order line. It also carries `order_total`, which repeats on every line of the order. Orders average four lines. A dashboard runs `SUM(order_total)` over a day. What does it report?

- A. The correct total revenue
- B. Roughly four times the correct revenue
- C. Roughly a quarter of the correct revenue
- D. It depends on the partition key

<details>
<summary>Answer</summary>

**B.** Each order's total is repeated once per line, so it is summed about four times. This is the mixed-grain mistake: an order-level measure sitting beside line-level columns. With 300,000 orders and about 1.2 million lines a day, the dashboard adds up 1.2 million order totals instead of 300,000.

The fix is to keep each measure at the grain of its row: put line amounts in the line-grain fact table (`line_amount` is summed safely) and keep order-level attributes in an order-grain table. This is why you state the grain before listing columns. A is the tempting answer if you assume one row per order, which is exactly the assumption an unstated grain lets you make. The partition key (D) affects how much data is read, never what the sum means.

Covered in [Data Model Design](06-data-model-design.md).
</details>

### Q11. "Airflow retries it"

The nightly finance job inserts 300,000 order rows into the revenue table. It crashes after writing 200,000. The orchestrator retries it automatically. A candidate says this is handled. Is it, and what do you change?

<details>
<summary>Answer</summary>

Not as described. If the job appends with a plain `INSERT`, the retry starts from the top and writes all 300,000 again. The table now holds 500,000 rows, 167% of the truth, and nobody is alerted. A retry is only safe because of the write pattern underneath.

Make the step idempotent. For a dated batch output, **overwrite the partition**: the job takes its date as a parameter, pins its input to that date, and replaces that day's partition atomically, so one run or five leave exactly 300,000 rows. For a table of entities that change (current order status), use a `MERGE` on the business key, after taking the latest change per key. For a stream, write with a deterministic key such as the event ID.

Then the retry story is complete: retry transient errors with backoff and a cap, alert after the cap, and explain that retries are safe because each write is a partition overwrite. A job that takes its date as a parameter is also a backfill tool.

Covered in [Pipeline Design](07-pipeline-design.md).
</details>

### Q12. The 2 a.m. job on partial data

The finance job is scheduled for 2:00 a.m. The payments pull was late tonight. The job ran at 2:00 against partial payments and reported success. How do you redesign the scheduling?

<details>
<summary>Answer</summary>

Trigger on data, not only on time. Model the pipeline as a DAG where the reconciliation task depends on both the orders partition and the payments partition for the date. A sensor (or an event emitted when upstream finishes) lets the task run when its inputs are really there. Keep the clock only as the earliest start time.

Give every wait a timeout and an alert. If the payments pull is not there by a set time, the job should not wait forever or run on nothing: page someone, or publish the prior data marked stale. Work backwards from the deadline: if finance needs the table by 07:00 and the job takes 40 minutes after the pull, the pull must finish by 06:20 at the latest, and earlier if you want margin.

Tie each run to a data interval ("October 31"), not the wall-clock moment it started, so a rerun three days later still does the right thing.

The tempting fix is to move the schedule to 4:00 a.m. That hides the problem until the next late night.

Covered in [Pipeline Design](07-pipeline-design.md); the SLA arithmetic connects to [Monitoring and SLAs](09-monitoring-and-slas.md).
</details>

### Q13. Where is it weakest? (multiple choice)

You have finished the meal-kit design. Events average 700 a second and peak at 7,000. Finance needs revenue exact to the cent, and refunds land days after a day is closed. The interviewer asks, "Where is this design weakest?" Which answer is strongest?

- A. "The Kafka cluster. We could add more partitions in case volume grows."
- B. "Cost. Everything could be cheaper."
- C. "Finance. Revenue must match payments to the cent and refunds arrive after day-close, so I'd like to cover how corrections flow in and how we reconcile. Or is there another area you'd rather see?"
- D. "Nothing stands out. I covered the requirements."

<details>
<summary>Answer</summary>

**C.** Pick the dive from your own requirements and volume math. "Exact to the cent" makes correctness a certain dive, refunds make late data one too, and the small volume makes scale a one-sentence mention. C gives a reason, names two topics, and hands the interviewer a way to redirect.

A picks the first scary-sounding component. At 7,000 events a second a small cluster has room to spare, so it spends your best minutes on your safest topic. B names a suspect without a number or mechanism. D tells the interviewer you did not see the weak spots. Keep a list of parked risks while you design, so this answer is ready.

Covered in [Deep Dives](08-deep-dives.md).
</details>

### Q14. A green dashboard and an empty table

The nightly job started at 02:00, ran for 40 seconds and reported success. At 09:00 finance finds Monday's revenue table empty. The payments extract returned zero rows because of an expired credential, and the table was rebuilt from nothing. Your monitoring alerted on job failures only. What monitoring would have caught it, and what should the pipeline have done?

<details>
<summary>Answer</summary>

The monitoring watched the pipeline (did the job run?) instead of the data. Measure the data against a reference:

- **Freshness** from the data itself: the newest event time or the existence of yesterday's partition with rows, not when the job finished.
- **Completeness** against a reference: the source's own count, a control total, or history. Even "yesterday's row count must be at least 50% of the same weekday last week" would have caught this.
- **Quality** with a few rules and a reconciliation against the payments provider's total (for example within 0.01%).

Put checks at stage boundaries so a problem is caught at the raw layer as a re-pull, not by finance on Thursday.

The pipeline's behavior on failure should be **block**: refuse to overwrite the serving table, keep showing the prior good version with a "Monday is delayed" banner, and page someone at about 02:05. Block fits finance because wrong data is worse than late data. For a marketing dashboard, **warn** may fit better. Alert on SLAs at risk, not on every task failure.

The tempting answer is "add more dashboards and tools". Tools do not tell you which number counts as a problem.

Covered in [Monitoring and SLAs](09-monitoring-and-slas.md).
</details>

### Q15. Grade this answer

A candidate answers a practice prompt: "I'd use Kafka and Spark Streaming into Snowflake, because it needs to be real time. If a job fails, Airflow retries it. We'd add monitoring with Grafana." Name the mistakes you can spot, and give a one-line fix for each.

<details>
<summary>Answer</summary>

At least four of the 15 patterns appear:

- **Tools in the first sentence (mistake 2).** Fix: name the job each box does and choose products only after requirements and volume justify them.
- **Taking "real time" at face value (mistake 3).** Fix: ask what decision is made with the number and how soon they act, then write a number such as "under 5 minutes".
- **Streaming chosen with no freshness number (mistake 11).** Fix: decide path by path, picking the slowest option that meets each freshness target.
- **"The scheduler retries it" as the whole failure story (mistake 12).** Fix: describe the write (partition overwrite or `MERGE`), pin the input range, cap retries with backoff, and dead-letter bad records.
- **Monitoring that names a tool and no promise (mistake 14).** Fix: give freshness, completeness and quality SLAs with numbers, and say what happens when a check fails.

Also missing: any mention of consumers, volume, duplicates or late data. When you catch one of these in your own answer, say so and fix it out loud. Interviewers score recovery well and score defending the mistake poorly.

Covered in [Top 15 Mistakes](10-top-15-mistakes.md).
</details>
