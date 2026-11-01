# Data Engineering System Design Course Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write the full 65-file DE system design course in markdown, plus README and glossary, with every file passing a clean-context review and humanizer pass.

**Architecture:** A small stdlib-Python checker (`tools/check_course.py`) is built first and acts as the "test suite": forbidden terms, external links, broken relative links, required headings per lesson type, quiz shape and Mermaid validity. Then lessons are written one task each, in an order that puts shared references (glossary, key numbers, the framework) before the lessons that lean on them. Every lesson task runs the same **Lesson Procedure** (below): write → check → clean-context review + `/humanizer` → re-check → commit.

**Tech Stack:** GitHub-flavored Markdown, Mermaid (validated with `@mermaid-js/mermaid-cli@11.4.0` via `npx`), Python 3 stdlib (`unittest`) for the checker.

**Spec:** `docs/superpowers/specs/2026-11-01-de-system-design-course-design.md` — every executor reads it in full before their task. Section numbers below (§) refer to it.

## Global Constraints

- No reference to the reference course, its company, site or author anywhere in the repo (§3.1). Check: `grep -rniE -f .forbidden-terms --exclude-dir=.git --exclude=.forbidden-terms .` prints nothing. If `.forbidden-terms` is missing, stop and ask the course owner.
- No outside sources: no courses, books, blogs, newsletters, talks, named people, or `http(s)://` links in course content. Product names are fine (§3.1).
- All text original. Hello Interview is the style model only and is never named in course content (§3.3). The ad clickstream breakdown must not retell their ad-click aggregator.
- Cloud-neutral: generic component first, mainstream options in passing (§3.4).
- Diagrams are ```` ```mermaid ```` blocks valid in GitHub's Mermaid; use a table/text sketch where Mermaid fits poorly (§3.5, §4).
- GitHub-flavored markdown only; callouts as `> [!TIP]`, `> [!WARNING]`, `> [!NOTE]`; quiz answers in `<details><summary>…</summary>…</details>` (§3.6, §4).
- Voice, clarity rules and length targets per §4: concept/framework/pattern 1,500–3,000 words; tech deep dives 2,000–3,500; breakdowns 3,500–6,000.
- Delivery framework order (§6 table) is the single source of truth; breakdowns use its steps as section headings.
- Assumed reader knowledge: SQL, basic batch vs streaming, "used it at work" level of Spark/Kafka/Airflow/a warehouse. Everything beyond is defined on first use.
- Numbers must agree with `02-core-concepts/10-key-de-numbers.md`; terms must agree with `GLOSSARY.md`.
- Repo tooling (my call): `tools/` holds only the checker and its tests; it is not course content and is not linked from the README.

## Review Focus

Failure modes the checker cannot catch, most likely first. Each is an explicit item in the reviewer checklist of the Lesson Procedure (step R2).

1. **Technical inaccuracy** (e.g. wrong Kafka transaction semantics, Iceberg/Delta feature claims out of date for 2026) — reviewer verifies every non-obvious technical claim and flags version-dependent ones.
2. **Overlap with already-written lessons** — reviewer reads the briefs of neighbouring lessons (Lesson Briefs table) and the linked lessons, and cuts content another lesson owns, replacing it with a link.
3. **Numbers that disagree with Key DE Numbers** — reviewer compares every throughput/latency/size/cost figure against `02-core-concepts/10-key-de-numbers.md`.
4. **Terms used before they're explained** — reviewer marks the first use of every non-assumed term and confirms it is defined there or linked.
5. **Humanizer flattening the voice or changing meaning** — reviewer diffs before/after the humanizer pass and reverts any edit that alters technical meaning, numbers, required headings, Mermaid, or `<details>` blocks, or that removes the interviewer's opinionated voice.

---

## Required headings (the checker enforces these, in this order, as `##` headings)

| Type | Applies to | Required `##` headings, in order |
|---|---|---|
| `concept` | Modules 01–03 lessons | `The Problem`, `In the Interview`, `Common Mistakes`, `Key Takeaways` |
| `tech` | Module 04 lessons | `When to Use It (and When Not To)`, `How It Works`, `Key Numbers`, `Interview Follow-ups`, `Alternatives`, `Key Takeaways` |
| `breakdown` | Modules 05–06 lessons | `Understanding the Problem`, `Requirements`, `Sources & Volume`, `High-Level Design`, `Data Model`, `Pipeline Design`, `Potential Deep Dives`, `Monitoring & SLAs`, `Final Design`, `What's Expected at Each Level`, `Related Lessons` |
| `quiz` | `*-quiz.md` | `Questions` |

