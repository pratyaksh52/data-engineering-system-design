# Module 6 Quiz: Advanced Breakdowns

Fifteen questions on the ten advanced breakdowns: where a design bends, what breaks at scale, and what a senior or staff answer adds to a mid-level one. Answer each out loud or on paper first, then open the answer and compare your reasoning, not only your conclusion.

## Questions

### Q1. Paid once

A music service pays royalties on a 5-billion-plays-a-day ledger. A phone on a train uploads 40 plays, loses the response, and uploads the same batch again three days later. A teammate says, "Our stream processor is exactly-once, so we're covered." Is the label paid once? How do you make it so without scanning seven years of plays?

<details>
<summary>Answer</summary>

Not necessarily. Exactly-once covers a job's own retries and restarts. Here there are two different messages in the log, written three days apart by a client retry. Only the `play_id` knows they are the same play.

A stream-job dedup window is the freshness layer, not the guarantee. Keeping 24 hours of `play_id`s is about 250 GB of state, which is fine, but it misses the three-day retry. Stretching to 30 days is about 7.5 TB, which is too big to checkpoint.

The strong answer dedups in the daily build, bounded by play date. Every copy of a play carries the same device-stamped `play_ts`, so a duplicate can only collide with a row in the same `play_date` partition. Yesterday's arrivals touch at most 31 play dates, so the `MERGE` on `play_id` reads a few partitions, and bloom filters skip most files. Then make the ledger the second line of defense: post a play only if no `stream` row with its `play_id` exists. Add a content check on `(user_id, track_id, play_ts)` that flags rather than drops, since silently dropping a paid play is worse than a review.

Covered in [Music Streaming Analytics](01-music-streaming-analytics.md).
</details>

### Q2. Billions of impressions, 120 TB a day

A video service shows about 40 billion impressions a day. You want to log every feature the ranking model saw, so training matches serving. By value, that is about 120 TB a day. Finance balks. Someone proposes logging features for a 5% sample of pages. What do you do instead, and what rule keeps it safe?

<details>
<summary>Answer</summary>

Sampling cuts storage 20x but leaves 95% of impressions without features. You either train on 5% of your labels or reconstruct the rest, which brings back training-serving skew.

Log each value at the grain where it changes. Profile features change per request, so log them once per page by value (about 2 KB). Pair features and context change per impression, so log them per title by value (about 100 bytes). Title features change only with the catalog, so log a `snapshot_id` by reference. That is roughly 6 KB per page, about 6 TB a day raw and 1.2 TB as Parquet: a 20x reduction with no information lost. The training builder rehydrates title features by joining the 20 MB snapshot, which Spark broadcasts to every executor, so there is no shuffle on that side.

The safety rule: anything logged by reference must be immutable and kept as long as the log. A snapshot overwritten in place turns every reference into a lie. At 20 MB a day, keep all of them for the 90-day window.

Covered in [Video Recommendations](02-video-recommendations.md).
</details>

### Q3. 80 ms at the 99th percentile

Your fraud service must answer in 100 ms. On a sale day the online feature store's p99 rises to 80 ms. Do you approve or decline, and what do you design so that this is a decision you made rather than one that happened to you?

<details>
<summary>Answer</summary>

"Wait for every feature" is the bad answer: the fetch plus the 30 ms model blows the budget, the authorization service times out, and it applies a default that nobody on your team chose.

A hard deadline at the 25 ms feature budget, with defined defaults, is better, but a default of 0 for `device_attempts_1m` is exactly what a fraudster wants. Failing open on everything hands attackers a free window, and they time attacks to sale-day load.

