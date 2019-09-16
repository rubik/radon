import pytest


@pytest.fixture
def log_mock(mocker):
    return mocker.patch('radon.cli.log_result')