Other `##`/`###` headings may appear between them. Additional rules:
- Every lesson starts with exactly one `#` H1 on line 1.
- `breakdown`: under `What's Expected at Each Level`, the `###` headings `Mid-level`, `Senior`, `Staff+` in that order. Bad/Good/Great options are `####` headings starting `Bad Solution:`, `Good Solution:`, `Great Solution:`.
- `concept`: lesson 1.02 (`02-delivery-framework.md`) must contain the §6 framework table (7 rows, same step names).
- `quiz`: 10–15 questions, each a `### Q<n>.` heading followed by exactly one `<details>` block.

---

## Task 1: Course checker

**Files:**
- Create: `tools/check_course.py`
- Create: `tools/tests/test_check_course.py`
- Create: `tools/tests/fixtures/` (minimal passing and failing markdown per lesson type)

**Interfaces:**
- Produces: CLI `python3 tools/check_course.py [--mermaid] [--allow-planned] [PATH ...]` — `--allow-planned` downgrades `BROKEN_LINK` to a `WARN` line when the missing target's repo-relative path matches `^0[1-6]-[a-z-]+/\d\d-[a-z0-9-]+\.md$` (a curriculum lesson not yet written). PATHs are files or dirs (default: whole repo excluding `docs/`, `tools/`, `.git`). Exit 0 if no errors; exit 1 and one line per error as `path:line: CODE message`. Word-count outside the §4 range prints `WARN` lines but does not fail.
- Produces: `lesson_type(path: Path) -> str | None` returning `"concept" | "tech" | "breakdown" | "quiz" | None` (README/GLOSSARY → `None`, which only get forbidden/link checks).
- Error codes: `FORBIDDEN`, `EXTERNAL_LINK`, `BROKEN_LINK`, `MISSING_H1`, `HEADINGS`, `LEVELS`, `QUIZ_COUNT`, `QUIZ_DETAILS`, `MERMAID`.

- [ ] **Step 1: Write failing tests** in `tools/tests/test_check_course.py` (unittest, each test builds files in a `tempfile.TemporaryDirectory` with its own `.forbidden-terms` containing `badterm`):
  - `test_forbidden_term_case_insensitive`: file containing `BadTerm` → `FORBIDDEN`.
  - `test_missing_forbidden_file_fails`: no `.forbidden-terms` → exit 1 with `FORBIDDEN` and message containing `.forbidden-terms missing`.
  - `test_external_link_rejected`: `[x](https://example.com)` → `EXTERNAL_LINK`.
  - `test_broken_relative_link`: `[x](../nope.md)` → `BROKEN_LINK`; an existing target (anchor stripped) passes.
  - `test_allow_planned_links`: link to missing `02-core-concepts/03-backfill-and-reprocessing.md` with `--allow-planned` → exit 0 with a `WARN`; link to missing `notes/x.md` with `--allow-planned` → still `BROKEN_LINK`.
  - `test_lesson_type_by_folder`: `01-the-framework/03-x.md`→`concept`, `04-technology-deep-dives/02-kafka.md`→`tech`, `06-breakdowns-advanced/01-x.md`→`breakdown`, `05-breakdowns-core/11-quiz.md`→`quiz`, `README.md`→`None`.
  - `test_breakdown_headings_order`: breakdown fixture with `Data Model` before `High-Level Design` → `HEADINGS`; correct fixture passes.
  - `test_breakdown_levels`: missing `### Staff+` → `LEVELS`.
  - `test_quiz_count_and_details`: 9 questions → `QUIZ_COUNT`; a `### Q3.` with no `<details>` → `QUIZ_DETAILS`; 12 well-formed → pass.
  - `test_mermaid_flag_reports_invalid` (skipped unless env `CHECK_MERMAID=1`): block `flowchart LR\n A -->` → `MERMAID`.
