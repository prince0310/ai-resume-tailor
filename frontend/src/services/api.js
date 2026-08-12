
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

export async function tailorResume(
  resumeFile,
  jobDescription,
  optionalDetails = {},
  onProgress = null
) {
  // ==========================================
  // Validation
  // ==========================================

  if (!resumeFile) {
    throw new Error(
      "Resume PDF is required."
    );
  }

  if (!jobDescription?.trim()) {
    throw new Error(
      "Job description is required."
    );
  }


  // ==========================================
  // Optional Details
  // ==========================================

  const {
    targetRole = "",
    githubUrl = "",
    linkedinUrl = "",
  } = optionalDetails;


  // ==========================================
  // Form Data
  // ==========================================

  const formData = new FormData();

  formData.append(
    "file",
    resumeFile,
    resumeFile.name
  );

  formData.append(
    "jd",
    jobDescription
  );

  if (targetRole?.trim()) {
    formData.append(
      "target_role",
      targetRole.trim()
    );
  }

  if (githubUrl?.trim()) {
    formData.append(
      "github_url",
      githubUrl.trim()
    );
  }

  if (linkedinUrl?.trim()) {
    formData.append(
      "linkedin_url",
      linkedinUrl.trim()
    );
  }


  // ==========================================
  // Backend Request
  // ==========================================

  let response;

  try {

    response = await fetch(
      `${API_BASE_URL}/api/generate`,
      {
        method: "POST",
        body: formData,
      }
    );

  } catch (error) {

    console.error(
      "Backend connection failed:",
      error
    );

    throw new Error(
      "Cannot connect to the Resume Tailor backend. Make sure FastAPI is running on port 8000."
    );
  }


  // ==========================================
  // HTTP Error
  // ==========================================

  if (!response.ok) {

    let message =
      `Backend returned HTTP ${response.status}.`;

    try {

      const data =
        await response.json();

      if (data?.detail) {
        message = data.detail;
      }

    } catch {
      // Response wasn't JSON.
    }

    throw new Error(message);
  }


  // ==========================================
  // Validate SSE Response
  // ==========================================

  const contentType =
    response.headers.get(
      "content-type"
    );

  if (
    !contentType ||
    !contentType.includes(
      "text/event-stream"
    )
  ) {

    const responseText =
      await response.text();

    console.error(
      "Unexpected backend response:",
      responseText
    );

    throw new Error(
      "The backend did not return a progress stream."
    );
  }


  // ==========================================
  // Read SSE Stream
  // ==========================================

  if (!response.body) {
    throw new Error(
      "The backend returned an empty response."
    );
  }


  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();


  let buffer = "";
  let downloadUrl = null;


  try {

    while (true) {

      const {
        value,
        done,
      } = await reader.read();


      if (done) {
        break;
      }


      buffer += decoder.decode(
        value,
        {
          stream: true,
        }
      );


      // SSE events are separated by
      // two newline characters.
      const events =
        buffer.split("\n\n");


      // Keep incomplete event in buffer.
      buffer =
        events.pop() || "";


      for (const event of events) {

        const lines =
          event.split("\n");


        for (const line of lines) {

          if (
            !line.startsWith("data:")
          ) {
            continue;
          }


          const jsonString =
            line
              .slice(5)
              .trim();


          if (!jsonString) {
            continue;
          }


          let data;

          try {

            data =
              JSON.parse(
                jsonString
              );

          } catch (error) {

            console.error(
              "Invalid SSE JSON:",
              jsonString
            );

            continue;
          }


          // ==========================================
          // Backend Error
          // ==========================================

          if (data.error) {

            throw new Error(
              data.error
            );
          }


          // ==========================================
          // Progress
          // ==========================================

          if (
            typeof onProgress ===
            "function"
          ) {

            onProgress(data);
          }


          // ==========================================
          // Finished
          // ==========================================

          if (
            data.step === "Finished" &&
            data.download_url
          ) {

            downloadUrl =
              `${API_BASE_URL}${data.download_url}`;
          }

        }
      }
    }

  } finally {

    reader.releaseLock();

  }


  // ==========================================
  // Verify Download URL
  // ==========================================

  if (!downloadUrl) {

    throw new Error(
      "Resume generation completed but no download URL was returned."
    );
  }


  return downloadUrl;
}