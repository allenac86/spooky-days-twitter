import json
from unittest.mock import Mock, patch, mock_open
from base64 import b64encode
from datetime import datetime
import pytest


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('IMAGE_BUCKET_NAME', 'test-bucket')
    monkeypatch.setenv('DYNAMODB_TABLE_NAME', 'test-table')
    monkeypatch.setenv('OPENAI_SECRET_ARN', 'arn:aws:secretsmanager:us-east-1:123:secret:test')
    monkeypatch.setenv('TWITTER_SECRET_ARN', 'arn:aws:secretsmanager:us-east-1:123:secret:twitter')


@pytest.fixture
def mock_config():
    now = datetime.now()
    month = now.strftime('%B').lower()
    day = str(now.day)
    return {
        "Prompt": "Create a spooky image for ",
        month: {day: ["Hat", "Bagel"]}
    }


@pytest.fixture
def mock_openai_response():
    mock_response = Mock()
    mock_response.data = [Mock()]
    mock_response.data[0].b64_json = b64encode(b"fake_image").decode('utf-8')
    return mock_response


@pytest.fixture
def lambda_context():
    context = Mock()
    context.aws_request_id = 'test-id'
    return context


def test_handler_success(mock_env_vars, mock_config, mock_openai_response, lambda_context):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_s3.get_object.return_value = {'Body': Mock(read=lambda: json.dumps(mock_config).encode())}
        mock_dynamodb = Mock()
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {'SecretString': 'test-api-key'}
        
        def client_factory(service):
            if service == 's3': return mock_s3
            if service == 'secretsmanager': return mock_secrets
            return mock_dynamodb
        
        mock_boto.side_effect = client_factory
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.images.generate.return_value = mock_openai_response
            mock_openai.return_value = mock_client
            
            with patch('builtins.open', mock_open()):
                from main import handler
                
                response = handler({}, lambda_context)
                
                assert response['statusCode'] == 200
                assert mock_s3.upload_file.called
                assert mock_dynamodb.put_item.called


def test_handler_failure(mock_env_vars, mock_config, lambda_context):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_s3.get_object.return_value = {'Body': Mock(read=lambda: json.dumps(mock_config).encode())}
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {'SecretString': 'test-api-key'}
        
        def client_factory(service):
            return mock_secrets if service == 'secretsmanager' else mock_s3
        
        mock_boto.side_effect = client_factory
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.images.generate.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            from main import handler
            
            response = handler({}, lambda_context)
            
            assert response['statusCode'] == 500


def test_upload_removes_tmp_prefix(mock_env_vars, mock_config):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_s3.get_object.return_value = {'Body': Mock(read=lambda: json.dumps(mock_config).encode())}
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {'SecretString': 'test-api-key'}
        
        def client_factory(service):
            if service == 'secretsmanager': return mock_secrets
            return mock_s3
        
        mock_boto.side_effect = client_factory
        
        with patch('openai.OpenAI'):
            from main import upload_image_to_s3
            
            upload_image_to_s3("/tmp/test.jpg", "bucket")
            
            mock_s3.upload_file.assert_called_once_with("/tmp/test.jpg", "bucket", "images/test.jpg")


def test_dynamodb_insert(mock_env_vars, mock_config):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_s3.get_object.return_value = {'Body': Mock(read=lambda: json.dumps(mock_config).encode())}
        mock_dynamodb = Mock()
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {'SecretString': 'test-api-key'}
        
        def client_factory(service):
            if service == 'secretsmanager': return mock_secrets
            if service == 's3': return mock_s3
            return mock_dynamodb
        
        mock_boto.side_effect = client_factory
        
        with patch('openai.OpenAI'):
            from main import insert_dynamodb_record
            
            insert_dynamodb_record("test_job", "uploaded")
            
            assert mock_dynamodb.put_item.called
            args = mock_dynamodb.put_item.call_args[1]
            assert args['Item']['job_id']['S'] == "test_job"
            assert args['Item']['status']['S'] == "uploaded"
