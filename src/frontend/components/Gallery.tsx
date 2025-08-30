"use client";

import { ReloadIcon } from "@radix-ui/react-icons";

interface GalleryProps {
  previews: string[];
  processedImages: string[];
  isLoading?: boolean;
  className?: string;
  mediaType?: "image" | "video"
}

export default function Gallery({
  previews = [],
  processedImages = [],
  isLoading = false,
  className = "",
  mediaType = "image"
}: GalleryProps) {
  // Get the latest image regardless of source
  const latestMedia =
    previews.length > 0
      ? previews[previews.length - 1]
      : processedImages.length > 0
      ? processedImages[processedImages.length - 1]
      : null;

  if (isLoading) {
    return (
      <div
        className={`h-full min-h-[400px] bg-gray-100 dark:bg-neutral-700/20 rounded-lg flex flex-col items-center justify-center w-full shadow-xl ${className}`}
      >
        <ReloadIcon className="h-12 w-12 text-gray-400 animate-spin mb-3" />
        <p className="text-gray-500 dark:text-gray-400 text-xl mb-4">
          Processing media...
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          Please wait while we process your media
        </p>
      </div>
    );
  }

  return (
    <div
      className={`h-full min-h-[400px] bg-gray-100 dark:bg-neutral-700/20 rounded-lg flex flex-col w-full shadow-xl ${className}`}
    >
      {!latestMedia ? (
        <div className="flex flex-col items-center justify-center flex-grow">
          <p className="text-gray-500 dark:text-gray-400 text-xl mb-4">
            No media to display
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Upload an media to view it here
          </p>
        </div>
      ) : (
        <div className="flex items-center justify-center w-full h-full p-4">
          <div className="relative max-h-full max-w-full rounded-lg overflow-hidden">
            {mediaType === "image" ? (
              <img
                src={latestMedia}
                alt="Displayed image"
                className="object-contain max-h-[calc(100vh-200px)] max-w-full"
              />
            ) : (
              <video
                src={latestMedia}
                controls={true}
                className="object-contain max-h-[calc(100vh-200px)] max-w-full"
                style={{ display: 'block' }}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}