The senior answer is tiered degradation, and it is neither "approve" nor "decline" for everyone. Fall back one tier at a time: if request-time counters time out, use the streaming aggregates' 1-hour counts (seconds stale), then the profile. Each fallback is a worse feature, not a missing one. Shed the least valuable reads first (merchant-level features matter least per payment). Then decide by stakes: low-amount payments from long-standing cards are approved, while high-amount payments or new devices get step-up authentication (the cardholder confirms in their bank's app) or review instead of a blind approval. Then record it: every decision logs `defaulted_features` and `degraded = true`, so training can exclude or flag those rows, and monitoring alerts on the default rate before losses show up. The staff-level addition is weighing a declined good customer against fraud loss when you set those thresholds with the risk team.

Covered in [Fraud Detection](03-fraud-detection.md).
</details>

### Q4. The viral post

A celebrity post gets 40,000 likes and 200,000 views a second. The count job is already pre-aggregating, so the counter store gets one write a second. But reads of that one key land on one shard. A teammate says, "Salt the counter key into 8 sub-keys." Respond.

<details>
<summary>Answer</summary>

Salting is the wrong tool. It splits a key so that writes spread across shards, but every read must then fetch all 8 sub-keys and add them, so a read-heavy key gets 8 times worse. Here the stream job has already turned 40,000 writes into one, so there is no write hot spot to fix; the load is reads. Adding replicas multiplies the cost of the whole cluster for one key and makes the count jump between asynchronous replicas.

A per-instance cache with request coalescing is good: with 500 instances the store sees at most 500 reads a second. But it is reactive (the first second of a viral post hits the store cold) and still sends 500 synchronized reads.

The great answer uses what the write side already knows. The count job computes the hot set (top 10,000 posts by rate) every second and publishes totals to a `hot_counts` topic. Every counter-service instance holds that set in memory, so hot reads never leave the process. The cost is about 0.5 GB/s of fan-out, and values are 1 to 2 seconds old, inside the 5-second target. Display rounding ("1.2M") lets counts above 10,000 be cached 5 to 10 seconds.

Covered in [Social Media Analytics](04-social-media-analytics.md).
</details>

### Q5. The 13-month query

At 10am one customer's analyst runs a 13-month funnel through your analytics SQL interface and every other tenant's dashboards slow down. Someone says to autoscale the query pool. What is your design?

<details>
<summary>Answer</summary>

Autoscaling alone hides the problem by paying for it. The pool grows to fit the noisiest tenant, and the bill lands on everyone's margin. Limits per tenant come first; scaling is for aggregate growth.

First split workloads: dashboards go to the OLAP store, ad hoc SQL to its own pool. Per-query timeouts and byte caps help, but they are the same for a $100 customer and a $500,000 one, and one tenant can still take every slot with 50 queries.

Put a query service with admission control in front of the engines. Concurrency is limited per tenant by plan, and a tenant's extra queries wait in its own queue. When the pool is busy, free slots go to the tenant with the fewest running queries, so a tenant sending 50 queries gets its 5 and everyone else still gets theirs. Estimate bytes scanned before running: large queries go to a separate lane, and over-cap queries are refused with a reason. The largest tenants get dedicated compute, so a 120 TB scan only slows its owner. Autoscale on demand across many tenants, not one queue.

Covered in [Multi-Tenant Platform](05-multi-tenant-platform.md).
</details>

### Q6. Cart, then cart page

A shopper adds a tent to the cart and reaches the cart page 400 ms later. The "complete your trip" row sometimes doesn't know about the tent, because the stream job hasn't updated the session store yet. Compare having the cart service write the session store synchronously with something else, and say which you'd ship.

<details>
<summary>Answer</summary>

Accepting stream lag ("p95 is 2 seconds") fails the promise: the next page often arrives in under a second.

The cart service writing the session store works for that case, but it puts the recommendation team's store on the checkout path (its latency and availability now affect carts), covers only server-side actions and not product views, and creates two writers, so an older stream write can overwrite the newer one unless both use write-if-newer on the same timestamp.

