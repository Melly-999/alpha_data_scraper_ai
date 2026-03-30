import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run tests marked as slow.",
    )
    parser.addoption(
        "--run-mt5",
        action="store_true",
        default=False,
        help="Run tests marked as mt5.",
    )


def pytest_collection_modifyitems(config, items):
    run_slow = config.getoption("--run-slow")
    run_mt5 = config.getoption("--run-mt5")

    skip_slow = pytest.mark.skip(reason="Need --run-slow option to run.")
    skip_mt5 = pytest.mark.skip(reason="Need --run-mt5 option to run.")

    for item in items:
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)
        if "mt5" in item.keywords and not run_mt5:
            item.add_marker(skip_mt5)
