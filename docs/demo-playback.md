# Legal Demo Playback

StreamSphere uses a small set of direct HTTPS sample videos to demonstrate the native HTML5 player. The catalog titles are fictional, so there are no title-specific original previews in the seeded catalog. None of these clips are presented as an original movie or trailer. The player labels all seeded media **Play Demo Preview** and states: "This is a legal demo playback sample and is not the original movie or trailer."

| Seeded title | Direct video source | Classification | License / attribution |
| --- | --- | --- | --- |
| Neon Horizon | [MDN flower MP4](https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4) | Preserved demo mapping | MDN Interactive Examples, CC0 sample media. |
| After the Silence | [Sintel trailer](https://media.w3.org/2010/05/sintel/trailer.mp4) | Preserved demo mapping | Blender Foundation, Creative Commons Attribution 3.0; hosted by W3C. |
| Paper Planets | [Big Buck Bunny trailer](https://media.w3.org/2010/05/bunny/trailer.mp4) | Preserved demo mapping | Blender Foundation, Creative Commons Attribution 3.0; hosted by W3C. |

All other seeded movies use one of the same three URLs as a deterministic generic fallback. The pool is intentionally reused instead of creating a large demo-media catalog. The player accepts only direct HTTPS MP4, WebM, or Ogg URLs and never injects arbitrary iframe content. Existing database records are updated only when their seeded URL still points to the legacy `example.com/trailers/` placeholder. Curated or user-supplied URLs are not overwritten.
