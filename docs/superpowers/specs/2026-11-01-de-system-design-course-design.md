# Data Engineering System Design Course — Design

**Date:** 2026-11-01
**Status:** Draft for review

## 1. Intent

A complete, self-study course that prepares working data engineers for the **data engineering system design interview**. The deliverable is course content only: a set of markdown files. There is no website, app, or build tooling for now.

**Readers:** data engineers with roughly 1–4 years of experience (junior to mid-level). They already use SQL and have touched Spark, Kafka, Airflow and a cloud warehouse, but haven't had to design a large data system end to end in front of an interviewer.

**Success:** after finishing, a reader can take an open-ended prompt ("design a clickstream analytics pipeline"), run the conversation with a clear structure, make choices they can defend with trade-offs and numbers, and handle deep-dive follow-up questions.

## 2. Goals, non-goals, anti-goals

**Goals**
- Cover the full curriculum in Section 5: 6 modules, 65 files: 59 lessons (20 of them problem breakdowns) plus 6 module quizzes. The exact list is below.
- Every lesson is clear to the target reader on a first read.
- Teach through an interviewer's eyes: what gets asked, what a strong answer sounds like, what sinks candidates.

**Non-goals**
- Not a tool manual or a hands-on tutorial. No setup steps, no runnable projects.
- Not exhaustive coverage of every concept. Interview relevance decides what goes in.
- No website, styling, navigation UI, or publishing pipeline (may come later; not part of this work).

**Anti-goals (failure even if every file exists)**
- A reader doesn't understand a lesson.
- Information overload: a lesson that dumps everything true about a topic.
- Things named but not explained: jargon, tool names or patterns used without the "what" and "why".

## 3. Hard constraints

1. **No reference, in any form, to the course whose structure this follows, its company, its website, or its author.** This applies to lesson text, file names, folder names, front matter, README, credits, comments, and this repo's docs. The structure in Section 5 is described here without attribution on purpose. The list of forbidden names lives in **`.forbidden-terms`** at the repo root, one case-insensitive regex per line. That file is listed in `.gitignore`, so it exists in the working folder but is never committed. The constraint check in Section 8 is:

   ```bash
   grep -rniE -f .forbidden-terms --exclude-dir=.git --exclude=.forbidden-terms .
   ```

   It must print nothing. If `.forbidden-terms` is missing (e.g. a fresh clone), stop and get the list from the course owner before writing or reviewing anything.
   - *(My call:)* to make this airtight, **the course cites no outside sources at all**: no courses, books, blogs, newsletters, talks or named people, and no "Going further" links to external sites. Vendor and open-source product names (Kafka, Snowflake, Debezium…) are fine, used as technology names.
