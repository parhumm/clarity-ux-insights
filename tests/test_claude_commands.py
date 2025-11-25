#!/usr/bin/env python3
"""Tests for Claude slash commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_commands_directory_structure():
    """Test that command directories exist."""
    print("\n🧪 Testing command directory structure...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    expected_dirs = [
        "analysis",
        "fetch",
        "maintenance",
        "reports",
    ]

    for dir_name in expected_dirs:
        dir_path = commands_dir / dir_name
        assert dir_path.exists(), f"Directory missing: {dir_name}"
        print(f"  ✓ {dir_name}/ exists")

    print(f"  ✓ All {len(expected_dirs)} directories found")


def test_command_files_exist():
    """Test that expected command files exist."""
    print("\n🧪 Testing command files...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    expected_commands = {
        "analysis": [
            "query-data.md",
            "aggregate-metrics.md",
            "system-status.md",
        ],
        "fetch": [
            "fetch-clarity-data.md",
        ],
        "maintenance": [
            "aggregate-all.md",
            "list-data.md",
        ],
        "reports": [
            "generate-summary.md",
        ],
    }

    total_commands = 0
    for category, commands in expected_commands.items():
        for command in commands:
            command_path = commands_dir / category / command
            assert command_path.exists(), f"Command missing: {category}/{command}"
            print(f"  ✓ {category}/{command}")
            total_commands += 1

    print(f"  ✓ All {total_commands} command files found")


def test_command_content():
    """Test that commands have proper content."""
    print("\n🧪 Testing command content...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    all_commands = list(commands_dir.glob("*/*.md"))

    for command_path in all_commands:
        with open(command_path, 'r') as f:
            content = f.read()

        # Check for title
        assert content.startswith('#'), f"{command_path.name}: Missing title"

        # Check for essential sections
        has_usage = 'Usage' in content or 'usage' in content
        has_examples = 'Example' in content or 'example' in content or '```' in content

        assert has_usage or has_examples, \
            f"{command_path.name}: Missing usage/examples section"

        print(f"  ✓ {command_path.relative_to(commands_dir.parent)}")

    print(f"  ✓ All {len(all_commands)} commands have proper content")


def test_command_code_blocks():
    """Test that commands have code examples."""
    print("\n🧪 Testing command code blocks...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    all_commands = list(commands_dir.glob("*/*.md"))

    for command_path in all_commands:
        with open(command_path, 'r') as f:
            content = f.read()

        # Check for code blocks
        assert '```' in content, f"{command_path.name}: Missing code blocks"
        assert 'python' in content.lower(), f"{command_path.name}: Missing python commands"

        print(f"  ✓ {command_path.name} has code examples")

    print(f"  ✓ All {len(all_commands)} commands have code blocks")


def test_command_cli_references():
    """Test that commands reference the CLI correctly."""
    print("\n🧪 Testing CLI references...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    # Commands that should reference clarity_cli.py
    cli_commands = [
        "analysis/query-data.md",
        "analysis/aggregate-metrics.md",
        "analysis/system-status.md",
        "maintenance/aggregate-all.md",
        "maintenance/list-data.md",
    ]

    for command_path in cli_commands:
        full_path = commands_dir / command_path
        with open(full_path, 'r') as f:
            content = f.read()

        assert 'clarity_cli.py' in content, \
            f"{command_path}: Should reference clarity_cli.py"
        print(f"  ✓ {command_path} references CLI")

    print(f"  ✓ All {len(cli_commands)} CLI commands reference clarity_cli.py")


def test_no_hardcoded_data():
    """Test that commands don't contain hardcoded project data."""
    print("\n🧪 Testing for hardcoded data...")

    commands_dir = Path(__file__).parent.parent / ".claude/commands"

    all_commands = list(commands_dir.glob("*/*.md"))

    # Patterns that should NOT appear (example project names)
    forbidden_patterns = [
        'Televika',  # Example project name
    ]

    for command_path in all_commands:
        with open(command_path, 'r') as f:
            content = f.read()

        for pattern in forbidden_patterns:
            assert pattern not in content, \
                f"{command_path.name}: Contains hardcoded data: {pattern}"

    print(f"  ✓ All {len(all_commands)} commands are generic")


def run_all_tests():
    """Run all Claude command tests."""
    print("=" * 60)
    print("CLAUDE SLASH COMMANDS TESTS")
    print("=" * 60)

    tests = [
        test_commands_directory_structure,
        test_command_files_exist,
        test_command_content,
        test_command_code_blocks,
        test_command_cli_references,
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
