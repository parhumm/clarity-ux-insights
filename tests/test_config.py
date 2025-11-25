#!/usr/bin/env python3
"""Tests for configuration system."""

import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import ClarityConfig, load_config


def test_default_config():
    """Test loading default configuration."""
    print("\n🧪 Testing default configuration...")

    config = ClarityConfig.load()

    assert config.project.name == "Clarity Project"
    assert config.project.type == "website"
    assert config.reports.default_period_days == 3
    assert config.data.retention_days == 90

    print("  ✓ Default configuration loaded successfully")
    print(f"    - Project: {config.project.name}")
    print(f"    - Retention: {config.data.retention_days} days")


def test_template_config():
    """Test loading from template file."""
    print("\n🧪 Testing template configuration...")

    template_path = Path(__file__).parent.parent / "config.template.yaml"
    assert template_path.exists(), "Template file not found"

    # Verify template is valid YAML
    with open(template_path, 'r') as f:
        data = yaml.safe_load(f)

    assert 'project' in data
    assert 'clarity' in data
    assert 'data' in data
    assert 'reports' in data

    print("  ✓ Template file is valid YAML")
    print(f"    - Sections: {', '.join(data.keys())}")


def test_example_configs():
    """Test all example configurations."""
    print("\n🧪 Testing example configurations...")

    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = list(examples_dir.glob("*-config.yaml"))

    assert len(example_files) > 0, "No example configs found"

    for example_file in example_files:
        print(f"  Testing {example_file.name}...")

        with open(example_file, 'r') as f:
            data = yaml.safe_load(f)

        # Validate required sections
        assert 'project' in data, f"{example_file.name}: Missing 'project' section"
        assert 'name' in data['project'], f"{example_file.name}: Missing project name"
        assert 'type' in data['project'], f"{example_file.name}: Missing project type"

        print(f"    ✓ {data['project']['name']} ({data['project']['type']})")

        # Check page tracking if defined
        if 'tracking' in data and 'pages' in data['tracking']:
            pages = data['tracking']['pages']
            print(f"      - {len(pages)} pages configured")

    print(f"  ✓ All {len(example_files)} example configs are valid")


def test_config_validation():
    """Test configuration validation."""
    print("\n🧪 Testing configuration validation...")

    config = ClarityConfig()

    # Test with valid config
    errors = config.validate()
    assert len(errors) == 0, "Default config should have no errors"
    print("  ✓ Default config validation passed")

    # Test with invalid output format
    config.reports.output_formats = ['invalid']
    errors = config.validate()
    assert len(errors) > 0, "Should catch invalid output format"
    print(f"  ✓ Validation catches errors: {errors[0]}")


def test_page_lookup():
    """Test page lookup functions."""
    print("\n🧪 Testing page lookup functions...")

    config = ClarityConfig()

    # Add test pages
    from config_loader import PageTrackingConfig
    config.tracking.pages = [
        PageTrackingConfig(id="page-001", path="/checkout", name="Checkout", category="conversion"),
        PageTrackingConfig(id="page-002", path="/search", name="Search", category="discovery"),
        PageTrackingConfig(id="page-003", path="/product/123", name="Product", category="content"),
    ]

    # Test get by ID
    page = config.get_page_by_id("page-001")
    assert page is not None
    assert page.path == "/checkout"
    print("  ✓ Get page by ID works")

    # Test get by path
    page = config.get_page_by_path("/search")
    assert page is not None
    assert page.id == "page-002"
    print("  ✓ Get page by path works")

    # Test get by category
    conversion_pages = config.get_pages_by_category("conversion")
    assert len(conversion_pages) == 1
    assert conversion_pages[0].id == "page-001"
    print("  ✓ Get pages by category works")


def test_ecommerce_config():
    """Test e-commerce example configuration."""
    print("\n🧪 Testing e-commerce configuration...")

    examples_dir = Path(__file__).parent.parent / "examples"
    ecommerce_path = examples_dir / "ecommerce-config.yaml"

    if not ecommerce_path.exists():
        print("  ⚠ E-commerce config not found, skipping")
        return

    with open(ecommerce_path, 'r') as f:
        data = yaml.safe_load(f)

    # Verify e-commerce specific settings
    assert data['project']['type'] == 'e-commerce'
    assert 'tracking' in data
    assert len(data['tracking']['pages']) >= 3  # Should have checkout, cart, product pages

    # Check for conversion pages
    conversion_pages = [p for p in data['tracking']['pages'] if p.get('category') == 'conversion']
    assert len(conversion_pages) >= 1, "E-commerce should have conversion pages"

    print(f"  ✓ E-commerce config validated")
    print(f"    - {len(data['tracking']['pages'])} pages")
    print(f"    - {len(conversion_pages)} conversion pages")


def run_all_tests():
    """Run all configuration tests."""
    print("=" * 60)
    print("CONFIGURATION SYSTEM TESTS")
    print("=" * 60)

    tests = [
        test_default_config,
        test_template_config,
        test_example_configs,
        test_config_validation,
        test_page_lookup,
        test_ecommerce_config,
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