- [ ] **Step 2: Run tests, expect failures:** `python3 -m unittest discover -s tools/tests -v` → errors (module not found).
- [ ] **Step 3: Implement `tools/check_course.py`.** Link parsing via regex over `](...)` excluding code fences; heading checks are "required headings appear as a subsequence of the file's `##` headings". `--mermaid`: write each block to a temp `.mmd` and run `npx -y @mermaid-js/mermaid-cli@11.4.0 -i <f> -o <f>.svg -q`; non-zero exit → `MERMAID` with the block's starting line.
- [ ] **Step 4: Run tests, expect pass:** `python3 -m unittest discover -s tools/tests -v` → `OK`; then `CHECK_MERMAID=1 python3 -m unittest discover -s tools/tests -v` → `OK`.
- [ ] **Step 5: Commit** `git add tools && git commit -m "Add course checker"` (with the attribution line from the session reminder).

---

## Lesson Procedure (every task from Task 2 on)

Each content task names its file(s), its type, and its brief (Lesson Briefs below). The author (implementer subagent) does W1–W4; a **fresh reviewer subagent that did not write the lesson** does R1–R5; the controller does C1.

- [ ] **W1: Read** the spec in full, this task's brief, the briefs of the lessons before and after it in the table, `GLOSSARY.md`, `02-core-concepts/10-key-de-numbers.md` (once they exist), and every already-written lesson this one links to.
- [ ] **W2: Write** the file following the §6 template for its type, the Required Headings table, and §4 voice/clarity/length.
- [ ] **W3: Update `GLOSSARY.md`**: add any new course-wide term the lesson defines (one-line definition + link to the lesson); never redefine an existing term differently.
- [ ] **W4: Check:** `python3 tools/check_course.py --mermaid --allow-planned <file> GLOSSARY.md` → exit 0. Fix until it passes.
- [ ] **R1: Read** only the spec, the lesson, the files it links to, and the neighbouring briefs. Do not read the author's notes or conversation.
- [ ] **R2: Verify and fix in place** against §8 checks 1–5 and the five Review Focus items above. Record each change made and anything not fixable.
- [ ] **R3: Humanizer:** save a copy of the file to the scratchpad, invoke the `humanizer:humanizer` skill on the lesson, apply its suggestions to the file except any that would change technical meaning, numbers, required headings, Mermaid blocks, code, or `<details>` structure (note skipped ones).
- [ ] **R4: Diff** the saved copy against the result (`diff -u`): every Mermaid block and relative link must be unchanged; revert any edit that violates R3's exceptions.
- [ ] **R5: Re-check:** `python3 tools/check_course.py --mermaid --allow-planned <file> GLOSSARY.md` → exit 0, and `grep -rniE -f .forbidden-terms --exclude-dir=.git --exclude=.forbidden-terms .` prints nothing. Report: changes from R2, humanizer edits applied/skipped, check output.
- [ ] **C1: Commit** `git add <file> GLOSSARY.md && git commit -m "<Module N>: <lesson title>"` (with attribution line).

Quizzes use the same procedure; their W1 also reads every lesson in the module, and every answer links to the lesson that covers it.

---

## Task order

| Task | Files | Notes |
|---|---|---|
| 1 | `tools/…` | checker (above) |
| 2 | `GLOSSARY.md` | seed: ~25 core terms (event time, processing time, watermark, idempotent, exactly-once, at-least-once, partition, grain, SCD, CDC, backfill, late data, compaction, small-files problem, OLAP, object storage, table format, medallion layers, SLA/SLO, freshness, completeness, schema evolution, data contract, fan-out, hot partition). Type `None`; procedure applies (R2 checks definitions are correct and plain). |
| 3 | `02-core-concepts/10-key-de-numbers.md` | written early so every later lesson uses its numbers |
| 4–13 | Module 1 lessons 01–10 | in order |
| 14 | `01-the-framework/11-quiz.md` | |
| 15–23 | Module 2 lessons 01–09 | (10 already done in Task 3) |
| 24 | `02-core-concepts/11-quiz.md` | |
| 25–33 | Module 3 lessons 01–09 | |
| 34 | `03-architecture-patterns/10-quiz.md` | |
| 35–44 | Module 4 lessons 01–10 | |
| 45 | `04-technology-deep-dives/11-quiz.md` | |
| 46–55 | Module 5 breakdowns 01–10 | |
| 56 | `05-breakdowns-core/11-quiz.md` | |
| 57–66 | Module 6 breakdowns 01–10 | |
| 67 | `06-breakdowns-advanced/11-quiz.md` | |
| 68 | `README.md` | per §5 "Top level"; linked TOC of all 65 files + GLOSSARY; "short on time" path (my default: 1.02, 1.03, 1.10, 2.10, then 4 breakdowns: 5.01, 5.04, 5.05, 6.08). |
| 69 | Whole-course pass | see below |

