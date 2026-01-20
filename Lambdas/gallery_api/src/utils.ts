import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';
import type { ImageMetadata } from './types.js';
import { Logger } from '@aws-lambda-powertools/logger';
import {
  SecretsManagerClient,
  GetSecretValueCommand
} from '@aws-sdk/client-secrets-manager';
import { TwitterApi } from 'twitter-api-v2';

const logger = new Logger({ serviceName: 'gallery_api_lambda' });
const s3 = new S3Client({});
const secretsClient = new SecretsManagerClient({});
const secretArn = process.env.TWITTER_SECRET_ARN;

let twitterClient: TwitterApi | null = null;

export async function listAllImages(bucket: string): Promise<ImageMetadata[]> {
  logger.info('Listing images from S3', { bucket, prefix: 'images/' });

  const command = new ListObjectsV2Command({
    Bucket: bucket,
    Prefix: 'images/',
  });

  try {
    const result = await s3.send(command);
    const imageCount = result.Contents 
      ? result.Contents.filter(obj => !obj.Key?.endsWith('/')).length
      : 0;

    logger.info('Images listed successfully', { bucket, imageCount });

    if (!result.Contents) return [];

    return result.Contents
      .filter(obj => !obj.Key?.endsWith('/'))
      .map(obj => (
        {
          key: obj.Key!,
          size: obj.Size ?? 0,
          lastModified: obj.LastModified?.toISOString() ?? '',
        }
    ));
  } catch (err) {
    logger.error('Failed to list images from S3',
      { bucket, error: (err as Error).message });

    throw err;
  }
}

async function getTwitterCredentials(): Promise<{
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
}> {
  if (!secretArn) {
    logger.error('TWITTER_SECRET_ARN environment variable not set');

    throw new Error('TWITTER_SECRET_ARN not set');
  }

  try {
    const command = new GetSecretValueCommand({ SecretId: secretArn });
    const response = await secretsClient.send(command);
    const credentials = JSON.parse(response.SecretString!);
    const apiKey = credentials.API_KEY; 
    const apiSecret = credentials.API_SECRET;
    const accessToken = credentials.ACCESS_TOKEN;
    const accessTokenSecret = credentials.ACCESS_TOKEN_SECRET;
    
    if (!apiKey || !apiSecret || !accessToken || !accessTokenSecret) {
      throw new Error('Missing required Twitter credentials in secret');
    }
    
    logger.info('Twitter credentials retrieved successfully');

    return { apiKey, apiSecret, accessToken, accessTokenSecret };
  } catch (err) {
    logger.error('Error retrieving Twitter credentials',
      { error: (err as Error).message });

    throw err;
  }
}

async function getTwitterClient(): Promise<TwitterApi> {
  if (!twitterClient) {
    const {
      apiKey,
      apiSecret,
      accessToken,
      accessTokenSecret
    } = await getTwitterCredentials();

    twitterClient = new TwitterApi({
      appKey: apiKey,
      appSecret: apiSecret,
      accessToken: accessToken,
      accessSecret: accessTokenSecret,
    });

    logger.info('TwitterApi client initialized');
  }

  return twitterClient;
}

export async function getTwitterData(): Promise<any> {
  logger.info('Fetching Twitter user data');

  try {
    const client = await getTwitterClient();
    const user = await client.v2.me({ 'user.fields': ['public_metrics'] });

    logger.info('Twitter user data retrieved successfully',
      {
        username: user.data.username,
        tweetCount: user.data.public_metrics?.tweet_count
      });

    return user.data;
  } catch (err) {
    logger.error('Failed to fetch Twitter user data',
      { error: (err as Error).message });

    throw err;
  }
}
