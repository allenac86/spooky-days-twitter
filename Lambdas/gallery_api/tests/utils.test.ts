const mockSend = jest.fn();

jest.mock('@aws-sdk/client-s3', () => {
  return {
    S3Client: jest.fn().mockImplementation(() => ({
      send: mockSend,
    })),
    ListObjectsV2Command: jest.fn(),
  };
});

jest.mock('@aws-sdk/client-secrets-manager', () => {
  return {
    SecretsManagerClient: jest.fn().mockImplementation(() => ({
      send: mockSend,
    })),
    GetSecretValueCommand: jest.fn(),
  };
});

jest.mock('twitter-api-v2', () => {
  return {
    TwitterApi: jest.fn().mockImplementation(() => ({
      v2: {
        me: jest.fn(),
      },
    })),
  };
});

import { TwitterApi } from 'twitter-api-v2';

const mockTwitterApi = (TwitterApi as unknown) as jest.Mock;


describe('listCurrentImages', () => {
  let utils: any;

  beforeEach(() => {
    jest.resetModules();
    utils = require('../src/utils');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('returns empty array if S3 returns no contents', async () => {
    mockSend.mockResolvedValueOnce({ Contents: [] });
    const result = await utils.listAllImages('test-bucket');
    expect(result).toEqual([]);
  });

  it('filters out objects with keys ending in "/"', async () => {
    mockSend.mockResolvedValueOnce({
      Contents: [
        { Key: 'images/foo.jpg', Size: 123, LastModified: new Date('2024-01-01') },
        { Key: 'images/bar/', Size: 0, LastModified: new Date('2024-01-02') },
      ],
    });
    const result = await utils.listAllImages('test-bucket');
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe('images/foo.jpg');
  });

  it('returns correct metadata for valid objects', async () => {
    mockSend.mockResolvedValueOnce({
      Contents: [
        { Key: 'images/foo.jpg', Size: 123, LastModified: new Date('2024-01-01T12:00:00Z') },
      ],
    });
    const result = await utils.listAllImages('test-bucket');
    expect(result[0]).toEqual({
      key: 'images/foo.jpg',
      size: 123,
      lastModified: '2024-01-01T12:00:00.000Z',
    });
  });

  it('throws on S3 error', async () => {
    mockSend.mockRejectedValueOnce(new Error('S3 error'));
    await expect(utils.listAllImages('test-bucket')).rejects.toThrow('S3 error');
  });
});