Forward links: a lesson may link to a lesson not yet written only if it's a curriculum path in §5. W4 and R5 therefore run the checker with `--allow-planned`; Task 69 runs it without, so every link must resolve by the end.

### Task 69: Whole-course pass
- [ ] Run `python3 tools/check_course.py --mermaid` on the whole repo → exit 0 (no `BROKEN_LINK` allowed now).
- [ ] Run the forbidden-terms grep → no output.
- [ ] A fresh reviewer reads every module's first and last lesson plus all 20 breakdowns' "Related Lessons" sections and reports terminology drift, contradictions between lessons, and duplicated content; fixes are applied per Lesson Procedure R2–R5 on each touched file.
- [ ] Commit `git commit -am "Course-wide consistency pass"`.

---

## Lesson Briefs

Each brief says what the lesson **owns** (must cover) and, where overlap is likely, what it **leaves** to another lesson. Everything else is the author's call (§9).

### Module 1 — The Framework (`01-the-framework/`, type `concept`)
| # | File | Owns | Leaves to |
|---|---|---|---|
| 01 | `01-how-interviews-work.md` | What a DE design round is; how it differs from a SWE round (data correctness, freshness, cost, consumers over QPS/API); what's scored; common formats (whiteboard, take-home-style discussion, pipeline-whiteboarding); how levels change expectations | Step details → 1.02–1.09 |
| 02 | `02-delivery-framework.md` | The §6 7-step table with timings; why order matters; why data model follows architecture and when to flip; one mini end-to-end walk-through at outline depth | Each step's depth → 1.03–1.09 |
| 03 | `03-requirements-gathering.md` | Functional vs non-functional for data systems; quantified NFRs (freshness, completeness, correctness, retention, access patterns, cost); asking consumers' questions; "below the line" | Volume math → 1.04 |
| 04 | `04-sources-and-volume.md` | Source types (DBs, events, files, APIs, third-party); volume/velocity/growth estimates; only math that changes design; worked example | Number reference → 2.10 |
| 05 | `05-high-level-architecture.md` | Ingest → store → process → serve; numbered data flow; building the diagram per requirement; Bad/Good/Great used as a technique | Patterns → Module 3 |
| 06 | `06-data-model-design.md` | Modeling for consumers; grain; facts/dimensions; SCD types 1/2; wide/OBT vs star; partition/cluster keys at a glance | Partitioning depth → 2.01 |
| 07 | `07-pipeline-design.md` | Batch vs streaming per path; idempotency (overwrite partitions, MERGE, keys); dependencies and scheduling; retries, dead letters, failure modes | Backfill → 2.03; dedup → 2.09 |
| 08 | `08-deep-dives.md` | How to pick deep dives; the usual suspects (scale, correctness, late data, failure, cost); leading vs following; mid/senior/staff differences | — |
| 09 | `09-monitoring-and-slas.md` | Defining freshness/completeness/quality SLAs; presenting observability in the last minutes | Alert mechanics → 2.06 |
| 10 | `10-top-15-mistakes.md` | 15 mistakes, each: what it looks like, why it hurts, the fix, link to the lesson. Use `## Mistakes 1–5` etc. sections plus the required headings (`The Problem` = why candidates fail) | — |

