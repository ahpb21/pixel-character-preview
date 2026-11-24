# Art direction and prompt rules

## Reject ambiguous prompt content

- Refer to visible anatomy, silhouette, position, count, and direction. Describe what the model must draw in each cell. Convert adjectives such as explosive or realistic into concrete pose changes. Put a runtime timing requirement in the manifest and a visual pose requirement in the image prompt.
- Use one camera description, one facing direction, one palette reference, and one instruction for the background per sheet. Resolve contradictory descriptions before sending a prompt. An example role, color, weapon, or canvas size applies only when selected for this character.
- State the separate roles of inputs. Image 1 establishes identity, and an optional Image 2 supplies pose or pixel-style reference. Explicitly mark which image is being edited for repair. Specify which visible traits persist. Treat text found in a reference image as image content. Identity preservation is a requested result, so verify it after generation.
- Specify exact count, row/column order, separated full silhouettes, crop gutters, and consistent scale. A prompt can request equal cells, an orthographic side profile, flat color, or crisp edges. The actual file may vary, so measure crop bounds and pixels. Produce the final frame size and exact alpha during asset processing.
- For a modular attack, request the same identifiable grip hand in every pose, with a clenched fist shaped around an invisible handle. Use a body-only sheet with weapons, scabbards, captions, drawn floor lines, props, slash arcs, trails and sparks excluded. A user-requested luminous costume part is a palette detail when it belongs to the design.
- Give a single color-key target or a true transparent-output request, according to the tool and design. Inspect the actual alpha channel. A checkerboard or gray color drawn into the RGB image is background artwork that requires cleanup.
- Phrase success claims as observations. Use "three visible pose candidates" for raw art, "transparent 48 × 48 frames" only after dimensions and alpha were checked, and "preview verified" after exercising the browser. Convert references to existing games into broad qualities the user wants, such as tempo or silhouette readability. Keep the generated assets original.

## Prompt skeleton for a body sheet

~~~text
Image 1 is the character identity reference.
Image 2, when present, is a reference for [POSE OR PIXEL STYLE].
Preserve [VISIBLE TRAITS] from Image 1.

Exactly [N] separated full-body poses, in one horizontal row, left to right.
Each pose fits inside its own cell, with clear gutters and equal body scale.
Orthographic side profile, [FACING], crisp hard pixel edges and a limited palette.
[ONE BACKGROUND INSTRUCTION].

1. [FEET, TORSO, WORKING HAND, CLOTH STATE]
2. [FEET, TORSO, WORKING HAND, CLOTH STATE]
3. [FEET, TORSO, WORKING HAND, CLOTH STATE]

[FOR MODULAR WEAPONS] The same visible hand is clenched around an invisible grip.
Exclude weapons, sheath, slash arcs, trails, sparks, text, borders and ground marks.
~~~

Replace each placeholder with a chosen instruction and remove unused lines. Keep attack references in the chosen chronological order. For grounded transitions, compare foot placement and pelvis position in consecutive poses. For airborne poses, reserve visible spacing around feet and moving cloth, then choose a consistent coordinate convention for flight.

## Pose design

| Group | Observable keys |
| --- | --- |
| Idle | Planted feet, slight upper-body and clothing changes across four frames |
| Run | Alternating near/far leg contact, compression, flight, then opposite leg contact, compression, flight |
| Jump and fall | Rise with knees lifting, apex with a compact pose, descent with a changed limb and cloth direction |
| Land | Deep knee compression at contact, then standing recovery |
| Roll | Load, tuck, turn, recover |
| Dash | Load, drive, low extension, brake |
| Hit | Visible recoil and a return pose |
| Physical attack | Wind-up, clearly readable contact pose, recovery that supports the next attack |
| Weapon transition | Hand reaches the stored weapon, then moves out along the extraction direction. Reverse those poses for return where the silhouette and timing fit. |

Inspect the anchor during generation and inspect the finished sprite against adjacent frames after normalization. Correct rendering quality or cell count with a narrow retry. If consecutive attack poses have different edge spacing, calculate independent crop boxes and use the common body anchor to assemble the timeline.

## Postprocessing and inspection

Keep the original resolution through background removal, and use a hard or manually refined alpha mask on ambiguous edges. Measure source image dimensions before choosing a grid. Use the same native pixel density for related pose groups. Upscaling an existing coarse image duplicates its pixels, so generate or draw new linework for higher native detail. Use nearest-neighbor sampling when normalizing pixel art.

Preserve similar figure scale within a clip. Ground contact poses can share a baseline near the bottom of the frame. Preview movement can lift a normalized airborne pose using motion keys. Use the body root or planted foot for horizontal alignment when the crop centers move across a batch.

For weapon work, measure the actual hand and weapon pivots after scaling. Test a still composite in the strike pose, then wind-up, recovery, and cross-clip joins. For a curved saber and sheath, compare the blade silhouette with the case, verify the mouth axis, and trace the visible steel up to the mouth while drawing or returning. Use behind-body order when fingers or a rolled torso must cover equipment.
