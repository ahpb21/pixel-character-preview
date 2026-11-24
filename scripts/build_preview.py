"""Build an offline PNG, Piskel, and Canvas preview from inspected source art."""

import argparse
import base64
import io
import json
import math
import shutil
import sys
import tempfile
from collections import deque
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw


TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "preview"
EFFECTS = {"dust", "dash", "hit", "slash"}
WEAPON_STATES = {"hidden", "sheathed", "drawing", "drawn", "sheathing"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def xy(value, label):
    require(isinstance(value, list) and len(value) == 2
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in value),
            f"{label} must be a finite [x, y] pair")
    return value


def positive_int(value, label):
    require(type(value) is int and value > 0, f"{label} must be a positive integer")
    return value


def remove_background(image, key):
    """Remove matching edge-connected pixels, with opt-in enclosed holes."""
    width, height = image.size
    color = ImageColor.getrgb(key["color"])
    require(len(color) == 3, "Background key must be an RGB color")
    tolerance = key.get("tolerance", 0)
    require(type(tolerance) is int and 0 <= tolerance <= 255,
            "Background tolerance must be an integer from 0 to 255")
    require(type(key.get("holes", False)) is bool, "Background holes must be a boolean")
    encoded = image.tobytes()
    matching = bytearray(
        max(abs(encoded[i + c] - color[c]) for c in range(3)) <= tolerance
        for i in range(0, len(encoded), 4)
    )
    alpha = bytearray(image.getchannel("A").tobytes())
    queue = deque()

    def seed(index):
        if matching[index]:
            matching[index] = 0
            queue.append(index)

    def remove_region():
        while queue:
            index = queue.popleft()
            alpha[index] = 0
            x = index % width
            if x:
                seed(index - 1)
            if x + 1 < width:
                seed(index + 1)
            if index >= width:
                seed(index - width)
            if index < width * (height - 1):
                seed(index + width)

    for x in range(width):
        seed(x)
        seed(width * (height - 1) + x)
    for y in range(height):
        seed(width * y)
        seed(width * y + width - 1)
    remove_region()
    if key.get("holes", False):
        for index in range(len(matching)):
            seed(index)
            remove_region()
    image.putalpha(Image.frombytes("L", image.size, bytes(alpha)))
    return image


def load_art(row, base, cache):
    filename = (base / row["source"]).resolve()
    if filename not in cache:
        with Image.open(filename) as file:
            cache[filename] = file.convert("RGBA")
    source = cache[filename]
    if "crop" in row:
        x, y, w, h = row["crop"]
        require(all(type(v) is int for v in (x, y, w, h)) and
                x >= 0 and y >= 0 and w > 0 and h > 0 and
                x + w <= source.width and y + h <= source.height,
                f"Crop is outside source image: {filename}")
        image = source.crop((x, y, x + w, y + h))
    else:
        image = source.copy()
    if "background" in row:
        image = remove_background(image, row["background"])
    require(image.getchannel("A").getbbox(), f"No visible pixels in {filename}")
    return image


def scaled_size(image, scale, label):
    require(isinstance(scale, (int, float)) and math.isfinite(scale) and scale > 0,
            f"{label} scale must be positive and finite")
    return max(1, round(image.width * scale)), max(1, round(image.height * scale))


def normalize_pose(row, image, size, ground):
    bounds = image.getchannel("A").getbbox()
    subject = image.crop(bounds)
    label = row["id"]
    require(not ("anchor" in row and "offset" in row), f"{label}: choose anchor or offset")
    require(not ("grip" in row and "gripSource" in row), f"{label}: choose grip or gripSource")
    fit = min((size - 2) / subject.width, (ground + 1) / subject.height)
    width, height = scaled_size(subject, row.get("scale", fit), label)
    require(width <= size and height <= size, f"{label}: scaled pose exceeds the frame")
    resized = subject.resize((width, height), Image.Resampling.NEAREST)
    require(resized.getchannel("A").getbbox(), f"{label}: scaling erased the pose")
    sx, sy = width / subject.width, height / subject.height

    def map_source(point):
        x, y = xy(point, label)
        return (x - bounds[0] + .5) * sx - .5, (y - bounds[1] + .5) * sy - .5

    if "anchor" in row:
        ax, ay = map_source(row["anchor"]["from"])
        tx, ty = xy(row["anchor"]["to"], f"{label} anchor.to")
        left, top = round(tx - ax), round(ty - ay)
    else:
        dx, dy = xy(row.get("offset", [0, 0]), f"{label} offset")
        left, top = round((size - width) / 2 + dx), round(ground + 1 - height + dy)
    require(0 <= left and 0 <= top and left + width <= size and top + height <= size,
            f"{label}: adjust the scale or anchor so the pose fits the frame")

    grip = row.get("grip")
    if "gripSource" in row:
        gx, gy = map_source(row["gripSource"])
        grip = [round(left + gx), round(top + gy)]
    if grip is not None:
        x, y = xy(grip, f"{label} grip")
        require(0 <= x < size and 0 <= y < size, f"{label}: grip is outside the frame")
    mount = row.get("mount")
    if mount is not None:
        mx, my = xy(mount["point"], f"{label} mount.point")
        require(0 <= mx < size and 0 <= my < size, f"{label}: mount is outside the frame")
        require(math.isfinite(mount.get("angle", 0)) and
                0 < mount.get("scaleX", 1) <= 1, f"{label}: invalid sheath transform")

    pose = Image.new("RGBA", (size, size))
    pose.paste(resized, (left, top))
    return pose, grip, mount