### Module 2 — Core Concepts (`02-core-concepts/`, type `concept`)
| # | File | Owns | Leaves to |
|---|---|---|---|
| 01 | `01-partitioning.md` | Why partition; choosing keys (time, tenant, hash); pruning; small files and over-partitioning; hot partitions and salting; clustering/Z-order at concept level | Engine specifics → Module 4 |
| 02 | `02-ingestion-patterns.md` | Push vs pull; full vs incremental loads; watermark columns; event streams; files/SFTP; APIs with rate limits; choosing per source | CDC → 3.04 |
| 03 | `03-backfill-and-reprocessing.md` | Why backfills happen; idempotent design that makes them safe; partition-scoped reruns; replay from Kafka/raw; cost and isolation of big backfills | — |
| 04 | `04-data-lineage.md` | Table vs column lineage; how it's captured (parsing, OpenLineage-style events); uses: impact analysis, debugging, compliance; how deep to go in interviews | — |
| 05 | `05-cost-optimization.md` | Where money goes (compute, storage, scans, egress); file formats/compression; pruning; right-sizing; storage tiers; incremental over full | — |
| 06 | `06-monitoring-and-alerting.md` | What to measure (freshness, volume, schema, distribution, nulls); alert design and noise; anomaly detection basics; on-call runbooks | SLA definition → 1.09 |
| 07 | `07-data-contracts.md` | Producer/consumer contracts; schema registry; compatibility modes; enforcement points; breaking-change workflow | — |
| 08 | `08-late-arriving-data.md` | Event vs processing time; watermarks and allowed lateness; late dimensions in batch; correction strategies; a timeline as a table/text sketch | — |
| 09 | `09-deduplication-at-scale.md` | Sources of dupes; dedup keys; windowed vs global dedup; state size; exactly-once vs effectively-once; batch MERGE dedup | — |
| 10 | (Task 3) `10-key-de-numbers.md` | Tables of: disk/network/memory throughputs; Kafka partition throughput; object storage request latency; Spark executor sizing rules of thumb; compression ratios (Parquet vs JSON); events/day ↔ events/sec conversions; rough cloud costs labeled "order of magnitude, 2026"; how to use them in an estimate | — |

### Module 3 — Architecture Patterns (`03-architecture-patterns/`, type `concept`)
Each owns: problem, how it works (diagram), when to use, when not to, how it shows up in answers, follow-up questions.
| # | File | Notes |
|---|---|---|
| 01 | `01-lambda-architecture.md` | Speed + batch layers; reconciliation; why it fell out of favour and where it still fits |
| 02 | `02-kappa-architecture.md` | Everything as a stream; replay for reprocessing; limits (retention, reprocess cost) |
| 03 | `03-medallion-architecture.md` | Bronze/silver/gold; what belongs where; criticisms; it's a convention not a law |
| 04 | `04-cdc-patterns.md` | Log-based vs query-based vs trigger; snapshot + stream; ordering, deletes, schema change; outbox pattern | Tools → 4.09 |
| 05 | `05-event-sourcing.md` | Events as source of truth; projections; how it differs from CDC; where data teams meet it |
| 06 | `06-data-mesh.md` | Domain ownership, data as product, self-serve platform, federated governance; org prerequisites; when it's overkill |
| 07 | `07-data-fabric.md` | Metadata-driven integration; how it differs from mesh; why it's mostly vendor framing; how to discuss it honestly |
| 08 | `08-micro-batch-vs-streaming.md` | Latency/cost/complexity trade; Spark Structured Streaming vs Flink-style continuous; how to choose from the freshness NFR |
| 09 | `09-reverse-etl.md` | Warehouse → operational tools; sync semantics, rate limits, idempotency; when an operational DB or API is better |

### Module 4 — Technology Deep Dives (`04-technology-deep-dives/`, type `tech`)
| # | File | Probed internals |
|---|---|---|
| 01 | `01-spark-internals.md` | Driver/executors, DAG/stages/tasks, shuffles, partitions, skew and AQE, broadcast joins, memory/spill, caching |
| 02 | `02-kafka.md` | Topics/partitions/offsets, consumer groups, replication/ISR/acks, ordering, retention/compaction, idempotent producer and transactions, KRaft |
| 03 | `03-airflow.md` | Scheduler/executor/workers, DAGs vs tasks, idempotent tasks, backfill/catchup, sensors and deferrable operators, data-aware scheduling, what not to do in Airflow |
| 04 | `04-dbt.md` | Models/refs/DAG, materializations incl. incremental strategies, tests, snapshots (SCD2), where it fits and doesn't |
| 05 | `05-snowflake.md` | As "how a modern cloud warehouse works": storage/compute separation, micro-partitions and pruning, clustering, warehouses and concurrency, caching tiers, cost model; brief BigQuery/Redshift/Databricks SQL differences |
| 06 | `06-delta-lake.md` | Transaction log, ACID on object storage, MERGE, time travel, OPTIMIZE/Z-order/liquid clustering, VACUUM, CDF |
| 07 | `07-iceberg.md` | Metadata tree (metadata/manifest lists/manifests), hidden partitioning and partition evolution, snapshots, catalogs (REST), engine neutrality; Delta vs Iceberg vs Hudi comparison owned here |
| 08 | `08-flink.md` | Streams, keyed state, event time and watermarks, windows, checkpoints/savepoints, exactly-once sinks, backpressure |
| 09 | `09-debezium-and-cdc-tools.md` | Debezium on Kafka Connect, snapshotting, schema history, managed CDC alternatives; failure modes (slot bloat, schema change) |
| 10 | `10-orchestrator-comparison.md` | Airflow vs Dagster vs Prefect vs managed (MWAA/Composer-style, cloud-native workflows); task- vs asset-centric; how to choose in an interview |

