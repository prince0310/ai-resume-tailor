import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Check,
  Circle,
  FileSearch,
  Loader2,
  Sparkles,
} from "lucide-react";


const STEPS = [
  {
    key: "uploaded",
    label: "Resume received",
  },
  {
    key: "extracting",
    label: "Reading resume content",
  },
  {
    key: "analyzing",
    label: "Understanding the job description",
  },
  {
    key: "tailoring",
    label: "Finding the strongest matches",
  },
  {
    key: "updating",
    label: "Applying targeted edits",
  },
  {
    key: "preparing",
    label: "Preparing your tailored PDF",
  },
];


export default function ProcessingState({
  isComplete,
}) {

  const [activeIndex, setActiveIndex] =
    useState(0);

  const timeoutRef =
    useRef(null);


  useEffect(() => {

    const ceiling = isComplete
      ? STEPS.length - 1
      : STEPS.length - 2;


    if (activeIndex < ceiling) {

      timeoutRef.current =
        setTimeout(() => {

          setActiveIndex(
            (current) =>
              Math.min(
                current + 1,
                ceiling
              )
          );

        }, 1200);

    }


    if (
      isComplete &&
      activeIndex <
      STEPS.length - 1
    ) {

      timeoutRef.current =
        setTimeout(() => {

          setActiveIndex(
            STEPS.length - 1
          );

        }, 350);

    }


    return () =>
      clearTimeout(
        timeoutRef.current
      );

  }, [
    activeIndex,
    isComplete,
  ]);


  return (

    <div className="w-full animate-fade-up">

      {/* HEADER */}

      <div className="mb-8 text-center">

        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-400/20 bg-violet-400/[0.08]">

          <Sparkles
            size={23}
            className="text-violet-300"
          />

        </div>


        <h1 className="font-display text-3xl font-semibold tracking-tight text-white sm:text-4xl">

          Tailoring your resume

        </h1>


        <p className="mt-3 text-sm text-white/35">

          Analyzing your resume against the
          job requirements.

        </p>

      </div>


      {/* PROGRESS CARD */}

      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5 sm:p-7">

        <div className="mb-6 flex items-center justify-between">

          <div className="flex items-center gap-2">

            <FileSearch
              size={16}
              className="text-violet-300"
            />

            <span className="text-xs font-medium text-white/45">
              AI analysis
            </span>

          </div>


          <span className="text-xs text-white/25">
            {Math.min(
              activeIndex + 1,
              STEPS.length
            )}{" "}
            / {STEPS.length}
          </span>

        </div>


        <div className="mb-7 h-1 overflow-hidden rounded-full bg-white/[0.06]">

          <div
            className="h-full rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-400 transition-all duration-700"
            style={{
              width: `${((activeIndex + 1) /
                  STEPS.length) *
                100
                }%`,
            }}
          />

        </div>


        <div className="space-y-2">

          {STEPS.map(
            (step, index) => {

              const done =
                index < activeIndex;

              const active =
                index === activeIndex;


              return (

                <div
                  key={step.key}
                  className={`flex items-center gap-3 rounded-xl px-3 py-3 transition-all ${active
                      ? "bg-violet-400/[0.07]"
                      : ""
                    }`}
                >

                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${done
                        ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-400"
                        : active
                          ? "border-violet-400/20 bg-violet-400/10 text-violet-300"
                          : "border-white/[0.07] text-white/15"
                      }`}
                  >

                    {done ? (

                      <Check size={14} />

                    ) : active ? (

                      <Loader2
                        size={14}
                        className="animate-spin"
                      />

                    ) : (

                      <Circle
                        size={8}
                        fill="currentColor"
                      />

                    )}

                  </div>


                  <span
                    className={`text-sm ${done
                        ? "text-white/45"
                        : active
                          ? "font-medium text-white"
                          : "text-white/20"
                      }`}
                  >

                    {step.label}

                  </span>


                  {active && (

                    <span className="ml-auto text-[10px] text-violet-300/60">
                      Working
                    </span>

                  )}

                </div>

              );

            }
          )}

        </div>

      </div>


      <p className="mt-5 text-center text-[11px] text-white/20">

        Your original PDF structure is being preserved.

      </p>

    </div>
  );
}