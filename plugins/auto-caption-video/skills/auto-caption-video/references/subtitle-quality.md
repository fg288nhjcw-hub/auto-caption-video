# Subtitle quality

Use this reference for transcription, correction, segmentation, synchronization, and subtitle export.

## Language and model selection

- Use the source language by default; translate only on request.
- Use an `.en` model only when the user explicitly identifies English audio.
- For an unknown language, use a multilingual model without `--language` and let Whisper detect it.
- Use `small` for clear speech, `medium` for noisy audio or speech over music, and `large-v3` only when the quality gain justifies its cost.
- Prefer word-level timestamps. Phrase-only SRT/VTT remains usable but cannot support reliable word animation.

## Mandatory transcript review

Read the entire transcript before layout work. Check:

- proper names, brands, numbers, technical terms, and homophones;
- wrong-language output or accidental translation;
- repeated filler, invented words, and missing speech;
- `♪`, `�`, or other non-speech entries;
- timestamps shorter than 0.05 seconds, reversed ranges, large unexplained gaps, or heavy overlap;
- punctuation and sentence boundaries without rewriting the speaker's meaning.

Treat transcription as failed when more than 20% of entries are music/replacement tokens or the text contains obvious nonsense. Retry with a larger appropriate model. If the retry fails, request a transcript/SRT or clearly identify the uncertain passages; do not invent words.

## Caption grouping

Use semantic phrases rather than fixed word counts:

- Energetic speech: 2–3 words per group.
- Conversational speech: 3–5 words per group.
- Calm or explanatory speech: 4–6 words per group.
- Break at sentence punctuation, topic shifts, speaker changes, and pauses of 150 ms or longer.
- Keep a group on screen long enough to read. Shorten text before shrinking it excessively.
- Show only one caption group at a time unless speaker labels make overlap necessary.

For Chinese and other scripts without spaces, optimize by characters and meaning. Avoid breaking a name, number-unit pair, fixed expression, or grammatical dependency across captions.

## Timing and animation

- Start from transcript timestamps; do not eyeball the entire timeline.
- Check synchronization by watching the opening, middle, closing, fast speech, and at least one edit boundary.
- Make entrances quick enough not to delay comprehension.
- Hard-hide each group at its end time so stale captions cannot remain visible.
- Keep word-level emphasis aligned to the spoken word, not merely the enclosing phrase.

## Text treatment

- Prioritize contrast and reading speed over decorative effects.
- Emphasize names, numbers, key claims, warnings, and calls to action selectively.
- Keep capitalization and punctuation appropriate to the source language.
- Fit text to a safe maximum width; never clip glow, outline, or emphasized scale.
- Use an outline, shadow, plate, or localized background treatment when footage contrast varies.

## Deliverables

Always preserve the normalized transcript used for composition. Generate SRT for portability and burn captions into the final video when requested. If the user requests editable styling, additionally provide ASS or the HyperFrames project.

