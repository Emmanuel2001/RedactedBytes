export async function uploadImages(files: File[]): Promise<{ id: string; url: string }[]> {
  const formData = new FormData();
  
  files.forEach((file, index) => {
    formData.append(`image_${index}`, file);
  });

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status: ${response.status}`);
    }

    const data = await response.json();
    return data.images;
  } catch (error) {
    console.error('Error uploading images:', error);
    throw error;
  }
}