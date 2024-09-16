import os
import pytest

@pytest.fixture(autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)