2. **All content is original.** Only the curriculum's shape (module and lesson topics and their order) was taken from the reference outline. No text, examples or diagrams were copied, because only titles were seen.
3. **Style model: Hello Interview's system design course** (voice and explanation patterns, see Section 4). Copy its *approach*, never its text or examples. In particular, the ad-click aggregator breakdown must be our own design and narrative, not a retelling of theirs. *(My call:)* course content does not name Hello Interview either; the style reference lives only in this spec.
4. **Cloud-neutral.** Name generic components first ("object storage", "a managed Kafka service", "a cloud warehouse") and give mainstream options in passing, e.g. "managed Kafka (MSK, Confluent Cloud, Event Hubs)". No lesson assumes one cloud.
5. **Diagrams in Mermaid**, embedded as ```` ```mermaid ```` blocks. They must render on GitHub (use only syntax GitHub's Mermaid supports).
6. **Markdown only.** GitHub-flavored markdown. Collapsible answers use `<details><summary>…</summary>…</details>`, which GitHub renders.

## 4. Voice and explanation style

**Voice.** Talk to the reader as an experienced interviewer who's on their side: second person, direct, opinionated, occasionally wry. Say what interviewers actually care about and push back on textbook answers when they don't fit ("you might reach for checkpointing here, but with 1-minute windows, do you need it?"). No marketing tone, no filler, no hype.

**Clarity rules (these enforce the anti-goals):**
- **Why before what.** Open each concept with the problem it solves, in a concrete situation, before naming it.
- **Define on first use.** Every term beyond the reader's assumed knowledge is defined in a sentence the first time it appears in a lesson. Assumed knowledge: SQL, basic batch vs streaming, what Spark/Kafka/Airflow/a warehouse are at a "used it at work" level.
- **One concrete example per idea**, with real-feeling numbers (e.g. "50k events/sec, ~1 KB each, ≈ 4 TB/day").
- **Fewer ideas, explained properly.** If a subtopic doesn't help in an interview, cut it. A short "Going further" list at the end can name, without explaining, at most 3 things that were left out.
- **Short paragraphs, scannable structure.** Headings every few paragraphs, tables for comparisons, bullets for lists. No wall of text.
- **Callouts** as GitHub blockquote alerts: `> [!TIP]` for interviewer tips, `> [!WARNING]` for common mistakes, `> [!NOTE]` for asides.

**Length targets.** Concept, framework and pattern lessons: 1,500–3,000 words (about 10–20 minutes). Technology deep dives: 2,000–3,500 words. Breakdowns: 3,500–6,000 words, in clearly separated steps. These are guides. Clarity wins over the word count either way.

**Diagrams.** 1–4 per lesson where they explain something. Typical uses: flowcharts (`flowchart LR`) with subgraphs for architectures and pipelines, `sequenceDiagram` for step-by-step flows (CDC, backfills, exactly-once), `erDiagram` for data models. Where Mermaid is a poor fit (e.g. event-time vs processing-time timelines), use a small table or a text sketch instead. In breakdowns, the architecture diagram grows step by step: each section shows the diagram at that point.

## 5. Curriculum

Folder per module, numbered files, kebab-case names.

### Module 1 — The Framework (`01-the-framework/`)
1. `01-how-interviews-work.md` — what a DE system design round is, how it differs from a SWE round, what's being scored, formats and timing
2. `02-delivery-framework.md` — the step-by-step structure with suggested minutes per step; the backbone every breakdown follows
3. `03-requirements-gathering.md` — functional vs non-functional for data systems (freshness, completeness, correctness, retention, access patterns), scoping and "below the line"
4. `04-sources-and-volume.md` — identifying sources and estimating volume, velocity and growth; doing only the math that changes the design
5. `05-high-level-architecture.md` — drawing the end-to-end flow: ingest, store, process, serve
6. `06-data-model-design.md` — modeling for the consumers: dimensional modeling, grain, SCDs, wide tables, when to normalize
7. `07-pipeline-design.md` — batch vs streaming choice, idempotency, scheduling and dependencies, failure handling
8. `08-deep-dives.md` — picking and running deep dives: what interviewers probe and how to lead it
9. `09-monitoring-and-slas.md` — freshness/completeness/quality SLAs, how to present observability in an interview
10. `10-top-15-mistakes.md` — the 15 most common ways candidates fail, each with the fix
11. `11-quiz.md`

### Module 2 — Core Concepts (`02-core-concepts/`)
1. `01-partitioning.md`
2. `02-ingestion-patterns.md`
3. `03-backfill-and-reprocessing.md`
4. `04-data-lineage.md`
5. `05-cost-optimization.md`
6. `06-monitoring-and-alerting.md`
7. `07-data-contracts.md`
8. `08-late-arriving-data.md`
9. `09-deduplication-at-scale.md`
10. `10-key-de-numbers.md` — reference numbers worth memorizing (throughputs, latencies, storage sizes, compression ratios, rough costs) with how to use them in estimates
11. `11-quiz.md`

*Overlap rule:* Module 1's `09-monitoring-and-slas` is about defining SLAs and presenting them in an interview. Module 2's `06-monitoring-and-alerting` is about the mechanics: what to measure, alert design, anomaly detection, on-call noise. Cross-link rather than repeat.

### Module 3 — Architecture Patterns (`03-architecture-patterns/`)
1. `01-lambda-architecture.md`
2. `02-kappa-architecture.md`
3. `03-medallion-architecture.md`
4. `04-cdc-patterns.md`
5. `05-event-sourcing.md`
6. `06-data-mesh.md`
7. `07-data-fabric.md`
8. `08-micro-batch-vs-streaming.md`
9. `09-reverse-etl.md`
10. `10-quiz.md`

Each pattern lesson covers: the problem it solves, how it works (diagram), when to use it, when not to, how it shows up in interview answers, and the follow-up questions to expect.

### Module 4 — Technology Deep Dives (`04-technology-deep-dives/`)
1. `01-spark-internals.md`
2. `02-kafka.md`
3. `03-airflow.md`
4. `04-dbt.md`
5. `05-snowflake.md`
6. `06-delta-lake.md`
7. `07-iceberg.md`
8. `08-flink.md`
9. `09-debezium-and-cdc-tools.md`
10. `10-orchestrator-comparison.md` — Airflow vs Dagster vs Prefect vs managed options, and how to choose in an interview
11. `11-quiz.md`

Each covers only what interviews test: when to choose it and when not to, how it works internally to the depth that gets probed, key numbers and limits, and the follow-up questions interviewers like. *Snowflake* is the one vendor-specific lesson. Frame it as "how a modern cloud warehouse works, with Snowflake as the example" and note where BigQuery/Redshift/Databricks SQL differ, to stay consistent with cloud neutrality.

### Module 5 — Question Breakdowns: Core (`05-breakdowns-core/`)
1. `01-log-aggregation.md`
2. `02-url-shortener-analytics.md`
3. `03-e-commerce-warehouse.md`
4. `04-real-time-dashboard.md`
5. `05-cdc-replication.md`
6. `06-medallion-data-lake.md`
7. `07-etl-framework.md`
8. `08-feature-store.md`
9. `09-data-quality-monitoring.md`
10. `10-surge-pricing.md` — ride-hailing surge pricing (Uber-style)
11. `11-quiz.md`

### Module 6 — Question Breakdowns: Advanced (`06-breakdowns-advanced/`)
1. `01-music-streaming-analytics.md` — Spotify-style
2. `02-video-recommendations.md` — Netflix-style recommendations data platform
3. `03-fraud-detection.md`
4. `04-social-media-analytics.md` — Twitter/X-style
5. `05-multi-tenant-platform.md`
6. `06-recommendation-engine.md`
7. `07-activity-feed.md` — LinkedIn-style
8. `08-ad-clickstream.md`
9. `09-data-mesh-platform.md`
10. `10-iot-sensor-pipeline.md`
11. `11-quiz.md`

*Naming (my call):* lesson titles may say "Design Spotify Analytics" the way interview prompts do. Real company names are used only as the well-known framing of the prompt, never to claim how that company actually built it.

*Overlap to manage:* `02-video-recommendations` and `06-recommendation-engine` must not be the same lesson twice. Video recommendations focuses on the **data platform behind recommendations** (viewing events, batch training data, offline/online consistency at a huge catalog). The recommendation engine focuses on **serving-time freshness**: near-real-time signals, candidate generation and feature serving for something like e-commerce. Likewise `08-ad-clickstream` vs `02-url-shortener-analytics` (click counting). Ad clickstream centers on attribution, impression-click joins, exactly-once billing-grade counts and reconciliation.

### Top level
- `README.md` — what the course is, who it's for, the assumed knowledge, how to use it (suggested order and a "short on time" path), and the full linked table of contents.

## 6. Templates

### Concept, framework and pattern lessons
1. Title and a 1–2 sentence "why this matters in an interview" lead
2. The problem (concrete scenario)
3. The core idea(s), explained with an example and diagram
4. Options and trade-offs (a table where options compete)
5. How to bring this up in an interview: phrases, timing, what interviewers listen for
6. Common mistakes (`> [!WARNING]`)
7. Key takeaways (3–5 bullets)
8. Optional "Going further" (≤ 3 topics named, not linked to outside sources) and links to related lessons

### Technology deep dives
1. What it is, and the one-line reason it shows up in designs
2. When to pick it / when not to
3. How it works: architecture diagram and the internals that get probed
4. Key numbers and limits
5. Common interview follow-ups with short model answers
6. Alternatives and how to compare them
7. Key takeaways

### The delivery framework (single source of truth)
*(My call.)* Module 1 lesson 02 teaches this order, lessons 03–09 teach one step each, and every breakdown uses the same steps as its section headings, so the framework and the examples never disagree:

| # | Step | Taught in | Rough time (45–60 min round) |
|---|------|-----------|------------------------------|
| 1 | Requirements (functional, non-functional, below the line) | 1.03 | ~5–8 min |
| 2 | Sources & volume (inputs, outputs, only the estimates that change the design) | 1.04 | ~3–5 min |
| 3 | High-level architecture (data flow, then boxes and arrows built per requirement) | 1.05 | ~10–15 min |
| 4 | Data model (tables/topics, grain, partitioning, built for the consumers) | 1.06 | ~5 min |
| 5 | Pipeline design (batch vs streaming per path, idempotency, scheduling, failure handling) | 1.07 | ~5–8 min |
| 6 | Deep dives | 1.08 | ~10–15 min |
| 7 | Monitoring & SLAs (how you'd know it's healthy and on time) | 1.09 | ~3–5 min |

Data model comes after the high-level architecture on purpose: in data systems you model the layers (raw, cleaned, serving) once you know they exist. Lesson 02 explains this and says when to flex (e.g. a warehouse-design prompt where the model *is* the design and comes earlier).

### Breakdowns (all 20)
0. **Understanding the Problem** — what the system is, in plain terms
1. **Requirements** — functional (2–4 core items) and non-functional (scale numbers first, then 3–5 quantified qualities: freshness, correctness, durability, query latency, cost), each with **Below the line (out of scope)**
2. **Sources & volume** — inputs and outputs, and only the numbers that change the design, worked inline
3. **High-level design** — numbered data flow, then built one requirement at a time. For each key decision, present **Bad → Good → Great** solutions (2–3 options, not all decisions need all three), each with how it works, why it falls short or succeeds, and an updated diagram
4. **Data model** — key tables/topics, grain, partitioning (an `erDiagram` where useful)
5. **Pipeline design** — batch vs streaming per path, idempotency, scheduling/dependencies, failure and retry behavior. Kept short where the high-level design already settled it
6. **Potential deep dives** — 3–5, each framed as the interviewer's question ("How do you make sure no event is counted twice after a replay?"), again with option ladders where it helps
7. **Monitoring & SLAs** — the few SLAs and checks that matter for this system
8. **Final design** — the complete diagram and a short walkthrough
9. **What's expected at each level** — **Mid-level**, **Senior**, **Staff+**: breadth vs depth, who drives, and a concrete bar for *this* problem at each level
10. Links to the concept, pattern and technology lessons used

### Quizzes
- 10–15 questions per module quiz, about two thirds short interview-style scenarios and one third multiple choice.
- Each answer is in a `<details>` block: the answer, why it's right, and why the tempting wrong answer is wrong. Link to the lesson that covers it.

## 7. Cross-cutting rules
- Relative links between lessons (`../02-core-concepts/09-deduplication-at-scale.md`). Every breakdown links back to the concepts it uses; concept lessons link forward to one or two breakdowns where they matter.
- Consistent terminology across the course (e.g. "object storage", "event time", "processing time", "watermark", "idempotent") with the same definitions everywhere. *(My call:)* keep a short `GLOSSARY.md` at the root so terms stay consistent; lessons still define terms inline.
- Numbers must be realistic and consistent with `10-key-de-numbers.md`.
- Technical accuracy matters: claims about Kafka, Spark, Flink, Iceberg, etc. must be correct as of 2026. When a behavior is version-dependent, say so briefly.

## 8. Quality bar per lesson
Before a lesson counts as done, it must pass:
1. **Clarity read:** a reader at the target level could follow it top to bottom without looking anything up.
2. **Overload check:** each section earns its place. Cut anything that isn't needed for the interview.
3. **Explained, not named:** every term, tool and pattern used is explained or linked to a lesson that explains it.
4. **Template followed** for its lesson type, and all Mermaid blocks are valid syntax.
5. **Constraint check:** no mention of the reference course, its company, site or author; no copied text from any source; cloud-neutral.

### Per-lesson review pipeline (required for every lesson and quiz)
A lesson is not done when it's written. It's done when it has passed through these steps, in this order:

1. **Write:** the author drafts the lesson.
2. **Clean-context verification:** a **fresh agent that did not write the lesson and has no memory of drafting it** (a new subagent given only this spec, the lesson file, and the files the lesson links to) checks the lesson against the quality bar above (checks 1–5) and the template for its type. It also checks technical accuracy. It **applies the fixes directly** to the lesson, then reports what it changed and anything it couldn't fix.
3. **Humanizer pass:** the same clean-context agent (still not the author) runs the `/humanizer` skill on the lesson and **applies the suggested changes** to the file. Humanizer edits must not change technical meaning, numbers, Mermaid blocks, code, headings required by the template, or `<details>` structure. If a suggestion would, skip it and note it.
4. **Final mechanical check:** after the humanizer edits, re-run the forbidden-terms check from Section 3 (zero hits required) and confirm every Mermaid block and relative link still matches what it was before step 3.

The point of the clean context is that the reviewer reads the lesson the way a learner would, without the author's assumptions filling in gaps. The author does not review their own lesson.

## 9. Left to the builder
- Exact wording, examples, scenarios and numbers within each lesson.
- Exact quiz questions.
- Which deep dives each breakdown picks (3–5), and which decisions get a Bad/Good/Great ladder.
- The order lessons are written in, and how lessons are batched, as long as every lesson goes through the Section 8 review pipeline.
- README wording and the "short on time" path.
