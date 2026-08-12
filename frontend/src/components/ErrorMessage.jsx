import {
  AlertTriangle,
  X,
} from "lucide-react";


export default function ErrorMessage({
  message,
  onDismiss,
}) {

  if (!message)
    return null;


  return (

    <div className="flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3.5 text-red-300">

      <AlertTriangle
        size={18}
        className="mt-0.5 shrink-0"
      />


      <p className="flex-1 text-sm leading-5">
        {message}
      </p>


      {onDismiss && (

        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="rounded-md p-1 text-red-300/50 transition hover:bg-red-400/10 hover:text-red-300"
        >

          <X size={15} />

        </button>

      )}

    </div>
  );
}