import { NextResponse } from 'next/server';

// Use Node.js runtime
export const runtime = 'nodejs';

export async function POST(request: Request) {
  console.log('Upload API route called');
  
  try {
    const formData = await request.formData();
    console.log('FormData received');
    
    const images = Array.from(formData.entries())
      .filter(([key]) => key.startsWith('image_'))
      .map(([key, value]) => {
        console.log(`Found image with key: ${key}`);
        return value;
      });
    
    if (images.length === 0) {
      console.log('No images provided');
      return NextResponse.json({ 
        success: false, 
        error: 'No images provided' 
      }, { status: 400 });
    }
    
    console.log(`Processing ${images.length} images`);
    const imageUrls = [];
    
    // Process each image individually
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://api:8000';
    const baseUrl = `${pythonBackendUrl}/redact`;
    console.log(`Using backend URL: ${baseUrl}`);
    
    const fullUrl = `${baseUrl}`;
    console.log(`Full API URL: ${fullUrl}`);
    
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      console.log(`Processing image ${i+1}/${images.length}`);
      
      // Log image details if possible
      if (image instanceof File) {
        console.log(`Image type: ${image.type}, size: ${image.size} bytes`);
      } else {
        console.log('Image is not a File object');
      }
      
      // Create a new FormData for each image
      const imageFormData = new FormData();
      imageFormData.append('file', image);
      console.log('FormData created for image');
      
      try {
        // Send the image to the Python backend with query params
        console.log(`Sending request to: ${fullUrl}`);
        console.time(`Image ${i+1} processing time`);
        
        const pythonResponse = await fetch(fullUrl, {
          method: 'POST',
          body: imageFormData,
        });
        
        console.timeEnd(`Image ${i+1} processing time`);
        console.log(`Response received with status: ${pythonResponse.status}`);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text().catch(e => 'Could not read error response');
          console.error(`Error response: ${errorText}`);
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        // Get response headers
        console.log('Response headers:');
        pythonResponse.headers.forEach((value, key) => {
          console.log(`   ${key}: ${value}`);
        });
        
        // Get the processed image as array buffer
        const arrayBuffer = await pythonResponse.arrayBuffer();
        console.log(`Received array buffer of size: ${arrayBuffer.byteLength} bytes`);
        
        // Convert array buffer to base64
        const base64 = Buffer.from(arrayBuffer).toString('base64');
        const dataUrl = `data:image/png;base64,${base64}`;
        console.log(`Created data URL (length: ${dataUrl.length})`);
        
        imageUrls.push(dataUrl);
        console.log(`Successfully processed image ${i+1}`);
      } catch (imageError) {
        console.error(`Error processing image ${i+1}:`, imageError);
        throw imageError;
      }
    }
    
    console.log(`All images processed successfully (${imageUrls.length} total)`);
    return NextResponse.json({ 
      success: true, 
      imageUrls // Make sure this key matches what the client code expects
    });
  } catch (error) {
    console.error('Error processing images:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to process images'
    }, { status: 500 });
  }
}