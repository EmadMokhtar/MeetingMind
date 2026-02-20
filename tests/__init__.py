"""Test package imports and version."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import meetingmind

    with subtests.test("has_version"):
        assert hasattr(meetingmind, "__version__")

    with subtests.test("version_format"):
        assert isinstance(meetingmind.__version__, str)
        assert "." in meetingmind.__version__


def test_module_imports():
    """Test that all main modules can be imported."""
    modules = [
        "meetingmind.config",
        "meetingmind.models",
        "meetingmind.agents",
        "meetingmind.state",
        "meetingmind.markdown",
        "meetingmind.watcher",
        "meetingmind.main",
    ]

    for module_name in modules:
        with subtests.test(module=module_name):
            __import__(module_name)
