(() => {
  "use strict";

  const $ = id => document.getElementById(id);
  const canvas = $("stage"), ctx = canvas.getContext("2d", { alpha: false });
  const menu = $("clips"), play = $("play"), next = $("next"), prev = $("prev");
  const loop = $("loop"), speed = $("speed"), showFx = $("effects"), showGrip = $("grips");
  const data = window.CharacterData;
  const texts = {
    en: { title: "Character preview", play: "Play", pause: "Pause", replay: "Replay",
      loop: "Loop", effects: "Show effects", grips: "Show anchors", speed: "Speed",
      prev: "Previous frame", next: "Next frame", clips: "Actions", piskel: "Piskel project",
      atlas: "Sprite sheet", data: "Action data", contact: "Frame contact sheet" },
    zh: { title: "角色动作预览", play: "播放", pause: "暂停", replay: "重播",
      loop: "循环", effects: "显示特效", grips: "显示挂点", speed: "播放速度",
      prev: "上一帧", next: "下一帧", clips: "动作", piskel: "Piskel 工程",
      atlas: "透明精灵图", data: "动作索引", contact: "逐帧总图" },
  };
  const language = data?.language === "zh" ? "zh" : "en";
  const text = texts[language];
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  $("title").textContent = data ? data.character + " · " + text.title : text.title;
  document.title = $("title").textContent;
  for (const element of document.querySelectorAll("[data-label]")) element.textContent = text[element.dataset.label];
  for (const [element, key] of [[speed, "speed"], [prev, "prev"], [next, "next"], [menu, "clips"], [canvas, "title"]]) {
    element.setAttribute("aria-label", text[key]);
  }
  play.textContent = text.play;

  const rad = degrees => degrees * Math.PI / 180;
  const clamp = t => Math.max(0, Math.min(1, t));
  function image(src) {
    return new Promise((resolve, reject) => {
      const bitmap = new Image();
      bitmap.onload = () => resolve(bitmap);
      bitmap.onerror = () => reject(new Error("Cannot load " + src));
      bitmap.src = src;
    });
  }

  async function start() {
    const size = data.frameSize, density = size / 48;
    canvas.width = Math.ceil(176 * density);
    canvas.height = Math.ceil(112 * density);
    const ground = Math.round(89 * density);
    const { weapon, sheath } = data.equipment;
    const [atlas, blade, caseArt] = await Promise.all([
      image("sprites.png"), weapon ? image(weapon.file) : null, sheath ? image(sheath.file) : null,
    ]);
    const { createFrame, clearFrame, createFx, composite, Particles, P, Rng, hex, hitSpark, slash } = window.PixelCharacterFx;
    const pixelLayer = document.createElement("canvas");
    pixelLayer.width = Math.ceil(canvas.width / density);
    pixelLayer.height = Math.ceil(canvas.height / density);
    const pixelCtx = pixelLayer.getContext("2d");
    const buffer = createFrame(pixelLayer.width, pixelLayer.height);
    const rgba = pixelCtx.createImageData(pixelLayer.width, pixelLayer.height);

    const dust = {
      meta: { duration: .26 },
      create(options) {
        const random = new Rng(options.seed);
        const particles = new Particles({ rng: random, ground: () => 0 });
        const colors = ["#686052", "#87795f", "#aa9a79"].map(hex);
        for (let i = 0; i < 8; i++) {
          const direction = options.spread && i % 2 ? 1 : -1;
          particles.spawn(P.DUST, random.range(-4, 4), random.range(-3, -1),
            direction * random.range(16, 57), random.range(-19, -4),
            random.range(.15, .26), colors[i % colors.length], random.range(1, 3));
        }
        return { update: dt => particles.update(dt), draw: painter => particles.draw(painter) };
      },
    };
    const dash = {
      meta: { duration: .22 },
      create(options) {
        const random = new Rng(options.seed);
        const color = hex(options.color ?? "#70b5bc");
        const lines = Array.from({ length: 6 }, () =>
          [random.range(-12, 9), random.range(-7, 4), random.range(9, 24)]);
        let age = 0;
        return {
          update(dt) { age += dt; },
          draw(painter) {
            const alpha = clamp(1 - age / .22);
            for (const [y, start, length] of lines) {
              const x = start - age * 58;
              painter.line(x - length * alpha, y, x, y, color, alpha);
            }
          },
        };
      },
    };
    const effects = { dust, dash, hit: hitSpark, slash };
    const live = new Map();
    let clip = data.clips[0], time = 0, selected = -1, request = 0, previous = null, playing = false;

    function position(ms, frame) {
      const keys = clip.motion;
      const start = keys.findLast(key => key.atMs <= ms) ?? keys[0];
      const end = keys.find(key => key.atMs > ms) ?? start;
      const phase = end && end !== start ? clamp((ms - start.atMs) / (end.atMs - start.atMs)) : 0;
      const a = start?.offset ?? [0, 0], b = end?.offset ?? a;
      return {
        x: Math.round((clip.originX ?? (canvas.width - size) / 2) + a[0] + (b[0] - a[0]) * phase + (frame?.dx ?? 0)),
        y: Math.round(ground - data.groundY - 1 + a[1] + (b[1] - a[1]) * phase + (frame?.dy ?? 0)),
      };
    }

    function renderFx(back) {
      if (!showFx.checked) return;
      for (const [i, event] of clip.effects.entries()) {
        const module = effects[event.kind];
        const behind = event.back ?? ["dust", "dash"].includes(event.kind);
        if (behind !== back) continue;
        const elapsed = time - event.atMs;
        const life = event.lifeMs ?? module.meta.duration * 1000;
        if (elapsed < 0 || elapsed >= life) continue;
        const age = elapsed / 1000;
        let effect = live.get(i);
        if (!effect || age < effect.t) {
          const anchor = position(event.atMs, clip.frames.findLast(f => f.startMs <= event.atMs));
          const [x, y] = event.point ?? [size / 2, data.groundY + 1];
          effect = createFx(module, {
            ...event.options,
            x: Math.round((anchor.x + x) / density),
            y: Math.round((anchor.y + y) / density),
            angle: rad(event.angle ?? 0),
            flip: event.flip ?? false,
            seed: event.seed ?? i + 2,
          });
          live.set(i, effect);
        }
        if (age > effect.t) effect.update(age - effect.t);
        clearFrame(buffer);
        effect.draw(buffer);
        composite(buffer, rgba.data);
        pixelCtx.putImageData(rgba, 0, 0);
        ctx.drawImage(pixelLayer, 0, 0, pixelLayer.width * density, pixelLayer.height * density);
      }
    }

    function drawEquipment(point, frame, front) {
      const { mount, grip, weaponState: state } = frame;
      if (!blade || state === "hidden") return;
      const stored = state === "sheathed";
      if (mount && caseArt) {
        ctx.save();
        ctx.translate(point.x + mount.point[0] + .5, point.y + mount.point[1] + .5);
        ctx.rotate(rad(mount.angle ?? 0));
        ctx.scale(mount.scaleX ?? 1, 1);
        if (!front) ctx.drawImage(caseArt, -sheath.pivot[0] - .5, -sheath.pivot[1] - .5);
        if (stored && front !== Boolean(mount.hiltBehind)) {
          const width = sheath.hiltColumns;
          ctx.drawImage(blade, 0, 0, width, blade.height, -width - .5, -weapon.pivot[1] - .5, width, blade.height);
        }
        ctx.restore();
      }
      if (stored || !grip || front !== (frame.layer === "front")) return;
      const angle = rad(frame.angle ?? 0);
      const x = -weapon.pivot[0] - .5, y = -weapon.pivot[1] - .5;
      ctx.save();
      ctx.translate(point.x + grip[0] + .5, point.y + grip[1] + .5);
      ctx.rotate(angle);
      if (state === "drawing" || state === "sheathing") {
        const distance = (mount.point[0] - grip[0]) * Math.cos(angle) + (mount.point[1] - grip[1]) * Math.sin(angle);
        ctx.beginPath();
        ctx.rect(x, y, Math.max(0, Math.min(blade.width, distance - x)), blade.height);
        ctx.clip();
      }
      ctx.drawImage(blade, x, y);
      ctx.restore();
    }

    function marker(point, anchor, color) {
      if (!anchor) return;
      const x = Math.round(point.x + anchor[0]), y = Math.round(point.y + anchor[1]);
      ctx.fillStyle = color;
      ctx.fillRect(x - 2, y, 5, 1);
      ctx.fillRect(x, y - 2, 1, 5);
    }

    function draw() {
      const index = clip.frames.findLastIndex(frame => frame.startMs <= time);
      const frame = clip.frames[index], point = position(time, frame);
      ctx.imageSmoothingEnabled = false;
      ctx.fillStyle = "#282a24";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#20221e";
      ctx.fillRect(0, ground, canvas.width, canvas.height - ground);
      ctx.fillStyle = "#44463b";
      ctx.fillRect(0, ground, canvas.width, Math.max(1, Math.round(density)));

      renderFx(true);
      drawEquipment(point, frame, false);
      const col = frame.frame % data.columns, row = Math.floor(frame.frame / data.columns);
      ctx.drawImage(atlas, col * size, row * size, size, size, point.x, point.y, size, size);
      drawEquipment(point, frame, true);
      renderFx(false);
      if (showGrip.checked) {
        marker(point, frame.grip, "#ffe2a0");
        marker(point, frame.mount?.point, "#83d8df");
      }
      if (selected === index) return;
      selected = index;
      $("phase").textContent = frame.label ?? frame.id;
      $("count").textContent = (index + 1) + " / " + clip.frames.length;
      $("status").textContent = frame.grip ? frame.grip.join(", ") + " · " + (frame.angle ?? 0) + "°" : "";
      prev.disabled = index === 0;
      next.disabled = index === clip.frames.length - 1;
    }

    function setPlaying(state) {
      cancelAnimationFrame(request);
      playing = state;
      play.textContent = state ? text.pause : time >= clip.durationMs ? text.replay : text.play;
      if (state) {
        previous = null;
        request = requestAnimationFrame(tick);
      }
    }

    function tick(now) {
      time += Math.max(0, now - (previous ?? now)) * Number(speed.value);
      previous = now;
      if (time >= clip.durationMs) {
        if (loop.checked) {
          time %= clip.durationMs;
          live.clear();
        } else {
          time = clip.durationMs;
          setPlaying(false);
          draw();
          return;
        }
      }
      draw();
      request = requestAnimationFrame(tick);
    }

    function choose(item, autoplay) {
      clip = item;
      time = 0;
      selected = -1;
      live.clear();
      loop.checked = Boolean(item.loop);
      for (const button of menu.children) button.setAttribute("aria-pressed", String(button.dataset.clip === item.id));
      draw();
      setPlaying(autoplay);
    }

    function step(delta) {
      const frame = clip.frames[selected + delta];
      time = frame.startMs + Math.min(40, frame.holdMs - 1);
      live.clear();
      setPlaying(false);
      draw();
    }

    for (const item of data.clips) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = item.name;
      button.dataset.clip = item.id;
      button.addEventListener("click", () => choose(item, true));
      menu.appendChild(button);
    }
    play.addEventListener("click", () => {
      if (playing) return setPlaying(false);
      if (time >= clip.durationMs) {
        time = 0;
        live.clear();
      }
      setPlaying(true);
    });
    prev.addEventListener("click", () => step(-1));
    next.addEventListener("click", () => step(1));
    showFx.addEventListener("change", () => { live.clear(); draw(); });
    showGrip.addEventListener("change", draw);
    play.disabled = false;
    choose(clip, false);
  }

  start().catch(error => {
    $("status").textContent = error.message;
    console.error(error);
  });
})();
