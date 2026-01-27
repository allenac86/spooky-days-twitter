import React, { useEffect, useState } from 'react';
import Button from 'react-bootstrap/Button';

type ImageMetadata = {
  key: string;
  size: number;
  lastModified: string;
  url?: string;
};

export async function fetchImages(): Promise<ImageMetadata[]> {
  const res = await fetch('/api/get-image-data', { cache: 'no-store' });

  if (!res.ok) {
    throw new Error(`fetch failed ${res.status}`);
  }

  const body = await res.json();

  return body.images || [];
}

export default function Gallery() {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ITEMS_PER_PAGE = 6;

  useEffect(() => {
    if (images.length === 0) {
      setLoading(true);

      fetchImages()
        .then((imgs) => {
          setImages(imgs);
        })
        .catch((err: any) => {
          setError(err.message || 'Fetch error');
        })
        .finally(() => {
          setLoading(false);
        });

      return;
    }

    const totalPages = Math.max(1, Math.ceil(images.length / ITEMS_PER_PAGE));

    if (page < 0) {
      setPage(0);
    }

    if (page >= totalPages) {
      setPage(totalPages - 1);
    }
  }, [page, images]);

  function prev(): void {
    const totalPages = Math.max(1, Math.ceil(images.length / ITEMS_PER_PAGE));

    setPage((p) => {
      if (p <= 0) {
        return totalPages - 1;
      }

      return p - 1;
    });
  }

  function next(): void {
    const totalPages = Math.max(1, Math.ceil(images.length / ITEMS_PER_PAGE));

    setPage((p) => {
      if (p >= totalPages - 1) {
        return 0;
      }

      return p + 1;
    });
  }

  if (loading) {
    return (
      <div
        className="text-center p-6"
      >
        Loading gallery…
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="text-center p-6 text-danger"
      >
        {error}
      </div>
    );
  }

  if (!images.length) {
    return (
      <div
        className="text-center p-6"
      >
        No images found.
      </div>
    );
  }

  const start = page * ITEMS_PER_PAGE;
  const pageImages = images.slice(start, start + ITEMS_PER_PAGE);
  const totalPages = Math.max(1, Math.ceil(images.length / ITEMS_PER_PAGE));

  return (
    <div
      className="flex justify-center items-center min-h-[60vh] p-6"
    >
      <div
        className="w-full max-w-6xl"
      >
        <div
          className="flex justify-between items-center mb-3"
        >
          <div
            className="text-sm text-gray-300"
          >
            Page {page + 1} / {totalPages}
          </div>

          <div
            className="flex gap-2"
          >
            <Button
              variant="secondary"
              size="sm"
              onClick={prev}
              disabled={images.length === 0}
            >
              Prev
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={next}
              disabled={images.length === 0}
            >
              Next
            </Button>
          </div>
        </div>

        <div
          className="grid grid-cols-1
            sm:grid-cols-3 gap-6 justify-center
            items-center place-items-center"
        >
          {pageImages.map((img) => {
            return (
              <div
                key={img.key} className="w-full flex items-center justify-center"
              >
                {img.url
                  ? (
                    <img
                      src={img.url}
                      alt={img.key}
                      className="max-w-full h-auto rounded shadow-lg object-contain"
                      style={{ display: 'block' }}
                    />
                  )
                  : (
                    <div
                      className="text-gray-300 p-4 rounded"
                    >No URL for image
                    </div>
                  )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
