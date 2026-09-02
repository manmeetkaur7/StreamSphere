"use client";

import { useRef, useState } from "react";

type PreviewSource = {
  attribution: string;
};

const SAMPLE_SOURCES: Record<string, PreviewSource> = {
  "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4": {
    attribution: "Flower video from MDN Interactive Examples (CC0).",
  },
  "https://media.w3.org/2010/05/sintel/trailer.mp4": {
    attribution: "Sintel trailer by Blender Foundation (CC BY 3.0), hosted by W3C.",
  },
  "https://media.w3.org/2010/05/bunny/trailer.mp4": {
    attribution: "Big Buck Bunny trailer by Blender Foundation (CC BY 3.0), hosted by W3C.",
  },
};

function isDirectVideoUrl(url: string) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" && /\.(mp4|webm|ogg)$/i.test(parsed.pathname);
  } catch {
    return false;
  }
}

export default function MoviePreviewPlayer({ title, trailerUrl }: { title: string; trailerUrl: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [ended, setEnded] = useState(false);
  const source = SAMPLE_SOURCES[trailerUrl];
  const isDemoPreview = source !== undefined;
  const canPlay = isDirectVideoUrl(trailerUrl);

  async function playPreview() {
    setEnded(false);
    try {
      await videoRef.current?.play();
    } catch {
      setFailed(true);
    }
  }

  if (!canPlay) {
    return (
      <section className="rounded-[2rem] border border-dashed border-white/15 bg-[#0d0d0d] p-6">
        <h2 className="text-lg font-semibold text-white">Preview</h2>
        <p className="mt-3 text-sm leading-6 text-white/60">Preview unavailable for this title.</p>
      </section>
    );
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-4 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#ff8b92]">Legal demo media</p>
          <h2 className="mt-2 text-xl font-semibold text-white">{isDemoPreview ? "Demo Preview" : "Preview"}</h2>
        </div>
        <button
          type="button"
          onClick={() => void playPreview()}
          disabled={loading || failed}
          className="inline-flex h-11 items-center justify-center rounded-xl bg-[#E50914] px-5 text-sm font-semibold text-white transition hover:bg-[#c50b14] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Loading preview..." : isDemoPreview ? "Play Demo Preview" : "Watch Preview"}
        </button>
      </div>

      <div className="relative mt-5 aspect-video overflow-hidden rounded-2xl bg-black">
        <video
          ref={videoRef}
          controls
          playsInline
          preload="metadata"
          onPlay={() => setEnded(false)}
          onEnded={() => setEnded(true)}
          onCanPlay={() => setLoading(false)}
          onError={() => {
            setLoading(false);
            setFailed(true);
          }}
          className="h-full w-full"
        >
          <source src={trailerUrl} />
          Your browser does not support HTML5 video.
        </video>
        {loading ? <p className="absolute inset-0 flex items-center justify-center bg-black/70 text-sm text-white/70">Loading preview...</p> : null}
        {failed ? <p className="absolute inset-0 flex items-center justify-center bg-black/80 px-6 text-center text-sm text-white/70">Preview unavailable for this title.</p> : null}
        {ended ? (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80 px-6 text-center">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#ff8b92]">StreamSphere</p>
              <p className="mt-3 text-xl font-semibold text-white">Created by Manmeet Ghuman</p>
              <button
                type="button"
                onClick={() => void playPreview()}
                className="mt-5 rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Replay demo
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <p className="mt-4 text-xs leading-5 text-white/45">
        {source?.attribution ?? "Direct video source supplied for this catalog entry."} {isDemoPreview ? "This is a legal demo playback sample and is not the original movie or trailer." : `This preview is not a full version of ${title}.`}
      </p>
    </section>
  );
}
