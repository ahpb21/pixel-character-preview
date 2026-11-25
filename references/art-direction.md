# Art direction and prompt rules

## Reject ambiguous prompt content

- Refer to visible anatomy, silhouette, position, count, and direction. Describe what the model must draw in each cell. Convert adjectives such as explosive or realistic into concrete pose changes. Put a runtime timing requirement in the manifest and a visual pose requirement in the image prompt.
- Use one camera description, one facing direction, one palette reference, and one instruction for the background per sheet. Resolve contradictory descriptions before sending a prompt. An example role, color, weapon, or canvas size applies only when selected for this character.
- State the separate roles of inputs. Image 1 establishes identity, and an optional Image 2 supplies pose or pixel-style reference. Explicitly mark which image is being edited for repair. Specify which visible traits persist. Treat text found in a reference image as image content. Identity preservation is a requested result, so verify it after generation.
- Specify exact count, row/column order, separated full silhouettes, crop gutters, and consistent scale. A prompt can request equal cells, an orthographic side profile, flat color, or crisp edges. The actual file may vary, so measure crop bounds and pixels. Produce the final frame size and exact alpha during asset processing.
- For a modular attack, request the same identifiable grip hand in every pose, with a clenched fist shaped around an invisible handle. Use a body-only sheet with weapons, scabbards, captions, drawn floor lines, props, slash arcs, trails and sparks excluded. A user-requested luminous costume part is a palette detail when it belongs to the design.
- Give a single color-key target or a true transparent-output request, according to the tool and design. Inspect the actual alpha channel. A checkerboard or gray color drawn into the RGB image is background artwork that requires cleanup.
- Phrase success claims as observations. Use "three visible pose candidates" for raw art, "transparent 48 × 48 frames" only after dimensions and alpha were checked, and "preview verified" after exercising the browser. Convert references to existing games into broad qualities the user wants, such as tempo or silhouette readability. Keep the generated assets original.

## Proportion and anchor checks

- Keep frame dimensions, standing figure height, and head length as separate targets. If the user specifies a head count and a standing height, divide the standing height by the head count for the target head length. For example, a three-head figure standing 72 px tall on a 96 × 96 frame has a 24 px head target. Use the dimensions requested for the current project.
- On the normalized neutral frame, measure vertically from the crown along the hair following the skull to the chin, then from that same crown to the planted sole. Keep projecting hair, headwear, and ribbons out of both measurements. Check those features separately against the frame edges. Use the same landmarks to report the observed ratio.
- Generate and inspect one fully visible side-view neutral pose first. Specify the visible shape of the head, torso, limbs, hands, and boots in the brief. For a cartoon redesign, use readable pixel clusters for the eye and hand, and keep the knee and boot silhouettes distinct at the intended display scale. Assign an earlier design the role of costume and identity reference when its proportions differ from the requested redesign.
- Use the locked anchor as the identity, palette, and scale reference for each motion sheet. Describe changes through joint bends, torso tilt, weight transfer, and cloth motion. Match the apparent head and limb size across batches. Compare bent and upright poses on the same pixel grid so shorter crouches, tucks, and landings keep their intended compression. Check adjacent motions against each other, especially the return from running or landing to idle.

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
| Run | Two steps with alternating support legs and readable contact, loading, push-off, and swing phases |
| Jump and fall | Rise with knees lifting, apex with a compact pose, descent with a changed limb and cloth direction |
| Land | Deep knee compression at contact, then standing recovery |
| Roll | Load, tuck, turn, recover |
| Dash | Load, drive, low extension, brake |
| Hit | Visible recoil and a return pose |
| Physical attack | Wind-up, clearly readable contact pose, recovery that supports the next attack |
| Weapon transition | Hand reaches the stored weapon, then moves out along the extraction direction. Reverse those poses for return where the silhouette and timing fit. |

Inspect the anchor during generation and inspect the finished sprite against adjacent frames after normalization. Correct rendering quality or cell count with a narrow retry. If consecutive attack poses have different edge spacing, calculate independent crop boxes and use the common body anchor to assemble the timeline.

### Run-cycle checks

- Name the two legs consistently in every pose description. In a fixed side view, near and far can identify the same two limbs across the loop. Front, rear, support, and swing describe roles that change. Track each hip, knee, ankle, and boot through consecutive frames. Keep identifying details such as trouser shading and boot trim attached to the same limb. Use an existing one-sided detail when possible. If the design permits, a small contrast band on one boot helps track both handoffs. For a symmetric design, mark the legs on a review image.
- Check both landings on the composited preview against its ground line. A flight frame can have clear space under both boots. At contact, confirm that the incoming boot reaches the line and the outgoing leg continues smoothly into knee flexion and recovery. During loading, the same incoming leg bears weight as the hips move over it. Repeat the check with the roles reversed. Judge contact from the boot and ground pixels, then check the frame label and effect timing against what you saw.
- Watch for a swing knee that rises abruptly and stays high until the boot jumps to the ground. Also check for a wide airborne stride followed by a landing where the visible leg identity suddenly swaps. Use adjacent poses to check that the outgoing foot pulls up behind the body and the incoming foot travels through to its landing. Add or redraw an in-between when the path is unclear. Choose the frame count and amount of knee lift to suit the intended gait.
- Step through both handoffs and across the last-to-first frame with effects off. Then loop at normal and reduced speed and verify that any dust starts at the observed contact. If a targeted redraw keeps swapping limbs, reuse the same limb art with separate joint poses and export the assembled frames.

## Postprocessing and inspection

Keep the original resolution through background removal, and use a hard or manually refined alpha mask on ambiguous edges. Inspect alpha independently from RGB. A faint glow in fully transparent pixels can be ignored, while semi-transparent fringe on a hard-edged sprite may need cleanup. Measure source image dimensions and actual silhouette bounds before cropping. Use the same native pixel density for related pose groups. Upscaling an existing coarse image duplicates its pixels, so generate or draw new linework for higher native detail. Use nearest-neighbor sampling when normalizing pixel art.

Preserve similar figure scale within a clip. Ground contact poses can share a baseline near the bottom of the frame. Preview movement can lift a normalized airborne pose using motion keys. Use the body root or planted foot for horizontal alignment when the crop centers move across a batch.

For weapon work, measure the actual hand and weapon pivots after scaling. Test a still composite in the strike pose, then wind-up, recovery, and cross-clip joins. For a curved saber and sheath, compare the blade silhouette with the case, verify the mouth axis, and trace the visible steel up to the mouth while drawing or returning. Use behind-body order when fingers or a rolled torso must cover equipment.