### Module 5 — Breakdowns: Core (`05-breakdowns-core/`, type `breakdown`)
The "central tension" keeps each breakdown distinct; the author picks the scale numbers and deep dives (§9).
| # | File | Prompt | Central tension |
|---|---|---|---|
| 01 | `01-log-aggregation.md` | Collect app/infra logs from thousands of services for search and analytics | Ingest volume and cost vs retention and search latency (hot/warm/cold) |
| 02 | `02-url-shortener-analytics.md` | Click analytics for a URL shortener | Simple high-volume counting, top-K and unique visitors; approximate (HLL) vs exact |
| 03 | `03-e-commerce-warehouse.md` | Analytics warehouse for an online store | Dimensional model, SCD2, late orders/returns; the model is the design (framework flex from 1.02) |
| 04 | `04-real-time-dashboard.md` | Live operational metrics dashboard | Seconds-level freshness; pre-aggregation vs real-time OLAP; serving layer |
| 05 | `05-cdc-replication.md` | Replicate OLTP databases into the lake/warehouse | Correct ordering, deletes, schema change, initial snapshot at scale |
| 06 | `06-medallion-data-lake.md` | Build a company data lake from many sources | Layer design, table format, governance, small files |
| 07 | `07-etl-framework.md` | A config-driven framework other teams use to ship pipelines | Platform abstraction, multi-team ownership, testing, retries |
| 08 | `08-feature-store.md` | Feature store for ML | Offline/online consistency, point-in-time correctness, serving latency |
| 09 | `09-data-quality-monitoring.md` | DQ monitoring platform across hundreds of tables | Check types, scale of checks, alert noise, blocking vs warning |
| 10 | `10-surge-pricing.md` | Ride-hailing surge pricing data pipeline | Geo-bucketing, sub-minute supply/demand aggregation, feeding a pricing service |

### Module 6 — Breakdowns: Advanced (`06-breakdowns-advanced/`, type `breakdown`)
| # | File | Prompt | Central tension |
|---|---|---|---|
| 01 | `01-music-streaming-analytics.md` | Listening analytics and royalty counts for a music service | Billing-grade play counts, artist dashboards, massive event volume |
| 02 | `02-video-recommendations.md` | Data platform behind video recommendations | Viewing events → training data at huge catalog; offline/online consistency (not serving freshness — see 6.06) |
| 03 | `03-fraud-detection.md` | Real-time payment fraud detection data pipeline | Millisecond feature computation, stateful streaming, feedback labels |
| 04 | `04-social-media-analytics.md` | Engagement analytics for a social network | Fan-out of counts, trending topics, celebrity hot keys |
| 05 | `05-multi-tenant-platform.md` | Analytics platform serving many customers | Isolation, noisy neighbours, per-tenant cost and access control |
| 06 | `06-recommendation-engine.md` | E-commerce recommendations kept fresh | Near-real-time signals, candidate generation inputs, feature serving at request time (not the training platform — see 6.02) |
| 07 | `07-activity-feed.md` | Activity feed data pipeline for a professional network | Event fan-out, ranking signals, backfills when ranking changes |
| 08 | `08-ad-clickstream.md` | Ad impression/click pipeline for billing and attribution | Impression–click joins, attribution windows, exactly-once billing counts, reconciliation (original design; not a retelling of any public breakdown) |
| 09 | `09-data-mesh-platform.md` | Platform that lets domains publish data products | Self-serve infra, contracts, discovery, federated governance in practice |
| 10 | `10-iot-sensor-pipeline.md` | Ingest and analyse readings from millions of devices | Out-of-order/late data, intermittent connectivity, time-series storage and downsampling |

---

## Execution notes
- Tasks are sequential (later lessons link to and build on earlier ones). Do not parallelize lesson tasks.
- The implementer of a lesson and its reviewer must be different, fresh subagents (spec §8 pipeline).
- `npx` downloads mermaid-cli (with a headless Chromium) on first use; if that fails in the environment, stop and report rather than skipping Mermaid validation.
