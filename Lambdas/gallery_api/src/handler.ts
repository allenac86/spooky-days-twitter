import {
  getTwitterData,
  listAllImages,
  validateEnv,
  getPresignedUrl
} from './utils.js';
import { Logger } from '@aws-lambda-powertools/logger';

const BUCKET: string = process.env.IMAGE_BUCKET_NAME!;
const ORIGIN_HEADER_NAME: string = process.env.ORIGIN_HEADER_NAME!;
const ORIGIN_HEADER_VALUE: string = process.env.ORIGIN_HEADER_VALUE!;
const logger = new Logger({ serviceName: 'gallery_api_lambda' });

export const handler = async (event: any, context: any) => {
  const envError = validateEnv(logger);

  if (envError) return envError;

  const path = event.path;
  const originHeader = event?.headers
    ? event.headers[ORIGIN_HEADER_NAME]
    : undefined;

  logger.info('Handler invoked', { path, bucket: BUCKET });

  if (!path) {
    logger.error('No path provided in event');

    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'No path provided on the event' }),
    };
  }


  if (!originHeader || originHeader !== ORIGIN_HEADER_VALUE) {
    logger.warn('Forbidden - missing or invalid origin header',
      { hasHeader: !!originHeader });

    return {
      statusCode: 403,
      body: JSON.stringify({ error: 'Forbidden' })
    };
  }

  try {
    if (path === '/api/get-image-data') {
      const images = await listAllImages(BUCKET);

      logger.info(`Retrieved ${images.length} images from S3`);
      logger.info('Generating presigned URLs for images');

      const imagesWithUrls = await Promise.all(images.map(async (img) => ({
        ...img,
        url: await getPresignedUrl(BUCKET, img.key, 900),
      })));

      logger.info('Images retrieved successfully', {
        imageCount: imagesWithUrls.length
      });

      return {
        statusCode: 200,
        body: JSON.stringify({ images: imagesWithUrls }),
      };
    } else if (path === '/api/get-twitter-data') {
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
