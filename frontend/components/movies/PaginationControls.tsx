import Link from "next/link";

interface PaginationControlsProps {
  page: number;
  totalPages: number;
  createPageHref: (page: number) => string;
}

export default function PaginationControls({
  page,
  totalPages,
  createPageHref,
}: PaginationControlsProps) {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="flex flex-col items-center justify-between gap-4 rounded-3xl border border-white/10 bg-[#0d0d0d] px-5 py-4 text-sm text-white/65 sm:flex-row">
      <p>
        Page {page} of {totalPages}
      </p>

      <div className="flex items-center gap-3">
        <Link
          href={createPageHref(Math.max(1, page - 1))}
          aria-disabled={page <= 1}
          className={`inline-flex h-11 items-center justify-center rounded-2xl px-4 font-semibold transition ${
            page <= 1
              ? "pointer-events-none border border-white/10 text-white/25"
              : "border border-white/15 text-white hover:border-white/35 hover:bg-white/[0.04]"
          }`}
        >
          Previous
        </Link>
        <Link
          href={createPageHref(Math.min(totalPages, page + 1))}
          aria-disabled={page >= totalPages}
          className={`inline-flex h-11 items-center justify-center rounded-2xl px-4 font-semibold transition ${
            page >= totalPages
              ? "pointer-events-none border border-white/10 text-white/25"
              : "bg-[#E50914] text-white hover:bg-[#c50b14]"
          }`}
        >
          Next
        </Link>
      </div>
    </div>
  );
}
