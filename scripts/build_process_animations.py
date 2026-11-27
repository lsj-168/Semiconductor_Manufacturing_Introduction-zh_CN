"""Build the offline player and click-to-expand chapter figures.

Run from any directory with Python 3: python scripts/build_process_animations.py
"""

import json
from pathlib import Path

from draw_process_steps import svg
from process_steps import MATERIALS, PROCESSES

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "zh-CN" / "2-process-modules"
PLAYER = MODULES / "animations" / "index.html"
FIGURES = ROOT / "images" / "process-steps"
REPO = "https://github.com/lsj-168/Semiconductor_Manufacturing_Introduction-zh_CN"
START = "<!-- process-steps:start -->"
END = "<!-- process-steps:end -->"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def chapter_section(process, figures):
    if process["id"] == "copper":
        color_legend = "灰色是硅，青灰色是绝缘材料，紫色是阻挡层，浅橙色是种子层，铜色是铜，蓝色是覆盖层。"
    elif process["id"] == "cmp":
        color_legend = "灰色是硅，青灰色是绝缘材料，紫色是抛光垫，黄色点是抛光液。"
    elif process["id"] == "implantation":
        color_legend = "灰色是硅，黄色是光刻胶，蓝绿色点是掺杂离子或原子。"
    else:
        color_legend = "灰色是硅，蓝色是待加工薄膜，黄色是光刻胶。深橙色标出受光后的胶。" if "exposed" in process["legend"] else "灰色是硅，蓝色是待加工薄膜，黄色是光刻胶。"
    lines = [
        START, "## 分步图解", "", process["intro"], "",
        "每点击一个步骤，就展开该步的剖面和讲解。图按教学需要放大了薄层。",
        color_legend, "",
        "[下载交互动画](../animations/index.html)（在文件页下载 HTML，双击打开后选择"
        f"「{process['name']}」）。", "",
    ]
    for pos, ((title, what, why, caption), name) in enumerate(zip(process["steps"], figures), 1):
        lines.extend([
            "<details>", f"<summary>第 {pos} 步　{title}</summary>", "",
            f"![{caption}](../../../images/process-steps/{name})", "",
            f"*{caption}*", "",
            "**这一步做什么**", "", what, "",
            "**为什么做**", "", why, "", "</details>", "",
        ])
    title, url = process["ref"]
    return "\n".join(lines + [f"延伸阅读 [{title}]({url})。", END])


def update_chapter(path, block):
    markdown = path.read_text(encoding="utf-8")
    if START in markdown:
        start = markdown.index(START)
        end = markdown.index(END, start) + len(END)
        markdown = markdown[:start] + block + markdown[end:]
    else:
        anchor = "\n## 本章重点"
        if markdown.count(anchor) != 1:
            raise ValueError(f"Expected one chapter summary in {path}")
        markdown = markdown.replace(anchor, f"\n{block}\n\n---\n{anchor}", 1)
    write(path, markdown)


def main():
    prepared = []
    generated = set()
    for process in PROCESSES:
        steps = []
        figures = []
        for index, (title, what, why, caption) in enumerate(process["steps"]):
            drawing = svg(process["id"], index)
            name = f"{process['chapter']}-{index + 1:02d}.svg"
            write(FIGURES / name, drawing + "\n")
            figures.append(name)
            generated.add(name)
            steps.append(dict(title=title, what=what, why=why, caption=caption, drawing=drawing))
        update_chapter(MODULES / process["chapter"] / "README.md", chapter_section(process, figures))
        chapter_url = f"{REPO}/blob/master/zh-CN/2-process-modules/{process['chapter']}/README.md"
        prepared.append({**process, "steps": steps, "chapterUrl": chapter_url})

    # Escaping '<' keeps even a future literal '</script>' in data from closing the JSON element.
    data = json.dumps(dict(processes=prepared, materials=MATERIALS), ensure_ascii=False, indent=2)
    data = data.replace("<", "\\u003c")
    template = Path(__file__).with_name("process_animation_template.html").read_text(encoding="utf-8")
    write(PLAYER, template.replace("@@BOOK_DATA@@", data))

    orphaned = {p.name for p in FIGURES.glob("*.svg")} - generated
    if orphaned:
        print(f"Remove obsolete figures manually: {', '.join(sorted(orphaned))}")
    print(f"Built {len(generated)} figures and the offline player.")


if __name__ == "__main__":
    main()
