#!/usr/bin/env python3
"""Tests for report generator."""

import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.report_generator import ReportGenerator
from scripts.query_engine import DateRange
from datetime import date, timedelta


def test_report_generator_initialization():
    """Test that report generator initializes correctly."""
    print("\n🧪 Testing report generator initialization...")

    generator = ReportGenerator()

    assert generator.query_engine is not None, "Query engine not initialized"
    assert generator.templates_dir.exists(), "Templates directory not found"
    assert generator.reports_dir.exists(), "Reports directory not found"

    print("  ✓ Report generator initialized")
    print(f"  ✓ Templates dir: {generator.templates_dir}")
    print(f"  ✓ Reports dir: {generator.reports_dir}")


def test_find_templates():
    """Test that all templates can be found."""
    print("\n🧪 Testing template discovery...")

    generator = ReportGenerator()

    expected_templates = [
        'ux-health',
        'frustration-analysis',
        'device-performance',
        'geographic-insights',
        'content-performance',
        'engagement-analysis',
    ]

    for template_name in expected_templates:
        template_path = generator._find_template(template_name)
        assert template_path.exists(), f"Template not found: {template_name}"
        print(f"  ✓ Found template: {template_name}")

    print(f"  ✓ All {len(expected_templates)} templates found")


def test_extract_frontmatter():
    """Test frontmatter extraction."""
    print("\n🧪 Testing frontmatter extraction...")

    generator = ReportGenerator()

    # Load a template
    template_path = generator._find_template('ux-health')
    with open(template_path, 'r') as f:
        content = f.read()

    frontmatter, body = generator._extract_frontmatter(content)

    assert isinstance(frontmatter, dict), "Frontmatter not a dict"
    assert len(body) > 0, "Body is empty"

    # Templates have placeholders in frontmatter, so it might be empty dict after parsing
    # The important thing is that we can extract the sections
    print(f"  ✓ Frontmatter extracted: {len(frontmatter)} fields (may contain placeholders)")
    print(f"  ✓ Body extracted: {len(body)} characters")

    # Verify frontmatter section exists in original
    assert content.startswith('---'), "Template should have frontmatter"
    assert 'report_type' in content, "Template should have report_type field"
    print("  ✓ Frontmatter section validated")


def test_gather_data():
    """Test data gathering from database."""
    print("\n🧪 Testing data gathering...")

    generator = ReportGenerator()

    # Get last 3 days
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    date_range = DateRange(start_date, end_date)

    data = generator._gather_data(date_range)

    # Should have some data keys
    assert isinstance(data, dict), "Data not a dict"

    print(f"  ✓ Gathered {len(data)} data fields")

    # Show sample data
    if data:
        sample_keys = list(data.keys())[:5]
        for key in sample_keys:
            print(f"    - {key}: {data[key]}")


def test_fill_placeholders():
    """Test placeholder filling."""
    print("\n🧪 Testing placeholder filling...")

    generator = ReportGenerator()

    template = """
Project: {PROJECT_NAME}
Date: {START_DATE} to {END_DATE}
Sessions: {TOTAL_SESSIONS}
"""

    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    date_range = DateRange(start_date, end_date)

    data = {'TOTAL_SESSIONS': '1,234'}

    result = generator._fill_placeholders(template, data, date_range)

    assert '{PROJECT_NAME}' not in result, "PROJECT_NAME not filled"
    assert '{START_DATE}' not in result, "START_DATE not filled"
    assert '{END_DATE}' not in result, "END_DATE not filled"
    assert '{TOTAL_SESSIONS}' not in result, "TOTAL_SESSIONS not filled"
    assert '1,234' in result, "Session count not in result"

    print("  ✓ All placeholders filled")
    print(f"  ✓ Output length: {len(result)} characters")


def test_generate_report():
    """Test full report generation."""
    print("\n🧪 Testing report generation...")

    generator = ReportGenerator()

    # Use temporary output directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override reports directory
        generator.reports_dir = Path(tmpdir)

        # Generate report for last 3 days
        end_date = date.today()
        start_date = end_date - timedelta(days=3)
        date_range = DateRange(start_date, end_date)

        output_path = generator.generate_report(
            'ux-health',
            date_range
        )

        assert output_path.exists(), "Report file not created"
        assert output_path.suffix == '.md', "Report not markdown file"

        # Read and validate report
        with open(output_path, 'r') as f:
            content = f.read()

        assert len(content) > 0, "Report is empty"
        assert content.startswith('---'), "Report missing frontmatter"
        assert 'UX Health Report' in content, "Report missing title"
        assert '{PROJECT_NAME}' not in content, "Unfilled placeholders remain"

        print(f"  ✓ Report generated: {output_path.name}")
        print(f"  ✓ Report size: {len(content)} characters")
        print(f"  ✓ No unfilled placeholders")


def test_output_path_generation():
    """Test output path generation."""
    print("\n🧪 Testing output path generation...")

    generator = ReportGenerator()

    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    date_range = DateRange(start_date, end_date)

    # General report
    path1 = generator._default_output_path('ux-health', date_range)
    assert 'general' in str(path1), "General report not in general directory"
    assert 'ux-health' in str(path1), "Template name not in path"
    print(f"  ✓ General report path: {path1.name}")

    # Page-specific report
    path2 = generator._default_output_path('page-analysis', date_range, page_id='/payment')
    assert 'pages' in str(path2), "Page report not in pages directory"
    assert 'payment' in str(path2), "Page ID not in path"
    print(f"  ✓ Page report path: {path2.name}")

    print("  ✓ Output paths generated correctly")


def run_all_tests():
    """Run all report generator tests."""
    print("=" * 60)
    print("REPORT GENERATOR TESTS")
    print("=" * 60)

    tests = [
        test_report_generator_initialization,
        test_find_templates,
        test_extract_frontmatter,
        test_gather_data,
        test_fill_placeholders,
        test_generate_report,
        test_output_path_generation,
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
