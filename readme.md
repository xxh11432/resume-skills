<div align="center">

# resume-skills

**把你的 Agent 变成简历导师，交付一份能打的 PDF。**

不是"生成一份简历"，而是有人陪你把经历挖出来、组织好、排到恰好一页。它也能直接读你的项目目录、文档和 GitHub 仓库，按**后端 / 全栈 / Agent** 三个岗位出三版。

[![Stars](https://img.shields.io/github/stars/xxh11432/resume-skills?style=flat-square&color=e05d44)](https://github.com/xxh11432/resume-skills/stargazers)
[![Skill](https://img.shields.io/badge/type-Agent%20Skill-8957e5?style=flat-square)](skills/resume-master/SKILL.md)
[![HTML](https://img.shields.io/badge/output-HTML%20%E2%86%92%20PDF-2ea44f?style=flat-square)](#为什么是-html)

</div>

---

## 包含的 Skill

| Skill | 干什么 | 什么时候用 |
|---|---|---|
| [resume-master](skills/resume-master/SKILL.md) | 访谈 + 材料直读，提炼项目亮点，写 HTML 简历，导出恰好一页的 PDF；支持后端 / 全栈 / Agent 三岗位版本 | 写简历、改简历、按 JD 定制、读项目仓库出多版 |
| [backend-grilling](skills/backend-grilling/SKILL.md) | 模拟大厂后端技术面，一次一题连环追问，最后给评分卡 | 面试前拷打、查漏补缺、复盘 |

---

## 你大概遇到过这些

| 你说 | 常见的 AI 简历工具 | 这个 Skill |
|---|---|---|
| 「帮我改简历」 | 要你先把经历整理成文档 | 追着你问，每个问题都带选项 |
| 「这行太挤了」 | 重新生成一份完全不同的 | 改一个数值，3 秒重出 PDF |
| 「保持我原来的样子」 | 把你塞进它的模板里 | 拆图看懂你的排版，再动手 |
| 「我要一页」 | 说"好的"，然后给你两页 | 每改一次就数一次页数 |
| 「我只有一个项目仓库」 | 让你自己总结项目亮点 | 读代码与 README，按岗位挖出不同亮点 |

---

## 两套模板

选完只是起点，之后每个细节都还能聊。

<div align="center">

| 极简纯白 | 极客风尚 |
|:---:|:---:|
| <img src="skills/resume-master/assets/template_refs/images/极简纯白.png" width="230"> | <img src="skills/resume-master/assets/template_refs/images/极客风尚.png" width="230"> |

</div>

每套模板都提供两个版本：**HTML 给 AI 读**（学风格），**图片和 PDF 给你看**（做选择）。

---

## 一个项目，三种讲法

同一份经历，不是换几个关键词就能投三个岗位。

| 维度 | 后端开发 | 全栈开发 | Agent 开发 |
|---|---|---|---|
| 第一眼证明 | 正确性、稳定性、性能 | 能独立端到端交付 | 能把 LLM 做成可上线、可评估的产品 |
| 项目重心 | 一致性、并发、缓存、故障处理 | 需求 → 界面 → 接口 → 数据 → 上线 | 检索 / 工具调用、评估、成本、失败兜底 |
| 技能前置 | 语言框架 → 中间件 → 可观测性 | 前端 → 后端 → 数据库 / 部署 | Python / LLM → 检索 → 评估 / 观测 |

它会先建一份**证据台账**：每条事实都标清来源、置信度和是否需要你确认。仓库只能证明代码怎么写，不能证明哪部分是你写的——所以它会先问你负责哪块，再动笔。

```
这是我的项目目录（或 GitHub 链接），
帮我提炼项目亮点，分别生成后端开发、全栈开发、Agent 开发三版简历。
```

---

## 三十秒装好

把这个链接甩给你的 Agent：

```
https://github.com/xxh11432/resume-skills
帮我安装这个简历 skill，并安装所需的 python 依赖
```

完事。然后跟它说「帮我写份简历」「读一下我这份旧简历」，或者直接把项目目录 / GitHub 链接丢给它。

<details>
<summary>手动安装 / 环境要求</summary>

把 `skills/resume-master` 整个目录复制到全局 skills 目录：

| Agent | 目录 |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/antigravity/skills/` |

环境要求：

```bash
pip install pymupdf pypdf   # PDF 拆图与页数统计
```

PDF 拆图也可使用 Poppler 的 `pdftoppm` 或 ImageMagick 替代。导出 PDF 需要本机装有 **Google Chrome**（脚本会自动找）；找不到时会提示你手动用浏览器打印，不会卡住流程。`project_snapshot.py` 只用 Python 标准库，无需额外依赖。

</details>

---

## 它凭什么不一样

### 📄 它**看得见**你的简历，不只是读得懂

大部分工具读你的旧 PDF，是提取文本。

但简历是**排版作品**。提文本丢掉的恰恰是最要命的东西——字号、间距、模块顺序，以及有没有整段内容被页面底部悄悄吃掉。源文件里明明写了四条，印出来只剩一条，提文本永远发现不了，拆成图片看一眼就知道。

所以 Skill 里写死了一条规矩：

> **读 PDF 必须先拆成图片，一页一页地看。不许偷懒提文本。**

这也意味着，改旧简历时它能**延续你原有的视觉风格**，而不是把你搬进一个新模板。

### 🔢 「恰好一页」不是一句口号

`pdf_page_count.py` 存在的意义就是让这条规范可执行：

- 超出一页 → 压间距、减字号、裁内容
- 留白太多 → 加字号、补细节、丰富经历

每改一次查一次。没有这个脚本，「简历最好一页」就只是句正确的废话。

### 💬 它会反过来问你

不是「你给材料 → 它套模板」。

- **每个问题都附选项**，让你做识别题，不做问答题
- **不等问完才动手**——凑够姓名和一段经历就先把 HTML 拍给你看，因为人看着实物想起来的东西，比干坐着回答问题多得多
- **不让你自己整理经历**，那是它的活
- 只有结果没有动作，它会问你具体做了什么；没有数字，它会追着你要数字

### 🎨 你负责说，它负责实现

「这行太挤」「这块往上挪」「字再小半号」「把这段改成两列」——

说人话，重新编译，三秒出 PDF。

---

## 为什么是 HTML

这是这个项目最核心的一个判断。

- **Markdown** 排不出该有的效果，比如分栏
- **LaTeX / Typst** 先天为排版而生，但 AI 写它们至今容易犯语法错误
- **HTML** 是 AI 最熟悉的标记语言，而且只需要一个浏览器就能打印成 PDF

让 AI 生成 Word，它是在**猜排版**；让 AI 写 HTML，它是在**设计**。

在 HTML 里，AI 既稳定又有审美。

---

## 四种用法

| 场景 | 它会做什么 |
|---|---|
| **从零开始** | 先问你想要哪套模板 → 访谈式挖经历 → 边聊边出 HTML → 确认后编译 PDF |
| **改旧简历** | 拆图读懂旧简历（内容 + 排版）→ 分析 JD → 决定就地编辑还是重写 → 编译 |
| **项目材料直读** | 读目录 / 文档 / GitHub 仓库 → 建证据台账 → 提炼亮点 → 出后端 / 全栈 / Agent 三版 → 编译 |
| **只做导出** | `python scripts/render_pdf.py --in <path> --out <name>.pdf --paper A4` |

---

## 里面装了什么

```
skills/resume-master/
├── SKILL.md                    # 简历写作规范 + 事实边界 + 四条工作流
├── references/
│   ├── material-intake.md      # 文件 / 项目目录 / GitHub 仓库怎么读，证据台账怎么建
│   ├── project-highlights.md   # 项目亮点提炼 + 同一项目跨岗位映射
│   └── roles/
│       ├── backend.md          # 后端开发岗的信号、顺序、句式、误区
│       ├── fullstack.md        # 全栈开发岗
│       └── agent.md            # Agent 开发岗
├── assets/template_refs/
│   ├── html/                   # 两套模板，给 AI 读
│   ├── images/                 # 两套模板，给你挑
│   └── pdf/                    # 两套模板，看实际打印效果
└── scripts/
    ├── project_snapshot.py     # 项目目录 → 关键文件、技术栈、代码规模、git 信息
    ├── render_pdf.py           # HTML → PDF，不带页眉页脚时间戳
    ├── pdf_to_images.py        # PDF → 图片，让 AI 看见排版
    └── pdf_page_count.py       # 数页数，死守一页
```

一套方法论，两套模板，四个脚本。

---

## 后续计划

- [x] 分行业、分岗位的指导文件（后端 / 全栈 / Agent）
- [ ] 更多模板
- [ ] 更狠的经历深挖：让它主动发现「这段经历你写漏了什么」

---

## 一起把它做得更好

特别欢迎这三类分享：

- 你**真实在用**的简历模板
- 你写简历总结出的经验
- 你对「什么是好简历」的认知

提 Issue、发 PR，一起把它做得更好。

---

<div align="center">

**如果它帮到了你，给个 ⭐️ 是对开源最大的鼓励。**

</div>
