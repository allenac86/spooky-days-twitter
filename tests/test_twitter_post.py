import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def twitter_post_path():
    """Add twitter_post to sys.path for these tests."""
    path = str(Path(__file__).parent.parent / 'Lambdas' / 'twitter_post')
    if path not in sys.path:
        sys.path.insert(0, path)
    yield
    if path in sys.path:
        sys.path.remove(path)


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv(
        'TWITTER_SECRET_ARN', 'arn:aws:secretsmanager:us-east-1:123:secret:test'
    )
    monkeypatch.setenv('DYNAMODB_TABLE_NAME', 'test-table')
    monkeypatch.setenv('IMAGE_BUCKET_NAME', 'test-bucket')


@pytest.fixture
def mock_twitter_creds():
    return {
        'ACCESS_TOKEN': 'token',
        'ACCESS_TOKEN_SECRET': 'secret',
        'API_KEY': 'key',
        'API_SECRET': 'secret',
        'BEARER_TOKEN': 'bearer',
    }


@pytest.fixture
def s3_event():
    return {
        'Records': [
            {
                'eventName': 'ObjectCreated:Put',
                's3': {'object': {'key': 'images/january_15_0_NationalHatDay.jpg'}},
            }
        ]
    }


@pytest.fixture
def lambda_context():
    context = Mock()
    context.aws_request_id = 'test-id'
    return context


def test_insert_space_before_capital(mock_env_vars, mock_twitter_creds):
    with patch('boto3.client') as mock_boto:
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_twitter_creds)
        }
        mock_boto.return_value = mock_secrets

        with (
            patch('tweepy.Client'),
            patch('tweepy.OAuth1UserHandler'),
            patch('tweepy.API'),
        ):
            from main import insert_space_before_capital

            assert insert_space_before_capital('NationalHatDay') == 'National Hat Day'
            assert insert_space_before_capital('BagelDay') == 'Bagel Day'


def test_handler_success(mock_env_vars, mock_twitter_creds, s3_event, lambda_context):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.query.return_value = {
            'Items': [{'job_id': {'S': 'test'}, 'timestamp': {'N': '123'}}]
        }
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_twitter_creds)
        }

        def client_factory(service):
            if service == 's3':
                return mock_s3
            if service == 'dynamodb':
                return mock_dynamodb
            return mock_secrets

        mock_boto.side_effect = client_factory

        with (
            patch('tweepy.Client') as mock_client,
            patch('tweepy.OAuth1UserHandler'),
            patch('tweepy.API') as mock_api_class,
            patch('os.chdir'),
        ):
            mock_api = Mock()
            mock_media = Mock()
            mock_media.media_id = 'media-id'
            mock_api.media_upload.return_value = mock_media
            mock_api_class.return_value = mock_api

            mock_twitter = Mock()
            mock_client.return_value = mock_twitter

            from main import handler

            response = handler(s3_event, lambda_context)

            assert response['statusCode'] == 200
            assert mock_s3.download_file.called
            assert mock_twitter.create_tweet.called
            assert mock_dynamodb.update_item.called


def test_handler_s3_failure(
    mock_env_vars, mock_twitter_creds, s3_event, lambda_context
):
    with patch('boto3.client') as mock_boto:
        mock_s3 = Mock()
        mock_s3.download_file.side_effect = Exception('S3 Error')
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_twitter_creds)
        }

        mock_boto.side_effect = lambda s: mock_s3 if s == 's3' else mock_secrets

        with (
            patch('tweepy.Client'),
            patch('tweepy.OAuth1UserHandler'),
            patch('tweepy.API'),
            patch('os.chdir'),
        ):
            from main import handler

            response = handler(s3_event, lambda_context)

            assert response['statusCode'] == 500


def test_handler_wrong_event(mock_env_vars, mock_twitter_creds, lambda_context):
    wrong_event = {
        'Records': [
            {'eventName': 'ObjectRemoved:Delete', 's3': {'object': {'key': 'test.jpg'}}}
        ]
    }

    with patch('boto3.client') as mock_boto:
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_twitter_creds)
        }
        mock_boto.return_value = mock_secrets

        with (
            patch('tweepy.Client'),
            patch('tweepy.OAuth1UserHandler'),
            patch('tweepy.API'),
            patch('os.chdir'),
        ):
            from main import handler

            response = handler(wrong_event, lambda_context)

            assert response['statusCode'] == 500


def test_update_dynamodb_record(mock_env_vars, mock_twitter_creds):
    with patch('boto3.client') as mock_boto:
        mock_dynamodb = Mock()
        mock_dynamodb.query.return_value = {
            'Items': [{'job_id': {'S': 'test.jpg'}, 'timestamp': {'N': '123'}}]
        }
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_twitter_creds)
        }

        mock_boto.side_effect = (
            lambda s: mock_dynamodb if s == 'dynamodb' else mock_secrets
        )

        with (
            patch('tweepy.Client'),
            patch('tweepy.OAuth1UserHandler'),
            patch('tweepy.API'),
        ):
            from main import update_dynamodb_record

            update_dynamodb_record('table', 'test.jpg', 'caption', 'posted')

            assert mock_dynamodb.query.called
            assert mock_dynamodb.update_item.called
