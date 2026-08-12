import { useCallback, useRef, useState } from "react";

import {
  ArrowRight,
  Check,
  FileText,
  Lock,
  Sparkles,
  Target,
} from "lucide-react";

import Header from "./components/Header.jsx";
import ResumeUploader from "./components/ResumeUploader.jsx";
import JobDescriptionInput from "./components/JobDescriptionInput.jsx";
import ProcessingState from "./components/ProcessingState.jsx";
import SuccessState from "./components/SuccessState.jsx";
import ErrorMessage from "./components/ErrorMessage.jsx";

import { tailorResume } from "./services/api.js";


const STAGE = {
  FORM: "form",
  PROCESSING: "processing",
  SUCCESS: "success",
};


export default function App() {

  const [stage, setStage] =
    useState(STAGE.FORM);

  const [file, setFile] =
    useState(null);

  const [jobDescription, setJobDescription] =
    useState("");

  const [error, setError] =
    useState(null);

  const [processingDone, setProcessingDone] =
    useState(false);


  // Store the backend-generated PDF URL
  const resultUrlRef =
    useRef(null);


  const canSubmit =
    Boolean(file) &&
    jobDescription.trim().length > 0;


  // ==========================================
  // File Selection
  // ==========================================

  const handleFileSelect =
    useCallback((selectedFile, fileError) => {

      setError(fileError || null);

      if (selectedFile) {
        setFile(selectedFile);
      }

    }, []);


  // ==========================================
  // Submit
  // ==========================================

  const handleSubmit =
    useCallback(async (event) => {

      event.preventDefault();


      if (!file) {

        setError(
          "Upload your resume PDF to continue."
        );

        return;
      }


      if (!jobDescription.trim()) {

        setError(
          "Paste the job description to continue."
        );

        return;
      }


      setError(null);

      setProcessingDone(false);

      resultUrlRef.current = null;

      setStage(
        STAGE.PROCESSING
      );


      try {

        const downloadUrl =
          await tailorResume(
            file,
            jobDescription,
            (progressData) => {

              console.log(
                "Backend progress:",
                progressData
              );

            }
          );


        resultUrlRef.current =
          downloadUrl;


        setProcessingDone(true);


        setTimeout(() => {

          setStage(
            STAGE.SUCCESS
          );

        }, 600);


      } catch (err) {

        console.error(err);

        setError(
          err?.message ||
          "Something went wrong while tailoring your resume."
        );

        setStage(
          STAGE.FORM
        );

      }

    }, [
      file,
      jobDescription,
    ]);


  // ==========================================
  // Download
  // ==========================================

  const handleDownload =
    useCallback(async () => {

      if (!resultUrlRef.current) {
        return;
      }


      try {

        const response =
          await fetch(
            resultUrlRef.current
          );


        if (!response.ok) {

          throw new Error(
            "Unable to download the generated resume."
          );

        }


        const blob =
          await response.blob();


        const url =
          URL.createObjectURL(
            blob
          );


        const anchor =
          document.createElement(
            "a"
          );


        anchor.href = url;

        anchor.download =
          "tailored_resume.pdf";


        document.body.appendChild(
          anchor
        );

        anchor.click();

        document.body.removeChild(
          anchor
        );


        URL.revokeObjectURL(
          url
        );

      } catch (err) {

        console.error(err);

        setError(
          err?.message ||
          "Unable to download the generated resume."
        );

      }

    }, []);


  // ==========================================
  // Reset
  // ==========================================

  const reset =
    useCallback(() => {

      resultUrlRef.current =
        null;

      setFile(null);

      setJobDescription("");

      setError(null);

      setProcessingDone(false);

      setStage(
        STAGE.FORM
      );

    }, []);


  // ==========================================
  // PROCESSING SCREEN
  // ==========================================

  if (
    stage === STAGE.PROCESSING
  ) {

    return (

      <div className="min-h-screen bg-[#08090b]">

        <Header />

        <main className="mx-auto flex min-h-[calc(100vh-81px)] max-w-3xl items-center px-5 py-16">

          <ProcessingState
            isComplete={processingDone}
          />

        </main>

      </div>

    );
  }


  // ==========================================
  // SUCCESS SCREEN
  // ==========================================

  if (
    stage === STAGE.SUCCESS
  ) {

    return (

      <div className="min-h-screen bg-[#08090b]">

        <Header />

        <main className="mx-auto flex min-h-[calc(100vh-81px)] max-w-3xl items-center px-5 py-16">

          <SuccessState
            onDownload={handleDownload}
            onReset={reset}
          />

        </main>

      </div>

    );
  }


  // ==========================================
  // FORM SCREEN
  // ==========================================

  return (

    <div className="min-h-screen bg-[#08090b]">

      <Header />


      <main className="mx-auto max-w-7xl px-5 pb-20 pt-16 sm:px-8 lg:pt-24">


        {/* HERO */}

        <section className="mx-auto max-w-4xl text-center">

          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/[0.07] px-3.5 py-1.5">

            <Sparkles
              size={14}
              className="text-violet-300"
            />

            <span className="text-xs font-medium text-violet-200">
              AI resume optimization
            </span>

          </div>


          <h1 className="font-display text-5xl font-semibold leading-[1.02] tracking-[-0.04em] text-white sm:text-6xl lg:text-7xl">

            Tailor your resume.

            <br />

            <span className="bg-gradient-to-r from-violet-300 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
              Keep your story.
            </span>

          </h1>


          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-white/45 sm:text-lg">

            Match your existing resume to any job description
            without rebuilding it from scratch.

            <span className="text-white/70">
              {" "}Your original PDF stays intact.
            </span>

          </p>


          <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-3 text-xs text-white/40">

            <Feature text="No invented experience" />

            <Feature text="No new bullets" />

            <Feature text="Original layout preserved" />

          </div>

        </section>


        {/* WORKSPACE */}

        <form
          onSubmit={handleSubmit}
          className="mx-auto mt-16 max-w-6xl"
        >

          {error && (

            <div className="mb-6">

              <ErrorMessage
                message={error}
                onDismiss={() =>
                  setError(null)
                }
              />

            </div>

          )}


          <div className="relative grid gap-5 lg:grid-cols-[1fr_1fr]">


            {/* RESUME */}

            <div className="group rounded-2xl border border-white/[0.09] bg-white/[0.035] p-5 backdrop-blur-xl transition hover:border-white/[0.14] sm:p-6">

              <div className="mb-5 flex items-center justify-between">

                <div className="flex items-center gap-3">

                  <StepNumber number="01" />

                  <div>

                    <h2 className="font-semibold text-white">
                      Your resume
                    </h2>

                    <p className="text-xs text-white/35">
                      Upload your existing PDF
                    </p>

                  </div>

                </div>


                <FileText
                  size={18}
                  className="text-white/20"
                />

              </div>


              <ResumeUploader
                file={file}
                onFileSelect={
                  handleFileSelect
                }
                onFileRemove={() =>
                  setFile(null)
                }
              />

            </div>


            {/* JOB DESCRIPTION */}

            <div className="group rounded-2xl border border-white/[0.09] bg-white/[0.035] p-5 backdrop-blur-xl transition hover:border-white/[0.14] sm:p-6">

              <div className="mb-5 flex items-center justify-between">

                <div className="flex items-center gap-3">

                  <StepNumber number="02" />

                  <div>

                    <h2 className="font-semibold text-white">
                      Job description
                    </h2>

                    <p className="text-xs text-white/35">
                      Tell AI what you're applying for
                    </p>

                  </div>

                </div>


                <Target
                  size={18}
                  className="text-white/20"
                />

              </div>


              <JobDescriptionInput
                value={jobDescription}
                onChange={
                  setJobDescription
                }
              />

            </div>

          </div>


          {/* CTA */}

          <div className="mt-8 flex flex-col items-center">

            <button
              type="submit"
              disabled={!canSubmit}
              className="group relative flex w-full max-w-md items-center justify-center gap-3 overflow-hidden rounded-xl bg-white px-7 py-4 text-sm font-bold text-black transition-all hover:-translate-y-0.5 hover:shadow-[0_20px_60px_rgba(139,92,246,0.22)] disabled:cursor-not-allowed disabled:opacity-30"
            >

              <span>
                Tailor my resume
              </span>

              <ArrowRight
                size={18}
                className="transition-transform group-hover:translate-x-1"
              />

            </button>


            <div className="mt-4 flex items-center gap-2 text-[11px] text-white/25">

              <Lock size={11} />

              Your resume is processed securely

            </div>

          </div>

        </form>

      </main>


      <footer className="border-t border-white/[0.06] py-8 text-center">

        <p className="text-xs text-white/25">

          Resume Tailor AI · Edit your resume.
          Don't recreate it.

        </p>

      </footer>

    </div>
  );
}


// ==========================================
// Small UI Components
// ==========================================

function StepNumber({ number }) {

  return (

    <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/[0.05] font-mono text-[10px] font-bold text-white/45">

      {number}

    </span>

  );
}


function Feature({ text }) {

  return (

    <span className="flex items-center gap-1.5">

      <Check
        size={13}
        className="text-violet-400"
      />

      {text}

    </span>

  );
}