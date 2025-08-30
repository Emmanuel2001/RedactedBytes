import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const videoFile = formData.get("video") as File;

    if (!videoFile) {
      return NextResponse.json({ error: "No video file provided" }, { status: 400 });
    }

    if (!videoFile.type.startsWith("video/")) {
      return NextResponse.json({ error: "Invalid file type" }, { status: 400 });
    }

    // Send the original file directly; avoid extra buffering
    const redactionFormData = new FormData();
    redactionFormData.append("file", videoFile, videoFile.name);

    // Forward to FastAPI
    const apiUrl = process.env.REDACTION_API_URL || "http://localhost:8000/redact-video";
    const redactionResponse = await fetch(apiUrl, {
      method: "POST",
      body: redactionFormData,
    });

    if (!redactionResponse.ok) {
      throw new Error(`Redaction failed with status: ${redactionResponse.status}`);
    }

    const contentType = redactionResponse.headers.get("content-type") ?? "";

    // If FastAPI returns JSON (e.g., a URL), just pass it through
    if (contentType.includes("application/json")) {
      const data = await redactionResponse.json();
      return NextResponse.json({
        message: "Video redacted successfully",
        videoUrl: data.videoUrl || "",
      });
    }

    // Otherwise, proxy the video bytes back to the client
    return new NextResponse(redactionResponse.body, {
      status: 200,
      headers: {
        "Content-Type": contentType || "video/mp4",
        "Content-Disposition": `inline; filename="redacted-${videoFile.name}"`,
        "Cache-Control": "no-store",
      },
    });
  } catch (error: unknown) {
    console.error("Error processing video:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
    return NextResponse.json({ error: "Error processing video", details: errorMessage }, { status: 500 });
  }
}