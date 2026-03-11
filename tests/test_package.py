"""
Basic package and entry point tests.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from stellar_seismic_catalog import __version__


def test_version() -> None:
    """Package exposes a version string."""
    assert __version__ == "0.1.0"
