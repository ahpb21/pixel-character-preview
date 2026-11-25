---
name: pixel-character-preview
description: Turn a brief for an original side-view 2D pixel action character into inspected keyframes, transparent sprite sheets, an editable Piskel project, and an offline Canvas preview with optional weapons and pixelfx. Use for the complete character-to-preview workflow.
---

# Pixel Character Preview

Carry a single user brief through visual generation, sprite preparation, playback, and verification. The output is a local character preview and reusable sprite assets. Game input, combat simulation, and gameplay systems require their own request.

## Read before working

- Read [Art direction and prompt rules](references/art-direction.md) before writing any image prompt. Its rules apply to retries and user-facing claims.
- For a requested head-to-body ratio or deliberately exaggerated anatomy, use the [proportion and anchor checks](references/art-direction.md#proportion-and-anchor-checks) before generating motion batches.
- Read [Build contract](references/build-contract.md) before preparing the manifest or modifying the preview template. Paths are relative to the skill folder.
- Use the available image generator for new raster art. Retain user-provided references and generated outputs. When generation capability is unavailable, work from supplied art if available and report which assets are still needed.

## Interpret one brief

Respect supplied character references, art style, resolution, weapons, and action list. When the user asks for the complete action set and leaves routine choices open, use the following baseline. An explicit action list supersedes this baseline.

- Choose a clear side-view silhouette and an original recognizable costume. Right-facing is the default. Use `48 × 48` for coarse pixel art. Use `96 × 96` or the requested size when the brief calls for finer native art. Work in the intended pixel style from the first reference.
- Use a compact movement set of idle 4, run 6, rise/apex/fall 3, landing 2, roll 4, dash 4, and hit recoil 1. Provide a complete jump playback and individual fall and landing views. Reuse the idle pose for recovery where it fits.
- Use one action with three clear keys and a five-hit chain with five distinct attacks. Reuse the first attack's body poses where the two timelines share them. Choose mechanics and effects suited to the character. Visible weapons, scabbards, and sheathing transitions apply when the brief or design supports them.
- Choose editable output names and a new project folder in the requested workspace. Select the preview language from the interaction. Ask only when a missing reference or a major choice actually blocks the work.

## Execute the workflow

1. **Lock the anchor.** Inspect or generate one neutral profile pose. If redesigning the proportions, use existing art for identity and use the checked redesign as the scale reference. Check the final-size anchor and record its measured landmarks before using that exact art in every pose batch.
2. **Generate in batches.** Give each image a single job and each pose a single chronological slot. Generate body poses, weapon art, and sheath art as separate inputs when applicable. Keep original images and exact prompts in the project source directory.
3. **Inspect each image.** Count the actual poses, check identity, orientation, hands, feet, overlap, cut lines, and background. Repair specific defects with targeted retries or pixel cleanup. Label the remaining result according to its actual state.
4. **Prepare the atlas and manifest.** Choose real crop rectangles and a consistent scale for related poses. Align ground-contact poses while preserving intended movement. Map grip points and sheath mouths against the final frames. Use the builder to key suitable backgrounds and normalize PNGs. For ambiguous color keys, use an alpha mask or pixel editor first.
5. **Build playback.** Set explicit frame durations and effect event times. For stored weapons use separate hand and sheath anchors, switch attachment at the contact pose, and verify one visible weapon representation per frame. Use the effect vocabulary supported by the builder. The preview remains functional for unarmed characters.
6. **Run and verify.** Run `python scripts/build_preview.py <manifest.json> <new-output-directory>` from any working directory. Open `index.html` directly in a browser. Check the contact sheet, every requested action, step controls, fitting and equipment transitions, the effect toggle, and offline loading. For running, track both legs through both landings and across the loop seam using the [run-cycle checks](references/art-direction.md#run-cycle-checks). Verify the editable Piskel structure and the image dimensions. Fix failures before delivery. If a verification surface is unavailable, name the check that remains.
7. **Deliver.** Link the offline preview, transparent atlas, Piskel file, action JSON, and any modular equipment art. Summarize frame counts, resolution and choices made for the brief. Keep the original references and prompts accessible for future iteration.

## Accuracy rules

The one-line brief authorizes the workflow and reasonable defaults. The resulting art still requires inspection. Cite actual file dimensions, alpha, pose counts, and preview behavior only after checking them. Describe raw source images as keyframe references until they have been normalized and verified. Keep the editable project's FPS distinct from the millisecond timeline.

A compatible agent needs image generation or supplied source art, local file access, Python with Pillow, and a modern browser for visual verification. The preview bundle ships its local effect runtime and loads without a server.