Ship request-carried actions. The client keeps its last 10 actions (SKU, type, `event_id`, timestamp) and sends them with every recommendation request, the same events it sends to the message log. The service reads the session record, adds the request's actions whose `event_id` isn't in it, recomputes the session vector in microseconds, and uses it for this request only. No write happens on the request path, the stream job stays the only writer, and the shared `event_id` makes the merge an exact dedup. This is read-your-writes for the shopper even when the pipeline is behind. Limit: the buffer is per device.

Covered in [Recommendation Engine](06-recommendation-engine.md).
</details>

### Q7. Redefining affinity

The ranking team wants a new affinity signal: decayed weights, comments worth more than views. A teammate proposes editing the job and letting tomorrow's run overwrite the old values. What goes wrong, and how do you ship it so an A/B test can run?

<details>
<summary>Answer</summary>

Overwriting breaks the live model, which was trained on 90-day counts and now reads decayed scores on a different scale, so feed quality drops overnight. The new model has no history to train on, and the A/B test is impossible because only one version exists. This is training-serving skew, and it fails silently.

A redefined signal needs live values for everyone, historical values for every past day the new model trains on, and both versions live at once. So treat `v2` as a new output:

- Backfill `v2` point-in-time from the fine-grained `interactions_daily` rollup, not raw events. About 10 TB instead of 36 TB, and decay lets one pass in day order emit all 60 `as_of` partitions. That works only because the rollup kept action type and day.
- Load `affinity:v1` and `affinity:v2` side by side in the online store, one row per viewer (about 180 GB per version).
- Ship by config: each ranker names its signal versions, and `v1` is retired only after the test.

Say what you won't rebuild: inboxes hold IDs only.

Covered in [Activity Feed](07-activity-feed.md).
</details>

### Q8. Credits only

Your ad platform invoiced October on November 2. On November 12 the invalid-traffic team flags 400,000 clicks across October and November. One campaign capped at $300 had $318 of valid clicks on November 4, so $18 was marked `over_budget`. After the $40 credit, someone suggests billing the $18 to fill the freed budget. What do you do?

<details>
<summary>Answer</summary>

Do not re-settle the day. That would send the advertiser a credit and a new charge for the same day, weeks later, for clicks they were told were free, and every IVT sweep would reopen every capped day it touched.

Post an `ivt_credit` row for each flagged billed click, in the current open period (November). October's invoice stays as issued, and November shows "credits for October activity". The $18 stays unbilled. The rule is that after settlement a day's charges can only go down. It costs little: if credits are 1 to 2% of spend and a third of campaigns hit their cap, the forgone re-billing is well under 1% of revenue. It never surprises a customer with a higher bill.

Follow-ons: mark the clicks `invalid` so the next attribution run drops the bot farm's "sales", and call advertisers whose credits exceed about 5% of last month's spend before the invoice.

Covered in [Ad Clickstream](08-ad-clickstream.md).
</details>

### Q9. A grain change

The bookings domain wants to change a hub data product from one row per booking to one row per room-night. 140 pipelines in 18 domains read it. A teammate suggests announcing the change date in a channel. Walk through what you'd actually build.

<details>
<summary>Answer</summary>

A grain change is breaking under every compatibility mode: the same column names now mean something different. Announcing a date means half the consumers miss it, and revenue silently doubles for multi-night stays.

Expand and contract is the right shape: publish `_v4` beside `_v3` and retire `_v3` later. Done by hand across 18 domains it means weeks of chasing, and on the date either `_v3` lives forever or some consumers break.

The senior answer makes it a platform workflow. CI posts the 140 consuming pipelines and owners on the pull request, from lineage. Both ports publish from one build, with `_v3` derived from `_v4` (grouped back to bookings), so bookings maintains one pipeline. Progress is measured by reads in query logs, not replies: done means zero reads for 14 days. The sunset date is enforced: tier 1 gets at least 90 days, reminders at days 60 and 80, then frozen, then retired. Extensions go to the governance group and are visible. The cost is double storage and compute for 90 days.

Covered in [Data Mesh Platform](09-data-mesh-platform.md).
</details>