def prepare_equipment(spec, base, cache, out):
    result = {}
    for key in ("weapon", "sheath"):
        if key not in spec:
            continue
        require(key != "sheath" or "weapon" in result, "A sheath requires a weapon")
        row = spec[key]
        image = load_art(row, base, cache)
        image = image.resize(scaled_size(image, row.get("scale", 1), key), Image.Resampling.NEAREST)
        require(image.getchannel("A").getbbox(), f"{key}: scaling erased the artwork")
        x, y = xy(row["pivot"], f"{key} pivot")
        require(0 <= x < image.width and 0 <= y < image.height,
                f"{key} pivot is outside the scaled image")
        filename = key + ".png"
        image.save(out / filename)
        result[key] = {"file": filename, "pivot": [x, y], "width": image.width, "height": image.height}
        if key == "sheath":
            hilt = positive_int(row["hiltColumns"], "hiltColumns")
            require(hilt <= result["weapon"]["width"], "hiltColumns exceeds weapon width")
            result[key]["hiltColumns"] = hilt
    return result


def compile_clips(spec, poses, equipment):
    result, seen = [], set()
    for clip in spec["clips"]:
        clip_id = clip["id"]
        require(isinstance(clip_id, str) and clip_id and clip_id not in seen,
                f"Missing or duplicate clip id: {clip_id}")
        seen.add(clip_id)
        require(type(clip.get("loop", False)) is bool, f"{clip_id}: loop must be a boolean")
        frames, elapsed = [], 0
        for row in clip["frames"]:
            require(row["id"] in poses, f"{clip_id}: unknown pose {row['id']}")
            pose = poses[row["id"]]
            hold = positive_int(row["holdMs"], f"{clip_id} holdMs")
            state = row.get("weaponState", "hidden")
            require(state in WEAPON_STATES, f"{clip_id}: unknown weapon state {state}")
            require(row.get("layer", "behind") in {"front", "behind"}, f"{clip_id}: invalid weapon layer")
            grip, mount = pose["grip"], pose["mount"]
            if state != "hidden":
                require("weapon" in equipment, f"{clip_id}: {state} needs weapon art")
            if state in {"drawing", "drawn", "sheathing"}:
                require(grip is not None and math.isfinite(row.get("angle", 0)),
                        f"{clip_id}: held weapon needs a grip and valid angle")
            if state in {"sheathed", "drawing", "sheathing"} or (state == "drawn" and "sheath" in equipment):
                require("sheath" in equipment and mount is not None,
                        f"{clip_id}: {state} needs sheath art and a pose mount")
            frame = {**row, "frame": pose["index"], "startMs": elapsed,
                     "weaponState": state, "grip": grip, "mount": mount}
            frames.append(frame)
            elapsed += hold
        require(frames, f"{clip_id}: supply at least one frame")
        effects = clip.get("effects", [])
        for effect in effects:
            require(effect["kind"] in EFFECTS, f"{clip_id}: unknown effect {effect['kind']}")
            at = effect["atMs"]
            require(type(at) is int and 0 <= at < elapsed, f"{clip_id}: effect outside timeline")
            if "point" in effect:
                xy(effect["point"], f"{clip_id} effect.point")
            if "lifeMs" in effect:
                positive_int(effect["lifeMs"], f"{clip_id} effect.lifeMs")
        motion = clip.get("motion", [])
        previous = -1
        for key in motion:
            require(type(key["atMs"]) is int and previous < key["atMs"] <= elapsed,
                    f"{clip_id}: motion keys must increase and fit the timeline")
            xy(key["offset"], f"{clip_id} motion.offset")
            previous = key["atMs"]
        if "originX" in clip:
            require(math.isfinite(clip["originX"]), f"{clip_id}: originX must be finite")
        result.append({**clip, "frames": frames, "durationMs": elapsed, "effects": effects, "motion": motion})
    require(result, "Supply at least one clip")
    return result


