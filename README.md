# Pixel Character Preview

Pixel Character Preview 是一套面向 AI Agent 的原创 2D 横版像素角色制作 Skill。给出一句角色描述，Agent 可以依次生成基准图和动作关键帧，处理透明背景、统一帧尺寸、挂接武器，再做成可直接在浏览器打开的 Canvas 预览。

完整动作集包括待机、跑步、起跳与滞空、下落、落地、翻滚、冲刺、受击、单次攻击和五连击。有武器的角色可加入逐帧握点、刀鞘和拔刀归鞘。用户可以指定动作、造型、像素尺寸和武器设计。

## 安装

1. 克隆仓库，或从 GitHub 下载 ZIP 并解压。
2. 将整个目录放到 Agent 的 Skill 安装位置，目录名使用 `pixel-character-preview`。`SKILL.md`、`references/`、`scripts/` 和 `assets/` 应位于同一层。
3. 让 Agent 载入该 Skill，再发出下面的一句话请求。

```bash
git clone https://github.com/ahpb21/pixel-character-preview.git
```

## 一句话使用

> 使用 $pixel-character-preview，生成一个戴橙色围巾的原创像素短剑角色，做出完整动作和五连击，并输出可以直接打开的离线预览。

如果希望角色在同样的显示尺寸下保留更多细节，可以在请求里指定「使用原生 `96 × 96` 像素帧」。默认的粗颗粒规格为 `48 × 48`。直接放大已有低分辨率图会复制像素，原生高分辨率素材需要从基准图开始按目标密度绘制。

也可以给 Agent 一张已有的角色基准图，并说明允许的动作范围。它会保留角色的可见识别特征，按动作批次生成，测量实际切线和握点，再进行预览验证。

## 运行条件

- 支持读取 `SKILL.md` 和同目录参考文件的 Agent，以及本地文件读写权限。
- 从零创作时需要图像生成能力。有现成原图时可以直接进入整理、构建与验证。
- 运行构建脚本需要 Python 3 和 Pillow。验证预览可使用现代浏览器，构建完成后通过本地 `index.html` 播放。

如需手动运行构建，先按构建契约准备说明帧裁切、挂点与时间轴的 JSON，再从仓库根目录执行。

```bash
python -m pip install -r scripts/requirements.txt
python scripts/build_preview.py path/to/character.json path/to/new-preview
```

预览生成到一个新的目录。保持里面的 HTML、脚本和图片相对位置，直接打开 `index.html` 即可播放。

## 输出与验收

| 文件 | 用途 |
| --- | --- |
| `index.html` | 离线 Canvas 预览，支持动作切换、逐帧、慢放、循环和特效开关 |
| `sprites.png` | 按固定帧网格整理的透明角色精灵图 |
| `character.piskel` | 可编辑的 Piskel 工程 |
| `actions.json` | 帧索引、时长、握点、武器状态和特效事件 |
| `contact-sheet.png` | 便于核对所有姿势和帧号的逐帧总图 |
| `weapon.png`、`sheath.png` | 角色设计使用武器或刀鞘时导出的独立素材 |

提示词需逐帧写清姿态、朝向、数量、排布和参考图用途。原图需经过检查才能确认帧数，再由后处理确定精确像素尺寸、透明度和对齐。交付预览前，检查动作、武器遮挡和特效触发是否符合时间轴。[提示词约束](references/art-direction.md) · [构建与验收契约](references/build-contract.md)

预览内置 `pixelfx` 的运行时代码。该部分按所附许可使用。[pixelfx 许可与来源](assets/preview/pixelfx-LICENSE.txt)
