# 场景演示与触发示例 (Showcase & Test Prompts)

此文档列出了触发 `GCP KC Glossary Builder` (Google Knowledge Catalog 术语自动化引擎) 的真实用户对话示例。你可以直接复制这些话发给安装了该 Skill 的 AI Agent（如 Claude Code, OpenClaw 等）。

## 场景 1：从零开始提取并导入 (End-to-End Extraction)

> **你的输入 (User Prompt)**: 
> "这是一个关于电商业务的新版 PRD 文档（`retail_prd_v2.md`）。请你扮演 GCP KC Glossary Builder，帮我把里面的指标提取出来，生成一个业务术语表 JSON。然后运行 `import_glossary.py` 帮我导入到项目 `my-gcp-project` 的 `retail-glossary` 里。"

**Agent 的执行动作**:
1. 读取 `retail_prd_v2.md`，执行 Map-Reduce 摄取。
2. 提取并生成包含计算逻辑、责任人、数据密级等维度的 JSON 文件。
3. 提示确认，确认后后台执行 `import_glossary.py` 脚本，安全调用 Google Cloud API 进行异步导入。

---

## 场景 2：基于现有结果进行双向深度绑定 (Deep Binding)

> **你的输入 (User Prompt)**: 
> "我已经有了一个提取好的 `extracted.json`，请用 glossary builder 帮我执行深度绑定（Deep Binding）。我的 BigQuery dataset 是 `retail_dwh`。注意要确保相关的物理表和表里的字段都被反向打上了 Aspect 标签。"

**Agent 的执行动作**:
1. 校验 `extracted.json` 的完整性。
2. 执行 `bind_aspects.py`。
3. Agent 会实时反馈终端日志：“[+] Injecting Business Context into BigQuery Columns for v_trd_dist_ord_dtl...”。
4. 在 BigQuery 的列上注入业务计算公式和术语链接。

---

## 场景 3：无痕清理重置 (Clean Slate)

> **你的输入 (User Prompt)**: 
> "我们决定重新梳理业务大盘，请执行 glossary builder 的一键清理功能，把 `my-gcp-project` 下 `retail-glossary` 里的所有 terms 和 categories 全部干净地删掉，避免报错。"

**Agent 的执行动作**:
1. 自动调用 `delete_glossary.py` 脚本。
2. 执行安全的级联删除逻辑，规避 GCP 常见的 400 失败错误。
3. 报告清理完成，此时你的 Google KC 处于干净的空白状态。
