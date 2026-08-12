import {
  FileEdit,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-white/[0.07] bg-[#08090b]/80 backdrop-blur-xl">

      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">

        <div className="flex items-center gap-3">

          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.06]">

            <div className="absolute inset-0 rounded-xl bg-violet-500/20 blur-lg" />

            <FileEdit
              size={19}
              className="relative text-violet-300"
            />

          </div>

          <div>

            <div className="font-display text-sm font-semibold tracking-tight text-white">
              Resume Tailor
            </div>

            <div className="text-[11px] text-white/40">
              AI-powered resume optimization
            </div>

          </div>

        </div>


        <div className="hidden items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/[0.06] px-3 py-1.5 sm:flex">

          <ShieldCheck
            size={13}
            className="text-emerald-400"
          />

          <span className="text-xs font-medium text-emerald-300">
            Your original PDF stays intact
          </span>

        </div>

      </div>

    </header>
  );
}