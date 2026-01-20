import { getTwitterData, listAllImages } from './utils.js';
import { Logger } from '@aws-lambda-powertools/logger';

const BUCKET = process.env.IMAGE_BUCKET_NAME!;
const logger = new Logger({ serviceName: 'gallery_api_lambda' });const handler = async (event: any, context: any) => {
  const path = event.path;

  logger.info('Handler invoked', { path, bucket: BUCKET });

  if (!path) {
    logger.error('No path provided in event');

    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'No path provided on the event' }),
    };
  }

  if (!BUCKET) {
    logger.error('IMAGE_BUCKET_NAME environment variable not set');

    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'IMAGE_BUCKET_NAME not set' }),
    };
  }

  try {
    if (path === '/get-image-data') {
      const images = await listAllImages(BUCKET);

      logger.info('Images retrieved successfully', { imageCount: images.length });

      return {
        statusCode: 200,
        body: JSON.stringify({ images }),
      };
    } else if (path === '/get-twitter-data') {
      const twitterData = await getTwitterData();

      logger.info('Twitter data retrieved successfully', { userId: twitterData.id });

      return {
        statusCode: 200,
        body: JSON.stringify({ twitterData }),
      };
    } else {
      logger.warn('Unknown path requested', { path });

      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'Endpoint not found' }),
      };
    }
  } catch (err) {
    logger.error('Operation failed', { path, error: (err as Error).message });

    return {
      statusCode: 500,
      body: JSON.stringify({ error: (err as Error).message }),
    };
  }
};

export const lambdaHandler = handler;
