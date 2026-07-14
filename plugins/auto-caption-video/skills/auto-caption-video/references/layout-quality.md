# Video layout quality

Use this reference to analyze source footage, choose a target canvas, place captions, and verify the redesigned video.

## Analyze before redesigning

Sample frames across the full timeline, including cuts and subject movement. Map:

- faces, eyes, hands, products, demonstrations, and active UI;
- existing subtitles, lower thirds, logos, watermarks, and embedded text;
- stable negative space and areas that change contrast;
- camera movement, cropping risk, and scene boundaries.

Do not assume one caption position works for every scene.

## Choose the canvas

- Preserve source dimensions when the user gives no destination or target ratio.
- Use 16:9 for landscape presentation/video platforms, 9:16 for vertical short-form video, and 1:1 only when explicitly useful.
- When reframing, keep the essential subject visible throughout. Prefer adaptive crops, picture-in-picture, split layouts, or a restrained background fill over cutting off faces, hands, products, or UI.
- Keep source audio and duration unchanged unless editing is requested.

## Establish hierarchy

Treat source footage as the primary layer. Captions are the second layer; labels and decoratives are supporting layers.

- Build the densest hero frame in its final static layout before animating.
- Use full-canvas flex/grid containers and padding for content structure; reserve absolute positioning for captions and decoratives.
- Use one accent color and a small, declared palette.
- Use one expressive typeface per scene with a quieter supporting face. Avoid near-identical font pairings.
- Make video typography large enough to read at playback size, not merely in an editor.
- Use timing, scale, weight, and position to create hierarchy; do not give every element equal emphasis.

## Place captions safely

- Start near the lower center in landscape and lower-middle in portrait, then adapt to the actual footage.
- Keep captions inside platform-safe margins and away from common UI zones.
- Move captions above or beside faces, hands, demos, product UI, source text, and logos.
- Keep caption placement stable within a shot. Change position at a cut or clear motion boundary rather than jittering every phrase.
- Use a full-width centered container with a safe maximum text width.
- Fit text dynamically and leave scale headroom for emphasized words.

## Improve without overdesigning

Add only elements that improve comprehension or balance: a caption plate, progress marker, speaker label, restrained title, or contextual callout. Avoid generic gradients, decorative card grids, random icons, and motion unrelated to the speech.

Use ambient motion only when it fits the source and does not compete with the speaker or demonstration. Preserve an existing visual identity rather than replacing it with a generic template.

## Inspect over time

Run HyperFrames lint, validation, and inspect with at least 15 samples. Review frames at:

- the first and last caption;
- the longest and shortest caption groups;
- every major cut or layout change;
- the brightest and darkest footage;
- moments where the subject moves into a caption zone;
- any crop or aspect-ratio transition.

Fix overflow, low contrast, collisions, awkward wrapping, stale captions, and unexpected empty areas. Mark intentional overflow only after visually confirming it is harmless.

Watch representative sections with audio after static inspection. A layout can pass bounding-box checks and still feel late, frantic, or visually distracting.

