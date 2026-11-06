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

## Modules

Each module page lists its lessons. Terms are collected in the [Glossary](GLOSSARY.md).

<div class="grid cards" markdown="1">

- **[Module 1: The Framework](01-the-framework/index.md)**

    The structure of the round and the seven steps you follow in it.

    10 lessons and a quiz

- **[Module 2: Core Concepts](02-core-concepts/index.md)**

    The ideas that come up inside almost every design.

    10 lessons and a quiz

- **[Module 3: Architecture Patterns](03-architecture-patterns/index.md)**

    Named ways to put a data platform together, and when each one fits.

    9 lessons and a quiz

- **[Module 4: Technology Deep Dives](04-technology-deep-dives/index.md)**

    How the common tools work, to the depth interviewers probe.

    10 lessons and a quiz

- **[Module 5: Question Breakdowns, Core](05-breakdowns-core/index.md)**

    Ten full worked designs of classic prompts.

    10 lessons and a quiz

- **[Module 6: Question Breakdowns, Advanced](06-breakdowns-advanced/index.md)**

    Ten harder prompts with more moving parts.

    10 lessons and a quiz

</div>
