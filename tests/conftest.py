import sys
from pathlib import Path

import pytest

LAMBDA_IMAGE_GEN_PATH = str(Path(__file__).parent.parent / 'Lambdas' / 'image_gen')


@pytest.fixture(scope='session', autouse=True)
def setup_python_path():
    """Add Lambda directories to sys.path for testing."""
    if LAMBDA_IMAGE_GEN_PATH not in sys.path:
        sys.path.insert(0, LAMBDA_IMAGE_GEN_PATH)
    yield
    # Cleanup paths after tests
    if LAMBDA_IMAGE_GEN_PATH in sys.path:
        sys.path.remove(LAMBDA_IMAGE_GEN_PATH)


@pytest.fixture(autouse=True)
def reset_imports():
    """
    Reset module imports between tests to avoid state pollution.

    This ensures each test gets a fresh import of the Lambda modules,
    preventing issues with global variables like b64_image_list.
    """
    modules_to_reset = ['main']
    for module in modules_to_reset:
        if module in sys.modules:
            del sys.modules[module]
    yield


@pytest.fixture
def aws_credentials(monkeypatch):
    """Mock AWS credentials for boto3 clients."""
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')


@pytest.fixture
def mock_lambda_context():
    """
    Standard mock Lambda context object.

    Provides a reusable context object with typical Lambda attributes.
    """
    from unittest.mock import Mock

    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '$LATEST'
    context.invoked_function_arn = (
        'arn:aws:lambda:us-east-1:123456789012:function:test-function'
    )
    context.memory_limit_in_mb = 512
    context.aws_request_id = 'test-request-id'
    context.log_group_name = '/aws/lambda/test-function'
    context.log_stream_name = '2026/01/16/[$LATEST]test'

    context.get_remaining_time_in_millis.return_value = 300000

    return context