### Q10. Six hours of backlog

A regional cellular outage ends after 6 hours and 300,000 refrigerated trucks reconnect in the same minute, each holding 2,160 buffered readings. Firmware retries on a fixed timer and uploads at full speed. What happens, and what do you change?

<details>
<summary>Answer</summary>

About 130 GB arrives (300,000 × 2,160 × 200 bytes). In 5 minutes that is roughly 430 MB/s on top of the normal 100 MB/s, plus 300,000 TLS handshakes in seconds. Brokers reject connections, rejected devices retry in lockstep, and when they get through, live readings queue behind six hours of backlog. Dashboards go stale exactly when operations needs to know if cargo is safe.

Backoff with jitter plus autoscaling gets connections through, but the backlog still shares the path with current readings.

The great answer separates old from new. On reconnect each device sends its current reading on the live topic first, then drains the backlog oldest-first at a throttled rate (say 2 readings a second: 18 minutes per truck, about 120 MB/s across the fleet, inside the 300 MB/s the log is sized for). The platform can change the cap over the open MQTT connection. The backlog topic has its own consumers and can fall 30 minutes behind without any dashboard noticing, and 4-day retention covers a consumer that is down for a day. Monitor backlog lag separately from live lag: in a storm, one rises while the other stays flat.

Covered in [IoT Sensor Pipeline](10-iot-sensor-pipeline.md).
</details>

### Q11. Late plays and fraud (multiple choice)

A music service's October statement went out on November 5. On November 20, a listener uploads 300 October plays after a month offline, and on October 20 the fraud team told you about 2 million September bot streams. Pro-rata means any change moves other rights holders' money. What is the right treatment?

- A. Reopen the closed month and reissue the statement
- B. Keep every month open for 30 days so nothing late arrives after close
- C. Give each ledger row a posting period (its play month if open, else the earliest open month), post late plays as adjustments and fraud as negative rows in the open period
- D. Overwrite the plays table and re-run the old statement

<details>
<summary>Answer</summary>

**C.** The 300 October plays keep `play_date` in October but post to November with a `late_adjustments` count. The bot streams become `fraud_reversal` rows with `quantity = -1` in the open period, with an anti-join so a fraud feed delivered twice reverses once. Closed statements never change, and the ledger shows exactly what happened and when. With the close on the 5th and 99.95% of plays arriving within 4 days, nearly every play lands on its own month's statement.

A makes October never final: with 50 million late streams a month, every upload shifts every rights holder's share after money was allocated. B is exact but makes statements a month later than the contract allows, and the tail of bad clocks still arrives after it. D destroys the audit trail.

Flag the pro-rata bend to the royalty team: a late play takes November's pool share, not October's. That is a policy choice, not yours to make silently.

Covered in [Music Streaming Analytics](01-music-streaming-analytics.md).
</details>

### Q12. Monday morning regression (multiple choice)

The embedding team retrains title embeddings every week. The morning after, every ranking model's engagement drops a few percent, with no errors anywhere. Which fix addresses the cause?

- A. Retrain all ranking models weekly, right after the embeddings
- B. Ship a bundle manifest naming the model, catalog snapshot ID, label version and every dependent feature view, compute dependent features per embedding version, and have serving load bundles
- C. Version the embedding snapshot and record the ID on each model
- D. Freeze the embeddings and retrain them once a year

<details>
<summary>Answer</summary>

**B.** An embedding only has meaning relative to the run that produced it, so retraining reshuffles the space and a model served new vectors is reading a language it never learned. Features built from embeddings, such as a profile's taste vector, inherit the problem. The profile feature is named per version (`profile_taste_e42`), and both `e41` and `e42` are materialized during the overlap. A new version goes live only when a model retrained on it is promoted together with its features. Lineage deletes old versions only when no live bundle references them.

C is the good-but-incomplete answer: it fixes the direct mismatch, but profile features computed against "the current" version can already be in the new space while the model is pinned to the old. A cannot be atomic across a fleet, and the old models are still being served meanwhile. D gives up freshness to avoid a process problem.

