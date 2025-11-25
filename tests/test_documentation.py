#!/usr/bin/env python3
"""Tests for documentation completeness."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_documentation_files_exist():
    """Test that all documentation files exist."""
    print("\n🧪 Testing documentation files...")

    docs_dir = Path(__file__).parent.parent / "docs"
    expected_docs = [
        "QUICK-START.md",
        "DATE-FORMATS.md",
        "README-SUMMARY.md",
    ]

    for doc in expected_docs:
        doc_path = docs_dir / doc
        assert doc_path.exists(), f"Documentation missing: {doc}"
        print(f"  ✓ {doc}")

    print(f"  ✓ All {len(expected_docs)} documentation files found")


def test_example_configs_exist():
    """Test that example configurations exist."""
    print("\n🧪 Testing example configurations...")

    examples_dir = Path(__file__).parent.parent / "examples"
    expected_examples = [
        "ecommerce-config.yaml",
        "saas-config.yaml",
        "media-streaming-config.yaml",
    ]

    for example in expected_examples:
        example_path = examples_dir / example
        assert example_path.exists(), f"Example missing: {example}"
        print(f"  ✓ {example}")

    print(f"  ✓ All {len(expected_examples)} example files found")


def test_readme_links():
    """Test that README contains links to documentation."""
    print("\n🧪 Testing README links...")

    readme_path = Path(__file__).parent.parent / "README.md"
    with open(readme_path, 'r') as f:
        readme_content = f.read()

    required_links = [
        "QUICK-START.md",
        "DATE-FORMATS.md",
        "README-SUMMARY.md",
        "ecommerce-config.yaml",
        "saas-config.yaml",
        "media-streaming-config.yaml",
    ]

    for link in required_links:
        assert link in readme_content, f"README missing link to: {link}"
        print(f"  ✓ Links to {link}")

    print("  ✓ All documentation links present in README")


def test_quick_start_content():
    """Test that quick start guide has essential sections."""
    print("\n🧪 Testing quick start content...")

    quick_start_path = Path(__file__).parent.parent / "docs/QUICK-START.md"

    with open(quick_start_path, 'r') as f:
        content = f.read()

    required_sections = [
        "Prerequisites",
        "Installation",
        "Configuration",
        "Basic Usage",
        "Next Steps",
    ]

    for section in required_sections:
        assert section in content, f"Quick start missing section: {section}"
        print(f"  ✓ Has '{section}' section")

    print("  ✓ All required sections present")


def test_date_formats_content():
    """Test that date formats guide covers all formats."""
    print("\n🧪 Testing date formats guide...")

    date_formats_path = Path(__file__).parent.parent / "docs/DATE-FORMATS.md"

    with open(date_formats_path, 'r') as f:
        content = f.read()

    required_formats = [
        "Numeric Formats",
        "Relative Dates",
        "Month Formats",
        "Quarter Formats",
        "Year Format",
        "Custom Ranges",
    ]

    for format_type in required_formats:
        assert format_type in content, f"Date formats missing: {format_type}"
        print(f"  ✓ Documents '{format_type}'")

    # Check for example formats
    example_formats = ["7", "last-week", "November", "2025-Q4", "2025"]
    for fmt in example_formats:
        assert f'"{fmt}"' in content or f"'{fmt}'" in content, \
            f"Missing example: {fmt}"

    print("  ✓ All format types and examples documented")


def test_readme_summary_content():
    """Test that README summary has all key sections."""
    print("\n🧪 Testing README summary content...")

    summary_path = Path(__file__).parent.parent / "docs/README-SUMMARY.md"

    with open(summary_path, 'r') as f:
        content = f.read()

    required_sections = [
        "What's Included",
        "Features",
        "Architecture",
        "Directory Structure",
        "Test Coverage",
        "Performance",
        "Usage Examples",
    ]

    for section in required_sections:
        assert section in content, f"Summary missing section: {section}"
        print(f"  ✓ Has '{section}' section")

    print("  ✓ All required sections present")


def run_all_tests():
    """Run all documentation tests."""
    print("=" * 60)
    print("DOCUMENTATION TESTS")
    print("=" * 60)

    tests = [
        test_documentation_files_exist,
        test_example_configs_exist,
        test_readme_links,
        test_quick_start_content,
        test_date_formats_content,
        test_readme_summary_content,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
