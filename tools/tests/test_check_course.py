import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
CHECKER = HERE.parent / "check_course.py"
sys.path.insert(0, str(HERE.parent))
from check_course import Report, check_home_cards, check_nav, lesson_type  # noqa: E402


def quiz_text(n, details_for=None):
    details_for = range(1, n + 1) if details_for is None else details_for
    out = ["# Quiz", "", "## Questions", ""]
    for i in range(1, n + 1):
        out += [f"### Q{i}.", "", "Question text?", ""]
        if i in details_for:
            out += ['<details markdown="1">', "<summary>Answer</summary>", "", "Because.", "", "</details>", ""]
    return "\n".join(out)


class CheckerCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.root = Path(self._td.name)
        (self.root / ".forbidden-terms").write_text("badterm\n")

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def copy_fixture(self, name, rel):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIXTURES / name, p)
        return p

    def run_check(self, *args, paths=None):
        cmd = [sys.executable, str(CHECKER), "--root", str(self.root), *args]
        cmd += [str(p) for p in (paths or [])]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_forbidden_term_case_insensitive(self):
        p = self.write("README.md", "# T\n\nhas BadTerm in it\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN", out)
        self.assertIn("README.md:3:", out)

    def test_missing_forbidden_file_fails(self):
        (self.root / ".forbidden-terms").unlink()
        p = self.write("README.md", "# T\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN", out)
        self.assertIn(".forbidden-terms missing", out)

    def test_clean_file_passes(self):
        p = self.write("README.md", "# T\n\nfine\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual((code, out), (0, ""))

    def test_external_link_rejected(self):
        p = self.write("README.md", "# T\n\n[x](https://example.com)\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("EXTERNAL_LINK", out)

    def test_links_in_code_fences_ignored_and_images_checked(self):
        p = self.write("README.md", "# T\n\n```\n[x](https://example.com)\n```\n\n![a](nope.png)\n[a](#top) [m](mailto:a@b.c)\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertNotIn("EXTERNAL_LINK", out)
        self.assertIn("README.md:7: BROKEN_LINK", out)

    def test_broken_relative_link(self):
        p = self.write("a/x.md", "# T\n\n[x](../nope.md)\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("BROKEN_LINK", out)

    def test_existing_link_with_anchor_passes(self):
        self.write("other.md", "# O\n")
        p = self.write("a/x.md", "# T\n\n[x](../other.md#section)\n")
        code, out = self.run_check(paths=[p])
        self.assertEqual((code, out), (0, ""))

    def test_details_without_markdown_attribute_rejected(self):
        p = self.write("a/x.md", '# T\n\n<details>\n<summary>A</summary>\n\nB\n</details>\n\n<details markdown="1">\n</details>\n')
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("a/x.md:3: DETAILS_MARKDOWN", out)
        self.assertNotIn("a/x.md:9:", out)

    def test_nav_must_match_course_pages(self):
        self.write("index.md", "# H\n")
        self.write("01-the-framework/01-a.md", "# A\n")
        self.write("01-the-framework/02-b.md", "# B\n")
        cfg = self.write("zensical.toml", '[project]\nnav = [\n  { "Home" = "index.md" },\n'
                         '  { "M1" = ["01-the-framework/01-a.md", { "Gone" = "01-the-framework/09-gone.md" }] },\n]\n')
        report = Report()
        check_nav(cfg, self.root, report)
        out = "\n".join(report.lines)
        self.assertEqual(report.errors, 2)
        self.assertIn("page missing from the sidebar nav: 01-the-framework/02-b.md", out)
        self.assertIn("nav entry points to a missing page: 01-the-framework/09-gone.md", out)

    def home_card_course(self, card_desc="The ideas.", card_count="2 lessons and a quiz", extra=""):
        self.write("01-the-framework/index.md", "# Module 1: Framework\n\nThe ideas.\n\n## Lessons\n\n"
                   "1. [A](01-a.md)\n2. [B](02-b.md)\n3. [Quiz](03-quiz.md)\n")
        self.write("index.md", '# H\n\n<div class="grid cards" markdown="1">\n\n'
                   f"- **[Module 1: Framework](01-the-framework/index.md)**\n\n    {card_desc}\n\n    {card_count}\n{extra}\n</div>\n")
        report = Report()
        check_home_cards(self.root, report)
        return report

    def test_home_cards_match_module_index(self):
        report = self.home_card_course()
        self.assertEqual((report.errors, report.lines), (0, []))

    def test_home_card_drift_reported(self):
        report = self.home_card_course(card_desc="Old words.", card_count="3 lessons and a quiz")
        out = "\n".join(report.lines)
        self.assertEqual(report.errors, 2)
        self.assertIn("card description 'Old words.'", out)
        self.assertIn("card lesson count '3 lessons and a quiz'", out)

    def test_home_cards_missing_and_dangling(self):
        self.write("02-core-concepts/index.md", "# Module 2: Core\n\nMore.\n")
        report = self.home_card_course(extra="\n- **[Module 9: Gone](06-breakdowns-advanced/index.md)**\n\n    X\n\n    0 lessons and a quiz\n")
        out = "\n".join(report.lines)
        self.assertEqual(report.errors, 2)
        self.assertIn("no home page card for module 02-core-concepts", out)
        self.assertIn("card points to a missing module: 06-breakdowns-advanced", out)

    def test_allow_planned_links(self):
        p = self.write("README.md", "# T\n\n[x](02-core-concepts/03-backfill-and-reprocessing.md)\n")
        code, out = self.run_check("--allow-planned", paths=[p])
        self.assertEqual(code, 0)
        self.assertIn("WARN", out)
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("BROKEN_LINK", out)
        q = self.write("README.md", "# T\n\n[x](notes/x.md)\n")
        code, out = self.run_check("--allow-planned", paths=[q])
        self.assertEqual(code, 1)
        self.assertIn("BROKEN_LINK", out)

    def test_lesson_type_by_folder(self):
        cases = {
            "01-the-framework/03-x.md": "concept",
            "04-technology-deep-dives/02-kafka.md": "tech",
            "06-breakdowns-advanced/01-x.md": "breakdown",
            "05-breakdowns-core/11-quiz.md": "quiz",
            "README.md": None,
            "01-the-framework/index.md": None,
            "GLOSSARY.md": None,
        }
        for rel, want in cases.items():
            self.assertEqual(lesson_type(Path(rel)), want, rel)

    def test_missing_h1(self):
        p = self.write("01-the-framework/03-x.md", "intro\n\n## The Problem\n")
        code, out = self.run_check(paths=[p])
        self.assertIn("MISSING_H1", out)

    def test_concept_headings(self):
        good = self.copy_fixture("concept_good.md", "01-the-framework/03-x.md")
        self.assertEqual(self.run_check(paths=[good])[0], 0)
        bad = self.copy_fixture("concept_missing_heading.md", "01-the-framework/04-y.md")
        code, out = self.run_check(paths=[bad])
        self.assertEqual(code, 1)
        self.assertIn("HEADINGS", out)

    def test_tech_headings(self):
        good = self.copy_fixture("tech_good.md", "04-technology-deep-dives/02-kafka.md")
        self.assertEqual(self.run_check(paths=[good])[0], 0)

    def test_breakdown_headings_order(self):
        good = self.copy_fixture("breakdown_good.md", "05-breakdowns-core/01-x.md")
        code, out = self.run_check(paths=[good])
        self.assertEqual(code, 0, out)
        bad = self.copy_fixture("breakdown_bad_order.md", "05-breakdowns-core/02-y.md")
        code, out = self.run_check(paths=[bad])
        self.assertEqual(code, 1)
        self.assertIn("HEADINGS", out)

    def test_breakdown_levels(self):
        bad = self.copy_fixture("breakdown_no_staff.md", "05-breakdowns-core/03-z.md")
        code, out = self.run_check(paths=[bad])
        self.assertEqual(code, 1)
        self.assertIn("LEVELS", out)
        self.assertNotIn("HEADINGS", out)

    def test_word_count_warns_without_failing(self):
        good = self.copy_fixture("concept_good.md", "01-the-framework/03-x.md")
        code, out = self.run_check(paths=[good])
        self.assertEqual(code, 0)
        self.assertIn("WARN word count", out)

    def test_delivery_framework_table(self):
        steps = ["Requirements", "Sources & volume", "High-level architecture", "Data model",
                 "Pipeline design", "Deep dives", "Monitoring & SLAs"]
        table = "| # | Step |\n|---|---|\n" + "\n".join(f"| {i} | {s} |" for i, s in enumerate(steps, 1))
        body = "# T\n\n## The Problem\n\n{t}\n\n## In the Interview\n\n## Common Mistakes\n\n## Key Takeaways\n"
        rel = "01-the-framework/02-delivery-framework.md"
        p = self.write(rel, body.format(t=table))
        self.assertEqual(self.run_check(paths=[p])[0], 0)
        p = self.write(rel, body.format(t="no table here"))
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("HEADINGS", out)

    def test_quiz_count_and_details(self):
        p = self.write("05-breakdowns-core/11-quiz.md", quiz_text(9))
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("QUIZ_COUNT", out)
        p = self.write("05-breakdowns-core/11-quiz.md", quiz_text(12, [i for i in range(1, 13) if i != 3]))
        code, out = self.run_check(paths=[p])
        self.assertEqual(code, 1)
        self.assertIn("QUIZ_DETAILS", out)
        p = self.write("05-breakdowns-core/11-quiz.md", quiz_text(12))
        code, out = self.run_check(paths=[p])
        self.assertEqual((code, out), (0, ""))

    @unittest.skipUnless(os.environ.get("CHECK_MERMAID") == "1", "set CHECK_MERMAID=1 to run")
    def test_mermaid_flag_reports_invalid(self):
        bad = self.write("README.md", "# T\n\n```mermaid\nflowchart LR\n A -->\n```\n")
        code, out = self.run_check("--mermaid", paths=[bad])
        self.assertEqual(code, 1)
        self.assertIn("MERMAID", out)
        self.assertNotIn("unavailable", out)
        good = self.write("README.md", "# T\n\n```mermaid\nflowchart LR\n A --> B\n```\n")
        code, out = self.run_check("--mermaid", paths=[good])
        self.assertEqual((code, out), (0, ""))


if __name__ == "__main__":
    unittest.main()
