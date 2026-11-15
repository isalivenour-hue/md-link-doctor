#!/usr/bin/env python3
"""md-link-doctor: find broken relative links and anchors in Markdown files.

Offline and dependency-free. External (http/https/mailto) links are skipped.
Exit code 1 if any problem is found, so it works in CI.
"""
import argparse
import os
import re
import sys

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def slugify(text):
    """GitHub-style heading slug."""
    text = re.sub(r"[`*_]", "", text.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def parse(path):
    """Return (anchors, links) where links is a list of (line_no, target)."""
    anchors, links, seen, in_fence = set(), [], {}, False
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m:
                slug = slugify(m.group(2))
                count = seen.get(slug, 0)
                seen[slug] = count + 1
                anchors.add(slug if count == 0 else "%s-%d" % (slug, count))
            for a, b in LINK_RE.findall(re.sub(r"`[^`]*`", "", line)):
                links.append((n, a or b))
    return anchors, links


def is_external(target):
    return re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) is not None


def check_file(path, cache):
    problems = []
    anchors, links = cache.setdefault(path, parse(path))
    for line, target in links:
        if is_external(target):
            continue
        file_part, _, frag = target.partition("#")
        if file_part == "":
            dest = path
        else:
            dest = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
            if not os.path.exists(dest):
                problems.append((path, line, target, "file not found"))
                continue
        if frag:
            if os.path.isdir(dest) or not dest.lower().endswith(".md"):
                continue
            if dest not in cache:
                cache[dest] = parse(dest)
            if frag.lower() not in cache[dest][0]:
                problems.append((path, line, target, "anchor not found"))
    return problems


def find_markdown(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
                for f in sorted(files):
                    if f.lower().endswith(".md"):
                        yield os.path.join(root, f)
        else:
            yield p


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find broken relative links and anchors in Markdown.")
    ap.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    args = ap.parse_args(argv)
    cache, problems = {}, []
    for f in find_markdown(args.paths):
        problems.extend(check_file(f, cache))
    for path, line, target, why in problems:
        print("%s:%d: %s -> %s" % (path, line, why, target))
    print("%d problem(s) found" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
