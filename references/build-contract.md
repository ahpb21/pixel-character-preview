# Build contract

The script takes a reviewed JSON manifest and a new output directory. It reads local images, supports PNG alpha or explicit background keys, writes embedded editable Piskel images, and produces a portable browser preview. Use an available Python 3 interpreter with Pillow installed, or install the dependency listed in `scripts/requirements.txt`.

~~~sh
python scripts/build_preview.py character.json path/to/new-preview
~~~

Use absolute paths for the script when it is outside the project directory. Source paths inside the manifest resolve relative to that manifest. Keep the manifest and source artwork beside the output in the project. The builder writes the final directory after successful validation.

## Manifest fields

| Field | Meaning |
| --- | --- |
| `character` | Character name used in the viewer |
| `language` | `zh` or `en` for preview controls, default `en` |
| `frameSize` | Final square frame size. Write `96` for the Skill's default for new characters, or use the requested size. The standalone builder uses `48` when the field is omitted. |
| `groundY` | Zero-based row of the contact pixel, defaults to the scaled 48-frame baseline of 42 |
| `piskelFps` | Editable project preview rate, default 12. Runtime timing comes from each frame's `holdMs`. |
| `columns` | Requested atlas columns. The builder may wrap to keep each strip within roughly 2048 pixels. |
| `poses[]` | Unique poses in atlas order |
| `equipment` | Optional `weapon` and `sheath` files |
| `clips[]` | Playback sequences and event data |

Each pose needs `id` and `source`. Optional `crop: [x,y,w,h]` is the precise rectangle in original-image pixels. `background: {"color":"#808080","tolerance":10}` removes matching pixels connected to the crop edge. Tolerance applies independently to each RGB channel. The optional `holes: true` removes enclosed matching regions too, including any interior areas with matching actor colors. Inspect those frames carefully. Supply pre-masked images when preserving costume pixels requires finer control.

The builder trims the visible bounds, then scales with nearest-neighbor. Specify the same explicit `scale` for related poses whenever their silhouette height changes. Auto-fit is a convenience for independent poses, so verify resulting body scale before using it on a motion cycle. Default placement centers the visible bounds and aligns the lowest visible row to `groundY`. Choose one placement adjustment when needed. `offset: [dx,dy]` shifts the default placement. `anchor: {"from":[sx,sy],"to":[tx,ty]}` maps a point from the cropped source to the final frame. A pose that falls outside its frame returns a descriptive build error.

If source PNGs already have the exact target dimensions and reviewed pixel placements, pass each full frame without `crop`, set `scale: 1`, and use the same frame-local point for `anchor.from` and `anchor.to`. This preserves the position through the builder's trim and paste. Record the placement along with the grip and mount so the source remains reproducible.

Use `grip: [x,y]` for the finished frame or `gripSource: [x,y]` to transform a measured source pickup point using the same trimming, scaling, and placement. The latter uses local coordinates inside the crop. `mount: {"point":[x,y],"angle":151}` is the sheath-mouth location and angle on the finished frame. Both use frame-local coordinates with the origin at top left. Positive angles turn clockwise. Optional mount `scaleX` shortens the long axis for a pose such as a tuck. Optional `hiltBehind: true` places the stored handle behind the body.

Equipment entries accept `source`, optional `crop`, `background` and `scale`, and a required `pivot` measured in the final cropped and scaled weapon or sheath PNG. For sheaths the pivot is the mouth. `hiltColumns` is the width of the weapon image's left portion to display while stored. Art used with this renderer extends to the right along its local blade or sheath axis. Verify its alignment and shape in the preview.

A clip defines `id`, `name`, optional `loop`, and `frames`. Each playback frame references a pose by `id` and gives a positive `holdMs`. Optional `label` is shown in the viewer. Optional `dx` and `dy` are stage-space position adjustments in final frame pixels. `originX` is the stage-space starting body x-coordinate. If omitted, the body is centered. `motion` is an array of increasing `{"atMs":0,"offset":[0,0]}` keys. The renderer linearly interpolates offsets. Keep a jump arc in this motion track when airborne artwork was normalized to a ground-relative origin.

The per-frame `weaponState` values are `hidden`, `sheathed`, `drawing`, `drawn` and `sheathing`. `hidden` is the default. The last three require a grip and support `angle`, with 0 degrees pointing right. With a sheath, visible states require a mount. The hand normally covers the weapon. Optional `layer: "front"` permits a deliberately front-drawn weapon. Drawing and sheathing project the hand-to-mouth vector onto the weapon axis to clip the portion inside the sheath. Test contact visually.

