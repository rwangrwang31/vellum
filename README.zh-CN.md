# GPT-5.5 PDF/DOCX 本地工作台

[English](./README.md)

本仓库是一套独立、非官方、源码可见的混合来源本地工作台，用于本机 PDF/DOCX 文档工作流。它提供实用文档、脚本和辅助 CLI，支持在本机完成渲染、检查、转换、生成、QA 复查和产物注册。

![本地 PDF 工作流黑白简笔图示](./assets/pdf-workflow-illustration.png)

## 项目状态

- **公开发布定位：** 源码可见的混合来源本地工作台，不是“仓库内所有内容都已清权”的传统开源发布。
- **隶属关系：** 本仓库不隶属于 OpenAI、Anthropic 或文档中提到的其他平台提供方，也不由它们背书或分发。
- **许可边界：** MIT 风格许可仅拟适用于本仓库原创的文档、图示、本地工作流说明和胶水材料。

在再分发、镜像或将材料用于本地评估之外的用途前，请先阅读 [`LICENSE`](./LICENSE) 和 [`NOTICE`](./NOTICE)。

## 这是什么

- 围绕本机文件直接访问组织的 PDF/DOCX 本地工作台。
- 包含 PDF 脚本、DOCX 脚本、任务文档、示例、排障说明和辅助 CLI。
- 提供非 OCR 工作流参考：把扫描页或低文本页渲染成图片，再使用 GPT-5.5 风格的多模态页面复查。
- 把 `/home/oai/skills`、`/mnt/data`、截图工具、`file_search` 和 artifact 注册等平台概念映射成本机工作流。

## 这不是什么

- 不是 OpenAI 官方包，也不是 OpenAI 内部平台服务。
- 不是任何内部文档技能环境的精确复制，也不声明行为等价。
- 对导入、改写、参考或第三方材料而言，除非已单独完成来源和许可审查，否则不是“所有内容都已清权”的完整开源发行版。
- 不包含生成 PDF、私有输入、实时 registry、`node_modules/` 或机器本地生产栈。

## 功能概览

- `skills/pdfs/` 下提供 PDF 渲染、检查、提取、编辑、脱敏、转换、预检、表单和产物注册辅助工具。
- `skills/pdfs/js/` 下提供基于 `pdf-lib` 和 `pdfjs-dist` 的 JavaScript PDF helper。
- `skills/docx/` 下提供 DOCX 任务文档和辅助脚本。
- 提供本地 PDF 生成、QA 渲染和非 OCR 工作流文档。
- 提交 `outputs/artifacts/registry.example.jsonl` 作为 artifact registry 行结构示例，不提交生成产物。
- `assets/` 下保留 Excalidraw/SVG/PNG 工作流图示资产。

## 快速开始

克隆后优先阅读 [`QUICKSTART.md`](./QUICKSTART.md)。

最短路径：

1. 激活自己的本机 PDF 生产栈，或按 [`skills/pdfs/docs/local-opencode-gpt55-install.md`](./skills/pdfs/docs/local-opencode-gpt55-install.md) 完成最小 Python/JS 设置。
2. 按 [`QUICKSTART.md`](./QUICKSTART.md) 验证 Python 和 JavaScript helper 依赖。
3. 创建本机 `data/` 和 `outputs/` 目录，用于输入文件、生成产物、QA 渲染图和 registry 行。

## 常见工作流

- PDF 阅读/审阅：[`skills/pdfs/SKILL.md`](./skills/pdfs/SKILL.md) 和 [`skills/pdfs/tasks/read_review.md`](./skills/pdfs/tasks/read_review.md)。
- 页面渲染，用于视觉 QA 或多模态复查：[`skills/pdfs/scripts/render_pdf.py`](./skills/pdfs/scripts/render_pdf.py)。
- HTML/Markdown/LaTeX 转 PDF：[`skills/pdfs/scripts/`](./skills/pdfs/scripts/) 下的转换脚本。
- Artifact 注册：[`skills/pdfs/scripts/artifact_registry.py`](./skills/pdfs/scripts/artifact_registry.py) 和 [`outputs/artifacts/registry.example.jsonl`](./outputs/artifacts/registry.example.jsonl)。
- DOCX 工作流：[`skills/docx/SKILL.md`](./skills/docx/SKILL.md)。
- 完整非 OCR 生产循环：[`PDF_PRODUCTION_WORKFLOW.md`](./PDF_PRODUCTION_WORKFLOW.md)。

![本地 PDF 详细工作流黑白手写图示](./assets/pdf-workflow-detail.png)

## 文档地图

- [`QUICKSTART.md`](./QUICKSTART.md)：克隆后最快本机验证路径。
- [`PDF_PRODUCTION_WORKFLOW.md`](./PDF_PRODUCTION_WORKFLOW.md)：完整本地非 OCR PDF 生产工作流。
- [`skills/pdfs/docs/platform-local-replacements.md`](./skills/pdfs/docs/platform-local-replacements.md)：平台概念的本地替代映射。
- [`skills/pdfs/docs/local-opencode-gpt55-install.md`](./skills/pdfs/docs/local-opencode-gpt55-install.md)：本地 OpenCode/GPT-5.5 安装说明。

## 仓库结构

```text
assets/                         工作流图示及源文件
skills/pdfs/                    本地适配的 PDF 工作台
skills/docx/                    导入的本地 DOCX 工作台
outputs/artifacts/registry.example.jsonl 已提交的 registry 示例
QUICKSTART.md                   克隆后快速验证指南
PDF_PRODUCTION_WORKFLOW.md      完整本地 PDF 生产指南
```

完整 PDF/DOCX 包清单保留在各自的 `SKILL.md`、`tasks/`、`docs/`、`scripts/`、`examples/` 和 `troubleshooting/` 目录中，不再在 README 首页重复展开。

## 运行时状态

默认本地流程：直接读取电脑或项目路径中的文件，用仓库脚本处理 PDF/DOCX，把生成产物写入 `outputs/`，并用 `artifact_registry.py` 注册重要输出。

这些运行时路径只属于本机，不应提交：

```text
data/
outputs/artifacts/registry.jsonl
outputs/generated-pdf/
outputs/full-stack-smoke/
outputs/prod-ocr-workflow/
```

`outputs/artifacts/registry.example.jsonl` 是唯一提交的 output-like 文件。详细平台路径映射见 [`skills/pdfs/docs/platform-local-replacements.md`](./skills/pdfs/docs/platform-local-replacements.md)。

## 许可与声明

本仓库是源码可见的混合来源工作台。请阅读 [`LICENSE`](./LICENSE) 中的许可边界，以及 [`NOTICE`](./NOTICE) 中的来源、商标和再分发说明。

不要在未单独确认来源和许可前，把任何导入、改写、参考或第三方材料视为已被本仓库重新授权或已清权可再分发。

## 限制

- 本地生产命令可能依赖机器本地工具，例如 MiKTeX、Pandoc、Poppler、Ghostscript、LibreOffice、qpdf、Playwright、Python 包和 Node 包。
- 默认流程不要求本地 OCR 引擎；扫描版或低文本 PDF 预期先渲染成图片，再使用 GPT-5.5 风格多模态读取。
- 最终 PDF 在完成前应重新渲染为图片进行 QA。
