import pytest

from web.app import app

# Make a request to the flask application to force it to initialize
test_client = app.test_client()
test_client.get('/')


@pytest.fixture
def client():
    return test_client