def png_url(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def write_body_assets(frames, size, columns, name, fps, out):
    rows = math.ceil(len(frames) / columns)
    atlas = Image.new("RGBA", (columns * size, rows * size))
    chunks = []
    for first in range(0, len(frames), columns):
        group = frames[first:first + columns]
        strip = Image.new("RGBA", (len(group) * size, size))
        for x, frame in enumerate(group):
            strip.paste(frame, (x * size, 0))
        atlas.paste(strip, (0, (first // columns) * size))
        chunks.append({"layout": [[i] for i in range(first, first + len(group))],
                       "base64PNG": png_url(strip)})
    atlas.save(out / "sprites.png")
    layer = {"name": "Character body", "opacity": 1, "frameCount": len(frames), "chunks": chunks}
    piskel = {"modelVersion": 2, "piskel": {"name": name, "description": "Body frames in atlas order",
              "fps": fps, "width": size, "height": size, "hiddenFrames": [],
              "layers": [json.dumps(layer)]}}
    (out / "character.piskel").write_text(json.dumps(piskel, ensure_ascii=False), encoding="utf-8")


def write_contact_sheet(frames, poses, size, out):
    columns = min(8, len(frames))
    magnification = max(1, min(3, 144 // size))
    tile = size * magnification
    sheet = Image.new("RGB", (columns * tile, math.ceil(len(frames) / columns) * (tile + 17)), "#454840")
    labels = ImageDraw.Draw(sheet)
    for pose, frame in zip(poses.values(), frames):
        i = pose["index"]
        x, y = i % columns * tile, i // columns * (tile + 17)
        enlarged = frame.resize((tile, tile), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (x, y), enlarged)
        labels.text((x + 3, y + tile + 1), f"{i:02d}", fill="#f2eee5")
    sheet.save(out / "contact-sheet.png")


def build(spec_path, destination):
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    name = spec["character"]
    require(isinstance(name, str) and name.strip(), "character must be a name")
    language = spec.get("language", "en")
    require(language in {"zh", "en"}, "language must be zh or en")
    size = positive_int(spec.get("frameSize", 48), "frameSize")
    require(size >= 4, "frameSize must allow padding and a baseline")
    ground = spec.get("groundY", round(size * 42 / 48))
    require(type(ground) is int and 0 <= ground < size, "groundY must be inside the frame")
    fps = positive_int(spec.get("piskelFps", 12), "piskelFps")
    require(not destination.exists(), f"Output already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix="pixel-preview-") as temporary:
        out = Path(temporary) / "output"
        shutil.copytree(TEMPLATE, out)
        cache, frames, poses = {}, [], {}
        for row in spec["poses"]:
            identifier = row["id"]
            require(isinstance(identifier, str) and identifier and identifier not in poses,
                    f"Missing or duplicate pose id: {identifier}")
            frame, grip, mount = normalize_pose(row, load_art(row, spec_path.parent, cache), size, ground)
            poses[identifier] = {"index": len(frames), "grip": grip, "mount": mount}
            frames.append(frame)
        require(frames, "Supply at least one pose")
        equipment = prepare_equipment(spec.get("equipment", {}), spec_path.parent, cache, out)
        clips = compile_clips(spec, poses, equipment)
        limit = max(1, 2048 // size)
        columns = min(len(frames), limit, positive_int(spec.get("columns", limit), "columns"))
        write_body_assets(frames, size, columns, name, fps, out)
        write_contact_sheet(frames, poses, size, out)
        data = {"character": name, "language": language, "frameSize": size, "groundY": ground,
                "columns": columns, "frameCount": len(frames), "poses": poses,
                "equipment": equipment, "clips": clips}
        encoded = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
        (out / "actions.json").write_text(encoded + "\n", encoding="utf-8")
        (out / "character-data.js").write_text("window.CharacterData = " + encoded + ";\n",
                                              encoding="utf-8")
        out.rename(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="Reviewed JSON source manifest")
    parser.add_argument("output", type=Path, help="New output directory")
    args = parser.parse_args()
    try:
        build(args.spec.resolve(), args.output.resolve())
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
    print(f"Built offline preview at {args.output / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
