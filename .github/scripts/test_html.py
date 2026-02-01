#!/usr/bin/env python3
"""
HTML validation tests using Python's html.parser module.
Tests the Jekyll-generated site for common HTML issues.
"""

import os
import sys
from html.parser import HTMLParser
from pathlib import Path


class HTMLValidator(HTMLParser):
    """HTML parser that validates structure and collects information."""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tag_stack = []
        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_title = False
        self.has_body = False
        self.links = []
        self.images = []

        # Self-closing tags that don't need closing tags
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_decl(self, decl):
        if decl.lower().startswith('doctype'):
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)

        if tag == 'html':
            self.has_html = True
        elif tag == 'head':
            self.has_head = True
        elif tag == 'title':
            self.has_title = True
        elif tag == 'body':
            self.has_body = True
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.links.append(href)
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt')
            self.images.append({'src': src, 'alt': alt})
            if alt is None:
                self.warnings.append(f"Image missing alt attribute: {src}")

        # Track non-void elements for proper closing
        if tag not in self.void_elements:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in self.void_elements:
            return

        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag </{tag}> with no matching opening tag")
            return

        if self.tag_stack[-1] != tag:
            self.errors.append(
                f"Mismatched tags: expected </{self.tag_stack[-1]}>, found </{tag}>"
            )
            # Try to recover by popping until we find a match
            while self.tag_stack and self.tag_stack[-1] != tag:
                self.tag_stack.pop()

        if self.tag_stack:
            self.tag_stack.pop()

    def validate(self):
        """Run final validation checks."""
        if not self.has_doctype:
            self.warnings.append("Missing DOCTYPE declaration")
        if not self.has_html:
            self.errors.append("Missing <html> tag")
        if not self.has_head:
            self.errors.append("Missing <head> tag")
        if not self.has_title:
            self.warnings.append("Missing <title> tag")
        if not self.has_body:
            self.errors.append("Missing <body> tag")
        if self.tag_stack:
            self.errors.append(f"Unclosed tags: {', '.join(self.tag_stack)}")

        return len(self.errors) == 0


def validate_html_file(filepath):
    """Validate a single HTML file."""
    validator = HTMLValidator()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        validator.feed(content)
        validator.validate()

        return validator
    except Exception as e:
        validator.errors.append(f"Failed to parse file: {e}")
        return validator


def find_html_files(directory):
    """Find all HTML files in a directory recursively."""
    return list(Path(directory).rglob('*.html'))


def run_tests(site_dir='_site'):
    """Run HTML validation tests on all files in the site directory."""
    print(f"Running HTML validation tests on {site_dir}/")
    print("=" * 60)

    if not os.path.exists(site_dir):
        print(f"ERROR: Site directory '{site_dir}' not found!")
        print("Make sure to build the site first with 'jekyll build'")
        return False

    html_files = find_html_files(site_dir)

    if not html_files:
        print(f"ERROR: No HTML files found in {site_dir}/")
        return False

    print(f"Found {len(html_files)} HTML file(s) to validate\n")

    total_errors = 0
    total_warnings = 0
    failed_files = []

    for filepath in sorted(html_files):
        relative_path = filepath.relative_to(site_dir)
        validator = validate_html_file(filepath)

        if validator.errors:
            failed_files.append(str(relative_path))
            print(f"FAIL: {relative_path}")
            for error in validator.errors:
                print(f"  ERROR: {error}")
            total_errors += len(validator.errors)
        else:
            print(f"PASS: {relative_path}")

        for warning in validator.warnings:
            print(f"  WARNING: {warning}")
        total_warnings += len(validator.warnings)

    print("\n" + "=" * 60)
    print(f"Results: {len(html_files)} files tested")
    print(f"  Passed: {len(html_files) - len(failed_files)}")
    print(f"  Failed: {len(failed_files)}")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")

    if failed_files:
        print(f"\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")
        return False

    print("\nAll HTML validation tests passed!")
    return True


def test_site_structure(site_dir='_site'):
    """Test that expected site structure exists."""
    print("\nRunning site structure tests...")
    print("=" * 60)

    errors = []

    # Check index.html exists
    index_path = Path(site_dir) / 'index.html'
    if index_path.exists():
        print("PASS: index.html exists")
    else:
        print("FAIL: index.html not found")
        errors.append("Missing index.html")

    # Check for at least one HTML file
    html_files = find_html_files(site_dir)
    if html_files:
        print(f"PASS: Found {len(html_files)} HTML file(s)")
    else:
        print("FAIL: No HTML files found")
        errors.append("No HTML files in site")

    print("\n" + "=" * 60)
    if errors:
        print(f"Structure tests failed with {len(errors)} error(s)")
        return False

    print("All structure tests passed!")
    return True


if __name__ == '__main__':
    site_dir = sys.argv[1] if len(sys.argv) > 1 else '_site'

    print("Jekyll Site HTML Tests")
    print("=" * 60 + "\n")

    # Run all tests
    structure_ok = test_site_structure(site_dir)
    print()
    validation_ok = run_tests(site_dir)

    # Exit with appropriate code
    if structure_ok and validation_ok:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED")
        sys.exit(1)
