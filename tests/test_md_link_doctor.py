import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import md_link_doctor as m


def write(root, name, text):
    p = os.path.join(root, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class Tests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(m.slugify("Hello, World!"), "hello-world")
        self.assertEqual(m.slugify("`code` Heading"), "code-heading")

    def test_good_links(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "a.md", "# Top\n[b](b.md) [sec](b.md#second) [self](#top)\n")
            write(d, "b.md", "# B\n## Second\n")
            self.assertEqual(m.main([d]), 0)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.md", "[x](nope.md)\n")
            probs = m.check_file(p, {})
            self.assertEqual(len(probs), 1)
            self.assertEqual(probs[0][3], "file not found")

    def test_missing_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "b.md", "# B\n")
            p = write(d, "a.md", "[x](b.md#gone)\n")
            self.assertEqual(m.check_file(p, {})[0][3], "anchor not found")

    def test_external_and_code_fence_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.md", "[w](https://example.com)\n```\n[x](nope.md)\n```\n")
            self.assertEqual(m.check_file(p, {}), [])

    def test_inline_code_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.md", "use `[x](nope.md)` syntax\n")
            self.assertEqual(m.check_file(p, {}), [])

    def test_duplicate_headings(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.md", "# A\n# A\n[x](#a-1)\n")
            self.assertEqual(m.check_file(p, {}), [])

    def test_image_links(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.md", "![pic](img/missing.png)\n")
            self.assertEqual(len(m.check_file(p, {})), 1)

    def test_exit_code_on_problem(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "a.md", "[x](nope.md)\n")
            self.assertEqual(m.main([d]), 1)


if __name__ == "__main__":
    unittest.main()
