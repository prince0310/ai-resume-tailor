import {
  useCallback,
  useId,
  useState,
} from "react";

import {
  FileText,
  RotateCcw,
  UploadCloud,
  CheckCircle2,
} from "lucide-react";


const MAX_SIZE_BYTES =
  15 * 1024 * 1024;


function formatFileSize(bytes) {

  if (bytes < 1024)
    return `${bytes} B`;

  if (bytes < 1024 * 1024)
    return `${(bytes / 1024).toFixed(1)} KB`;

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


export default function ResumeUploader({
  file,
  onFileSelect,
  onFileRemove,
}) {

  const [isDragging, setIsDragging] =
    useState(false);

  const inputId = useId();


  const validateAndSet =
    useCallback(
      (candidate) => {

        if (!candidate)
          return;

        if (
          candidate.type !==
          "application/pdf" &&
          !candidate.name
            .toLowerCase()
            .endsWith(".pdf")
        ) {

          onFileSelect(
            null,
            "Please upload a PDF file."
          );

          return;
        }


        if (
          candidate.size >
          MAX_SIZE_BYTES
        ) {

          onFileSelect(
            null,
            "PDF must be smaller than 15MB."
          );

          return;
        }


        onFileSelect(
          candidate,
          null
        );
      },
      [onFileSelect]
    );


  const handleDrop = (event) => {

    event.preventDefault();

    setIsDragging(false);

    validateAndSet(
      event.dataTransfer.files?.[0]
    );
  };


  const handleBrowse = (event) => {

    validateAndSet(
      event.target.files?.[0]
    );

    event.target.value = "";
  };


  if (file) {

    return (

      <div className="flex items-center gap-4 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.05] p-4">

        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-emerald-400/10 text-emerald-400">

          <FileText size={21} />

        </div>


        <div className="min-w-0 flex-1">

          <p
            className="truncate text-sm font-semibold text-white"
            title={file.name}
          >
            {file.name}
          </p>

          <p className="mt-0.5 text-xs text-white/35">
            {formatFileSize(file.size)}
          </p>

        </div>


        <div className="hidden items-center gap-1.5 text-xs font-medium text-emerald-400 sm:flex">

          <CheckCircle2 size={14} />

          Ready

        </div>


        <button
          type="button"
          onClick={onFileRemove}
          className="flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-2 text-xs font-medium text-white/50 transition hover:border-white/20 hover:bg-white/5 hover:text-white"
        >

          <RotateCcw size={13} />

          Change

        </button>

      </div>

    );
  }


  return (

    <label
      htmlFor={inputId}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() =>
        setIsDragging(false)
      }
      onDrop={handleDrop}
      className={`
        flex min-h-[285px]
        cursor-pointer
        flex-col
        items-center
        justify-center
        rounded-xl
        border
        border-dashed
        px-6
        text-center
        transition-all

        ${isDragging
          ? "border-violet-400 bg-violet-400/[0.08]"
          : "border-white/10 bg-white/[0.015] hover:border-white/20 hover:bg-white/[0.03]"
        }
      `}
    >

      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl border border-white/10 bg-white/[0.05]">

        <UploadCloud
          size={25}
          className="text-violet-300"
        />

      </div>


      <p className="font-semibold text-white">
        Drop your resume here
      </p>


      <p className="mt-1 text-sm text-white/35">
        or click to browse
      </p>


      <div className="mt-6 rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5">

        <span className="text-[11px] font-medium text-white/35">
          PDF · Max 15MB · Text-based
        </span>

      </div>


      <input
        id={inputId}
        type="file"
        accept="application/pdf,.pdf"
        onChange={handleBrowse}
        className="sr-only"
      />

    </label>
  );
}