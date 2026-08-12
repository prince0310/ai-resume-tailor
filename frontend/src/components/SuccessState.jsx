import {
  Check,
  Download,
  RotateCcw,
  Sparkles,
} from "lucide-react";


export default function SuccessState({
  onDownload,
  onReset,
}) {

  return (

    <div className="w-full animate-fade-up text-center">

      <div className="mx-auto mb-7 flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.08]">

        <Check
          size={28}
          className="text-emerald-400"
          strokeWidth={2.5}
        />

      </div>


      <div className="mb-8">

        <div className="mb-3 flex items-center justify-center gap-2">

          <Sparkles
            size={14}
            className="text-violet-300"
          />

          <span className="text-xs font-medium uppercase tracking-wider text-violet-300">
            Optimization complete
          </span>

        </div>


        <h1 className="font-display text-4xl font-semibold tracking-tight text-white">

          Your resume is ready.

        </h1>


        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-white/35">

          Relevant content was tailored to the
          job description while keeping your
          original PDF structure intact.

        </p>

      </div>


      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

        <div className="flex items-center gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] p-4 text-left">

          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-violet-400/10">

            <Sparkles
              size={19}
              className="text-violet-300"
            />

          </div>


          <div className="min-w-0 flex-1">

            <p className="text-sm font-medium text-white">
              tailored_resume.pdf
            </p>

            <p className="mt-0.5 text-xs text-white/30">
              Original layout preserved
            </p>

          </div>


          <Check
            size={17}
            className="text-emerald-400"
          />

        </div>


        <button
          type="button"
          onClick={onDownload}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-white px-5 py-3.5 text-sm font-bold text-black transition hover:-translate-y-0.5 hover:shadow-[0_16px_45px_rgba(139,92,246,0.2)]"
        >

          <Download size={17} />

          Download tailored resume

        </button>


        <button
          type="button"
          onClick={onReset}
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm font-medium text-white/45 transition hover:border-white/20 hover:bg-white/[0.03] hover:text-white"
        >

          <RotateCcw size={15} />

          Tailor another resume

        </button>

      </div>

    </div>
  );
}