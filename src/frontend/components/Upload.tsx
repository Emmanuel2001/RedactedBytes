"use client";

import { ChangeEvent } from "react";
import { Button } from "@/components/ui/button";
import { UploadIcon, ReloadIcon } from "@radix-ui/react-icons";

interface UploadFormProps {
  onFilesChange: (files: File[]) => void;
  onUpload: () => void;
  disabled?: boolean;
  isUploading?: boolean;
  accept?: string; // Add this new prop
}

export default function UploadForm({
  onFilesChange,
  onUpload,
  disabled,
  isUploading,
  accept,
}: UploadFormProps) {
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    onFilesChange(Array.from(e.target.files));
  };

  return (
    <div className="flex flex-col items-center gap-4 justify-center">
      {/* Drag-and-Drop / File Input */}
      <div className="relative w-full max-w-lg border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept={accept || "image/*,video/*"}
          multiple
          onChange={handleFileChange}
          className="absolute w-full h-full opacity-0 cursor-pointer"
          disabled={isUploading}
        />
        <UploadIcon className="mx-auto mb-2 text-gray-400" />
        <p className="text-gray-500">Click here to select</p>
      </div>

      {/* Upload Button */}
      <Button
        onClick={onUpload}
        disabled={disabled || isUploading}
        variant="secondary"
        size="lg"
        className="relative"
      >
        {isUploading ? (
          <>
            <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          "Upload Media"
        )}
      </Button>
    </div>
  );
}