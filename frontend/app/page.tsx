"use client";

import { useState, useEffect } from "react";
import Background from "../components/Background";
import UploadForm from "../components/Upload";
import Gallery from "../components/Gallery";
import { Button } from "@/components/ui/button";
import { DownloadIcon } from "@radix-ui/react-icons";

export default function HomePage() {
  const [images, setImages] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [processedImages, setProcessedImages] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFilesChange = (files: File[]) => {
    setImages(files);
    const filePreviews = files.map((file) => URL.createObjectURL(file));
    setPreviews(filePreviews);
  };

  const handleUpload = async () => {
    if (images.length === 0) return;

    setIsUploading(true);
    // Clear previews while uploading
    setPreviews([]);

    try {
      const formData = new FormData();
      images.forEach((image, index) => {
        formData.append(`image_${index}`, image);
      });

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Received response:", data);

      // Make sure imageUrls exists in the response
      if (!data.imageUrls || !Array.isArray(data.imageUrls)) {
        console.error("Invalid response format:", data);
        throw new Error("Invalid response format from server");
      }

      // Add new processed images to state
      setProcessedImages((prev) => [...prev, ...data.imageUrls]);

      // Clear selected images after successful upload
      setImages([]);
    } catch (error) {
      console.error("Error uploading images:", error);
      alert("Failed to process images. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const latestMedia =
    previews.length > 0
      ? previews[previews.length - 1]
      : processedImages.length > 0
      ? processedImages[processedImages.length - 1]
      : null;

  const handleDownload = () => {
    if (!latestMedia) return;
    
    // Create an anchor element and set properties for download
    const link = document.createElement('a');
    link.href = latestMedia;
    link.download = `redacted-image-${Date.now()}.jpg`; // Default filename
    
    // Append to body, click and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    return () => previews.forEach((url) => URL.revokeObjectURL(url));
  }, [previews]);

  return (
    <>
      <Background />
      <div className="flex min-h-screen w-full">
        {/* Main content wrapper */}
        <div className="flex-1 flex justify-center items-center">
          
          <main className="w-full p-8 text-center space-y-4 relative z-10">
            <div><h1>Image Redactor</h1></div>
            {/* Gallery - Always render the Gallery component */}
            <div className="flex-1 flex items-center justify-center w-full">
              <div className="w-full h-[70vh] max-w-7xl">
                <Gallery
                  previews={previews}
                  processedImages={processedImages}
                  isLoading={isUploading}
                />
              </div>
            </div>

            {/* Upload */}
            <div className="py-4 flex justify-center flex-col items-center gap-4">
              {/* Download Button */}
              {latestMedia && (
                <Button
                  onClick={handleDownload}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <DownloadIcon className="h-4 w-4" />
                  Download Media
                </Button>
              )}
              
              {/* Upload */}
              <div className="max-w-md w-full">
                <UploadForm
                  onFilesChange={handleFilesChange}
                  onUpload={handleUpload}
                  disabled={images.length === 0}
                  isUploading={isUploading}
                  accept="image/*"
                />
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  );
}