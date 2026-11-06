# Data Engineering System Design

A self-study course for the data engineering system design interview: the 45 to 60 minute round where you get a vague prompt and have to design a data system out loud, defend your choices, and survive the follow-up questions.

**Start reading at the [course home](course/index.md).** It explains who the course is for, how to use it, and lists every lesson.

## What Is in This Repo

| Path | What it holds |
| --- | --- |
| `course/` | The course itself: the six modules, their quizzes and the glossary. `course/index.md` is the home page. |
| `tools/` | `check_course.py`, which checks lesson structure, links and the site sidebar, plus its tests. |
| `docs/` | Planning notes from when the course was written. Not part of the course. |
| `zensical.toml` | Config for the website version of the course. |
| `pyproject.toml` | Python dependencies, managed with uv. |

## Reading It as a Website

The course reads fine on GitHub as plain markdown. To read it as a website with search, a sidebar and dark mode, install [uv](https://docs.astral.sh/uv/) and run this from the repo root:

```bash
uv run zensical serve
```

Then open <http://localhost:8000>. The page reloads as you edit lessons. To build static HTML into `site/` instead:

```bash
uv run zensical build
```

## Checking the Course

Run the checker after editing any lesson. It must print no errors (word-count warnings are fine):

```bash
uv run tools/check_course.py
```

Run the checker's own tests:

```bash
uv run python -m unittest discover -s tools/tests
```

## Writing Lessons

Lessons are plain GitHub-flavored markdown, with three conventions so they also render on the site:

- Callouts use GitHub syntax: `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`.
- Hidden quiz answers use `<details markdown="1">`. Without `markdown="1"` the site shows the answer's markdown as raw text, and the checker flags it.
- Diagrams use ```` ```mermaid ```` code blocks.

A new lesson must also be added to the `nav` list in `zensical.toml` and to the module's `index.md`. The checker reports any page missing from the sidebar.
