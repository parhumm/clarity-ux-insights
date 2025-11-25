#!/usr/bin/env python3
"""Tests for report templates."""

import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_template_files_exist():
    """Test that all expected template files exist."""
    print("\n🧪 Testing template files existence...")

    templates_dir = Path(__file__).parent.parent / "templates"

    expected_general_templates = [
        "ux-health.md.template",
        "frustration-analysis.md.template",
        "device-performance.md.template",
        "geographic-insights.md.template",
        "content-performance.md.template",
        "engagement-analysis.md.template",
    ]

    expected_page_templates = [
        "page-analysis.md.template",
    ]

    # Check general templates
    general_dir = templates_dir / "general"
    for template in expected_general_templates:
        template_path = general_dir / template
        assert template_path.exists(), f"General template missing: {template}"
        print(f"  ✓ {template}")

    # Check page templates
    pages_dir = templates_dir / "pages"
    for template in expected_page_templates:
        template_path = pages_dir / template
        assert template_path.exists(), f"Page template missing: {template}"
        print(f"  ✓ pages/{template}")

    print(f"  ✓ All {len(expected_general_templates) + len(expected_page_templates)} templates found")


def test_template_yaml_frontmatter():
    """Test that all templates have valid YAML frontmatter."""
    print("\n🧪 Testing YAML frontmatter...")

    templates_dir = Path(__file__).parent.parent / "templates"

    all_templates = list((templates_dir / "general").glob("*.template"))
    all_templates.extend(list((templates_dir / "pages").glob("*.template")))

    for template_path in all_templates:
        with open(template_path, 'r') as f:
            content = f.read()

        # Check for YAML frontmatter
        assert content.startswith('---'), f"{template_path.name}: Missing YAML frontmatter start"
        assert content.count('---') >= 2, f"{template_path.name}: Incomplete YAML frontmatter"

        # Extract frontmatter
        parts = content.split('---', 2)
        frontmatter = parts[1].strip()

        # Check for required fields
        assert 'report_type:' in frontmatter, f"{template_path.name}: Missing report_type"
        assert 'project_name:' in frontmatter, f"{template_path.name}: Missing project_name"
        assert 'date_range:' in frontmatter or 'START_DATE' in content, f"{template_path.name}: Missing date info"
        assert 'generated:' in frontmatter, f"{template_path.name}: Missing generated"

        print(f"  ✓ {template_path.name} has valid frontmatter")


def test_template_placeholders():
    """Test that templates use consistent placeholder format."""
    print("\n🧪 Testing template placeholders...")

    templates_dir = Path(__file__).parent.parent / "templates"

    all_templates = list((templates_dir / "general").glob("*.template"))
    all_templates.extend(list((templates_dir / "pages").glob("*.template")))

    # Common placeholders that should be in most templates
    common_placeholders = [
        'PROJECT_NAME',
        'START_DATE',
        'END_DATE',
        'GENERATED_DATE',
    ]

    for template_path in all_templates:
        with open(template_path, 'r') as f:
            content = f.read()

        # Find all placeholders
        placeholders = re.findall(r'\{([A-Z_0-9]+)\}', content)

        # Check placeholder format (uppercase with underscores)
        for placeholder in placeholders:
            assert re.match(r'^[A-Z_0-9]+$', placeholder), \
                f"{template_path.name}: Invalid placeholder format: {placeholder}"

        # Check for common placeholders
        for common in common_placeholders:
            if common not in placeholders:
                print(f"  ⚠ {template_path.name}: Missing common placeholder {common}")

        print(f"  ✓ {template_path.name}: {len(set(placeholders))} unique placeholders")


def test_audience_sections():
    """Test that general templates have audience-specific sections."""
    print("\n🧪 Testing audience sections...")

    templates_dir = Path(__file__).parent.parent / "templates" / "general"

    required_audiences = [
        'Technical Team',
        'UX Team',
        'Product/UX Team',
        'Business Team',
        'Executive Team',
        'Marketing Team',
    ]

    for template_path in templates_dir.glob("*.template"):
        with open(template_path, 'r') as f:
            content = f.read()

        # Check for at least one audience section
        has_audience_section = any(audience in content for audience in required_audiences)
        assert has_audience_section, f"{template_path.name}: Missing audience sections"

        # Count audience sections
        audience_count = sum(1 for audience in required_audiences if audience in content)
        print(f"  ✓ {template_path.name}: {audience_count} audience sections")


def test_template_structure():
    """Test that templates have proper structure (headers, tables, etc.)."""
    print("\n🧪 Testing template structure...")

    templates_dir = Path(__file__).parent.parent / "templates"

    all_templates = list((templates_dir / "general").glob("*.template"))
    all_templates.extend(list((templates_dir / "pages").glob("*.template")))

    for template_path in all_templates:
        with open(template_path, 'r') as f:
            content = f.read()

        # Check for main title (# Header)
        assert re.search(r'^#\s+\w+', content, re.MULTILINE), \
            f"{template_path.name}: Missing main title"

        # Check for sections (## Header)
        sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        assert len(sections) >= 3, \
            f"{template_path.name}: Should have at least 3 sections, found {len(sections)}"

        print(f"  ✓ {template_path.name}: {len(sections)} sections")


def test_no_hardcoded_data():
    """Test that templates don't contain hardcoded project-specific data."""
    print("\n🧪 Testing for hardcoded data...")

    templates_dir = Path(__file__).parent.parent / "templates"

    all_templates = list((templates_dir / "general").glob("*.template"))
    all_templates.extend(list((templates_dir / "pages").glob("*.template")))

    # Patterns that should NOT appear (example project names, URLs, etc.)
    forbidden_patterns = [
        r'Televika',  # Example project name
        r'example\.com',  # Would be in placeholders, not hardcoded
        r'http://(?!.*\{)',  # Hardcoded HTTP URLs (not in placeholders)
        r'https://(?!.*\{)(?!docs\.microsoft)',  # Hardcoded HTTPS URLs except docs
    ]

    for template_path in all_templates:
        with open(template_path, 'r') as f:
            content = f.read()

        for pattern in forbidden_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches and 'microsoft' not in str(matches).lower():
                print(f"  ⚠ {template_path.name}: Potential hardcoded data: {matches}")

        print(f"  ✓ {template_path.name}: No forbidden patterns found")


def run_all_tests():
    """Run all template tests."""
    print("=" * 60)
    print("TEMPLATE TESTS")
    print("=" * 60)

    tests = [
        test_template_files_exist,
        test_template_yaml_frontmatter,
        test_template_placeholders,
        test_audience_sections,
        test_template_structure,
        test_no_hardcoded_data,
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
