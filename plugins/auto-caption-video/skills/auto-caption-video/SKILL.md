---
name: auto-caption-video
description: Automatically transcribe speech from video, create timed subtitles, improve caption and overlay layout, and render a polished captioned video. Use when Codex receives an MP4, MOV, WebM, or other video and the user asks to add or burn in subtitles, generate SRT captions, redesign the video canvas, reframe it for landscape or vertical social formats, improve visual hierarchy or readability, or deliver a finished captioned video rather than advice alone.
---

# Auto Caption Video

Turn one source video into accurate subtitle files and a visually improved rendered video. Use HyperFrames for transcription, composition, visual inspection, and rendering; use FFmpeg/FFprobe for media inspection and final verification.

## Define completion

Treat the task as complete only when all requested deliverables exist and pass checks:

- Preserve the full spoken content and source audio unless the user requests edits.
- Produce a reviewed word- or phrase-timed transcript and an `.srt` file.
- Burn readable, synchronized captions into the final video.
- Improve composition without hiding faces, demonstrations, product UI, or other essential content.
- Pass HyperFrames lint, validation, and layout inspection.
- Render a final MP4 and run `scripts/verify_deliverables.py` successfully.

Do not stop at a transcript, mockup, design recommendation, or preview render when the user asked for a finished video.

## Gather only decisions that matter

Inspect the video before asking questions. Derive duration, dimensions, frame rate, audio presence, language clues, existing visual identity, subject position, and embedded text.

Ask only when an unresolved choice materially changes the result:

- Ask for the target aspect ratio if the intended platform is unclear; otherwise preserve the source dimensions.
- Reuse a visible brand or existing `DESIGN.md`/`visual-style.md`. If no identity exists and the user has not authorized automatic art direction, ask for mood, light/dark canvas, and brand colors/fonts/references before composing.
- Ask whether speech should be translated only if the user requests another language. Default to same-language transcription.

State assumptions before rendering when the user delegates these choices.

## Execute the workflow

### 1. Inspect and preserve the source

Run `ffprobe` and sample frames across the full timeline. Identify faces, hands, demos, UI, lower thirds, logos, cuts, and areas that can safely hold captions. Preserve the original file and work in a new project directory.

Run `npx hyperframes doctor` before production work. If the installed `$hyperframes` and `$hyperframes-cli` skills are available, read and follow them for current composition and CLI rules.

Initialize a project without relying on implicit transcription:

```bash
npx hyperframes init <project-name> --non-interactive
```

Copy the source into the project with a simple stable filename such as `source.mp4`.

### 2. Transcribe deliberately

Read [references/subtitle-quality.md](references/subtitle-quality.md) before transcription.

- Known non-English language: use `--model small --language <code>`.
- Explicitly English: use `--model small.en --language en`.
- Unknown language: use `--model small` with no language flag.
- Noisy speech, mixed languages, or speech over music: start with `medium` without `.en` unless English is explicit.

```bash
npx hyperframes transcribe source.mp4 --model small
```

Read the complete transcript. Correct names, terms, punctuation, hallucinations, and language errors while preserving timestamps. Retry with a larger model if the quality gate fails. Never compose captions from an unchecked transcript.

Generate the standalone subtitle file from normalized JSON:

```bash
python3 <skill-dir>/scripts/transcript_to_srt.py transcript.json subtitles.srt
```

Keep word-level timing for animated captions even when delivering phrase-level SRT.

### 3. Establish visual direction

Create or update `DESIGN.md` before writing composition HTML. Record palette roles, typography, caption treatment, motion character, safe zones, and explicit anti-patterns. Preserve a coherent source identity when one exists; otherwise derive direction from the transcript and user answers.

Read [references/layout-quality.md](references/layout-quality.md). Build the most information-dense hero frame as static HTML/CSS first, then add animation. Improve hierarchy and balance while keeping the source content primary.

### 4. Compose synchronized captions

Use the source video as muted visual media and a separate audio element using the same source. Match the composition duration to the source duration.

Group captions by meaning, pauses, and reading pace. Use the transcript timestamps as ground truth. Show one caption group at a time, add a deterministic hard hide at every group end, and leave width headroom for emphasized words. Use dynamic font fitting rather than clipping.

Move or restyle captions scene by scene when a fixed lower-third position covers a face, UI, hands, or embedded text. Do not decorate every word; emphasize only meaningful names, numbers, claims, and calls to action.

### 5. Inspect before final render

Run all checks and fix every relevant error:

```bash
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --samples 15
npx hyperframes render --quality draft --output draft.mp4
```

Inspect sampled frames from the draft at the beginning, end, cuts, dense captions, and subject-position changes. Verify synchronization by watching representative sections with audio, not by reading timestamps alone.

Render only after the draft passes:

```bash
npx hyperframes render --quality high --output final.mp4
```

### 6. Verify and deliver

Run:

```bash
python3 <skill-dir>/scripts/verify_deliverables.py \
  --source source.mp4 \
  --output final.mp4 \
  --transcript transcript.json
```

Add `--width` and `--height` when a target canvas was requested. Fix failures instead of waiving them silently.

Deliver the final MP4, SRT file, and a concise note listing the chosen aspect ratio, subtitle language, and any uncertain transcript terms. Keep project source files only when the user asks for editable files.

## Guardrails

- Never overwrite or destructively edit the source video.
- Never use an `.en` model unless the audio is explicitly English.
- Never translate speech unless requested.
- Never continue from a transcript with more than 20% music/replacement tokens or obvious nonsense.
- Never crop, blur, or cover essential source content merely to make room for captions.
- Never claim the layout is optimized without inspecting frames across the timeline.
- Never claim completion without a rendered output and deterministic verification.