In a partial draw, inspect the exposed blade between the near hand and the sheath mouth. If the default behind-body pass hides that segment, use the front pass for that keyframe when the blade crosses the front of the torso. If the front pass obscures the fingers, a project-specific preview can redraw the relevant hand pixels above the blade. The stock template leaves front-layer equipment on top. Keep the sheath and stored hilt transitions tied to the same mouth axis and check both directions.

## Effect events

Use `effects: [{"kind":"slash","atMs":180,"point":[25,38]}]` in a clip. `atMs` is within the clip timeline, and `point` is relative to the pose origin at effect birth. A missing point defaults to the center of the frame's ground contact line. Set `back` for compositing behind the body when needed. `angle` and `flip` map to the effect transform. Optional `options` is passed to the effect, such as `{"radius":34,"light":0.6}` for a slash. `lifeMs` changes its visible lifetime, and `seed` makes repeatable effects. The renderer draws effects near a 48-frame reference density and scales the buffer with the chosen character density.

| Kind | Playback use |
| --- | --- |
| `dust` | Foot contacts, jump push, landing, roll or brake, with optional `options.spread` |
| `dash` | Short motion streak from a configured birth point, with optional `options.color` |
| `hit` | Imported pixelfx hit spark. Its `options.height` raises its impact above the event point. |
| `slash` | Imported pixelfx sword arc. Its upstream pivot is a placement origin. Inspect the arc and adjust the event position and angle against the blade. |

Motion and effect coordinates use target-frame pixels. For 96-pixel art, measure hand and equipment points at 96, and retune or scale movement and event coordinates accordingly. The effect buffer scaling does not change the game's timing.

For a modular strike, set the effect event at the visible swing timing and use the transformed blade edge or tip on the contact pose as an alignment target. Adjust the effect placement after applying its angle, flip, and buffer scale. Compare stills during the visible sweep and replay the full strike. Place contact dust from the supporting sole on the frame where it meets the ground line.

## Small example contract

These coordinates, filenames, and times illustrate the format. Replace them with observations from the actual art.

~~~json
{
  "character": "Example character",
  "language": "en",
  "frameSize": 96,
  "poses": [
    { "id": "idle", "source": "art/idle.png" },
    { "id": "cut", "source": "art/attack.png", "crop": [512, 0, 512, 512],
      "background": { "color": "#808080", "tolerance": 9 },
      "scale": 0.16, "grip": [76, 28] }
  ],
  "equipment": { "weapon": { "source": "art/blade.png", "pivot": [8, 6] } },
  "clips": [
    { "id": "idle", "name": "Idle", "loop": true, "frames": [{ "id": "idle", "holdMs": 200 }] },
    { "id": "attack", "name": "Attack",
      "frames": [
        { "id": "idle", "holdMs": 120 },
        { "id": "cut", "holdMs": 100, "weaponState": "drawn", "angle": -12 },
        { "id": "idle", "holdMs": 160 }
      ],
      "effects": [{ "kind": "slash", "atMs": 120, "point": [48, 80], "options": { "radius": 32 } }]
    }
  ]
}
~~~

The complete default set expands the same contract to separate idle, run, jump, fall, land, roll, dash, hit, single attack, and five-hit clips. In the full jump clip, sequence the same independent fall and land poses. In the five-hit clip, assign one contact event to each chosen strike pose. The atlas keeps one copy of a pose referenced by multiple clips.

## Verify the deliverables

Open `index.html` directly. Test all buttons, loop and pause, slow playback, frame stepping, and active effects. Use the anchor toggle to inspect hand and sheath points. Test strike directions, leading stationary phases, and transitions into and out of weapon states. Check console errors and that assets load from the output folder. The HTML references `sprites.png`, `character-data.js` and the same-folder runtime. Move or zip the entire output folder for sharing.

Open `character.piskel` in Piskel when available. Confirm frame count, size, order, transparency and foot placement using `contact-sheet.png` and the atlas. The exported JSON retains authored timings, grips, mounts and effects. The Piskel project holds the body pixels and its editing preview FPS.

For a structural check, decode the Piskel PNG chunks using each chunk's layout, then compare frame dimensions, order, and RGBA pixels against the atlas. Record editor import separately if tested. If delivering a ZIP, extract it to a separate folder and open that copy offline to check relative asset paths.

For updates, retain the manifest as the source of placements and timing. When a hand, sheath, or body origin moves in edited art, update its anchor in the manifest, rebuild into a fresh folder, then verify the changed clips.

[Piskel project import and frame grids](https://github.com/piskelapp/piskel/blob/master/docs/specs/import.md) · [pixelfx upstream](https://github.com/patch-gg/pixelfx)