Covered in [Video Recommendations](02-video-recommendations.md).
</details>

### Q13. Same chart, wrong tenant (multiple choice)

A multi-tenant analytics platform has row-level security on every pooled table. A penetration test shows that two tenants opening the same prebuilt chart sometimes get each other's numbers. No table was queried wrongly. What is the fix?

- A. Add `WHERE tenant_id = ?` in the dashboard code
- B. Create a view per tenant and grant only those views
- C. Add more canary tenants and alert when they see each other
- D. Key the dashboard cache by tenant (and likewise query logs, error messages and support tooling), enforced by the query service

<details>
<summary>Answer</summary>

**D.** If the cache keys only on SQL text, the second tenant gets the first one's cached result. The leak never touches a table, so table-level controls cannot see it. The same applies to logs, error messages and support tools. Tenant identity should come from the authenticated session, which the user can't change, and be part of every cache key.

A and B protect the tables, which already work through RLS. A is also brittle (one forgotten filter) and useless for the SQL interface. B means tens of thousands of views and grants managed by automation that can have its own bug.

C is a detection layer, and a good one: canaries that try to read each other's markers through every interface, including the cache, run 1,440 times a day. But they report the leak, they don't close it.
Covered in [Multi-Tenant Platform](05-multi-tenant-platform.md).
</details>

### Q14. Sold out at 14:00 (multiple choice)

A store gets 55,000 recommendation requests a second, each with about 1,000 candidates, and must stop advertising a sold-out SKU within 30 seconds at p99. Which design fits?

- A. CDC from inventory into a stream job that emits a yes/no only when a SKU flips, onto a compacted topic every replica consumes into an in-memory bitmap
- B. Look up stock from the inventory service for every candidate at request time
- C. Filter out-of-stock items when the nightly lists and index are built
- D. Cache stock per replica for 10 minutes

<details>
<summary>Answer</summary>

**A.** Recommendations need one bit per SKU (in stock, listed, not blocked), not "how many left". 30 million bits is under 4 MB per replica, filtering 1,000 candidates is microseconds, and the compacted topic keeps only the latest value per SKU, so it is a complete current table. A replica restarts from a bitmap snapshot plus a replay from its topic offset. Use a safety threshold (unavailable below 5 units, not 0), because stock falls faster than any pipeline propagates. End-to-end is a few seconds. Say the trade-off: eventually right within seconds, and checkout still checks real stock.

B is 55 million reads a second against the system that reserves stock at checkout; on Black Friday it takes down order-taking. C leaves sold-out items recommended until tomorrow. D misses the 30-second requirement by an order of magnitude, and a flash sale's top 200 SKUs are the most recommended.

Covered in [Recommendation Engine](06-recommendation-engine.md).
</details>

### Q15. Hourly p95 (multiple choice)

Sensors write 5-minute summaries. Product now wants hourly p95 temperature. Which approach is right?

- A. Average the twelve 5-minute p95 values
- B. Take the maximum of the twelve 5-minute p95 values
- C. Store a small quantile sketch per bucket (a t-digest or KLL) and merge the twelve
- D. Keep only raw readings and never summarize

<details>
<summary>Answer</summary>

**C.** Percentiles are not mergeable: twelve 5-minute p95s don't make an hourly p95. A sketch of a few hundred bytes answers the question approximately and merges. The cost is real: at 1.44 billion 5-minute rows a day and 300 bytes each, it is about 430 GB a day, so add it only for metrics someone asked for.

A and B give wrong numbers that look plausible: an average of percentiles ignores how many readings each bucket held, and a max overstates the tail. D is correct but gives up the cheap summary tiers the design relies on, since 43 billion readings a day cannot sit in the fast store for years.

Covered in [IoT Sensor Pipeline](10-iot-sensor-pipeline.md).
</details>
