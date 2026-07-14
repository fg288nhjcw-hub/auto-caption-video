# Auto Caption Video

A Codex skill and marketplace plugin for turning raw videos into polished, captioned social-video exports.

It can:

- transcribe speech and generate timed subtitles;
- remove silent opening and ending segments;
- improve subtitle, title, and overlay readability;
- reframe video for vertical or landscape social formats;
- render a finished captioned MP4 and verify the deliverables.

## Install from this marketplace

Clone this repository, then add its marketplace and install the plugin:

```bash
codex plugin marketplace add /absolute/path/to/auto-caption-video
codex plugin add auto-caption-video@auto-caption-video-marketplace
```

Restart Codex after installation. Then invoke the skill with `$auto-caption-video` and provide a video file.

Example:

```text
Use $auto-caption-video to add bilingual subtitles, remove silence before and after the conversation, optimize the vertical layout, and export the final MP4.
```

## Requirements

The workflow expects local video-processing and transcription tools such as FFmpeg, FFprobe, and an available speech-to-text backend. The skill checks the environment before rendering and reports missing dependencies.

## Repository structure

- `.agents/plugins/marketplace.json` — Codex marketplace catalog
- `plugins/auto-caption-video/.codex-plugin/plugin.json` — plugin manifest
- `plugins/auto-caption-video/skills/auto-caption-video/` — skill instructions, references, and helper scripts
