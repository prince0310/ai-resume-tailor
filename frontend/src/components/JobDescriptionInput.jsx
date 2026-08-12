import { useId } from "react";
import { FileText, Info } from "lucide-react";

export default function JobDescriptionInput({
  value,
  onChange,
}) {
  const id = useId();

  return (
    <div>
      <label
        htmlFor={id}
        className="sr-only"
      >
        Job description
      </label>

      <div className="relative">

        <textarea
          id={id}
          value={value}
          onChange={(e) =>
            onChange(e.target.value)
          }
          placeholder="Paste the complete job description here..."
          rows={12}
          className="min-h-[285px] w-full resize-none rounded-xl border border-white/10 bg-white/[0.02] p-4 text-sm leading-6 text-white outline-none placeholder:text-white/25 transition focus:border-violet-400/50 focus:bg-white/[0.035]"
        />

        {!value && (
          <div className="pointer-events-none absolute bottom-5 left-5 flex items-center gap-2 text-[11px] text-white/20">
            <FileText size={13} />
            <span>
              Paste the full job description
            </span>
          </div>
        )}

      </div>

      <div className="mt-3 flex items-center justify-between gap-4">

        <p className="flex items-center gap-1.5 text-xs text-white/30">

          <Info
            size={13}
            className="text-violet-400/70"
          />

          Include the full JD for better matching.

        </p>

        <span className="shrink-0 font-mono text-[10px] text-white/25">

          {value.length.toLocaleString()} chars

        </span>

      </div>

    </div>
  );
}