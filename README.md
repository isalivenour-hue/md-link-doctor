# md-link-doctor

Find broken relative links and heading anchors in your Markdown files. Offline, one file, no dependencies.

Docs rot: files get renamed, headings change, and links quietly break. This checks every `[text](path)`, `![img](path)` and `[text](file.md#heading)` against the files on disk and exits with code 1 if anything is broken, so you can run it in CI.

## Usage

```
python md_link_doctor.py            # scan the current directory
python md_link_doctor.py docs README.md
```

Example output:

```
docs/guide.md:12: file not found -> setup.md
docs/guide.md:20: anchor not found -> api.md#timeouts
2 problem(s) found
```

## What it checks

- Relative file links and images exist.
- `#anchor` fragments match a heading in the target file (GitHub-style slugs, with `-1`, `-2` suffixes for duplicate headings).
- Links inside fenced code blocks and inline code are ignored.
- `http(s):`, `mailto:` and other external links are skipped (no network access).

## Limitations

- Reference-style links (`[text][ref]`) and HTML `<a>` tags are not checked.
- Anchor slugs follow GitHub's rules for common headings; unusual Unicode headings may differ.

## Tests

```
python -m unittest discover -s tests -v
```

## License

MIT
