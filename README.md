# 业务术语表提取工具 (Business Glossary Extractor)

企业级、基于 Nuwa/Luban 标准提纯的自动化流水线，用于从非结构化数据源（Wiki、PRD、大文本文件、多文档）中提取业务术语定义，并将其同步到 Google Cloud Dataplex 中。
> An enterprise-grade, Nuwa/Luban-distilled automated pipeline for extracting Business Glossary definitions from unstructured data sources (Wikis, PRDs, large text files, multiple documents) and synchronizing them into Google Cloud Dataplex.

## 🌟 核心特性 (Key Features)

1. **Map-Reduce 提取 (Map-Reduce Ingestion)**: 突破 LLM 上下文限制，通过重叠分块策略安全处理海量文档。
   > Break through LLM context limits. Safely ingest massive documents with overlapping chunking strategies.
2. **实体对齐去重 (Entity Resolution/Deduplication)**: 智能合并同义词，并在提取过程中解决冲突定义。
   > Intelligently merge synonyms and conflicting definitions on the fly.
3. **防幻觉结构化 (AI-Optimized Structuring)**: 将计算逻辑、物理表、物理字段扁平化整合进强结构化的 Markdown `说明 (Description)` 字段，彻底根除大模型在 Text-to-SQL 任务中的幻觉与截断问题。
   > Flattens logical formulas, related tables, and physical columns into a structured Markdown `Description` field to completely eradicate AI hallucination in Text-to-SQL tasks.
4. **自动化工具箱 (Dataplex Toolbelt)**: 提供健壮的、参数化的 Python 自动化脚本，安全处理 Dataplex 的异步长耗时操作 (LROs) 和底层数据的深度绑定。
   > Comes with robust, argument-driven Python automation scripts to safely handle Dataplex Long-Running Operations (LROs) and deep bindings.

## 🚀 架构设计 (5-State Machine Architecture)

1. **数据摄取与分块 (Map 阶段)**: 保留上下文的重叠读取。
   > **Data Ingestion & Chunking (Map Phase)**: Overlapping reads for context preservation.
2. **语义提取与对齐 (Reduce 阶段)**: 全局内存用于术语去重和冲突消解。
   > **Semantic Extraction & Alignment (Reduce Phase)**: Global memory for term deduplication and conflict resolution.
3. **AI 友好型结构化 (AI-Optimized Structuring)**: 强制使用 Markdown 约束模式，针对检索增强生成 (RAG) 进行优化。
   > Enforces strict Markdown schemas to optimize for Retrieval-Augmented Generation (RAG).
4. **质量门禁与验证 (Validation & Quality Gate)**: Dataplex 长度合规校验、空格清理、完整性审计。
   > Dataplex length checks, whitespace stripping, and completeness auditing.
5. **输出与交接 (Output & Handoff)**: 校验大盘与自动化执行流交接。
   > Review dashboard and automated execution handoff.

## 📦 工具箱指南 (Toolbelt Scripts)

首先安装依赖：
> Install dependencies first:
```bash
pip install -r requirements.txt
```

### 1. 导入术语表 (Import Glossary: `import_glossary.py`)
解析提取的 JSON 并将分类 (Categories) 和术语 (Terms) 导入 Dataplex，无缝处理异步长耗时操作 (LRO)。
> Parses the extracted JSON and imports Categories and Terms into Dataplex, handling asynchronous LROs seamlessly.
```bash
python scripts/import_glossary.py --project_id=YOUR_PROJECT --project_num=YOUR_PROJECT_NUM --glossary_id=YOUR_GLOSSARY_ID --json_file=extracted.json
```

### 2. 深度绑定 (Deep Binding: `bind_aspects.py`)
扫描术语，解析其 `Description` 中的关联表，并自动附加 Dataplex 切面 (`has_calculation`, `has_physical_mapping`) 以及 BigQuery 底层实体链接 (Entry Links)。
> Scans terms, parses their `Description` for related tables, and automatically attaches Dataplex Aspects (`has_calculation`, `has_physical_mapping`) and BigQuery Entry Links.
```bash
python scripts/bind_aspects.py --project_id=YOUR_PROJECT --project_num=YOUR_PROJECT_NUM --glossary_id=YOUR_GLOSSARY_ID --json_file=extracted.json --dataset=YOUR_BQ_DATASET
```

### 3. 一键清理 (Cleanup: `delete_glossary.py`)
安全执行级联删除 (术语 -> 分类目录 -> 术语表根节点) 以彻底销毁字典，避免 GCP 抛出 `400 Failed Precondition` 错误。
> Safely performs a cascading deletion (Terms -> Categories -> Glossary) to avoid GCP `400 Failed Precondition` errors.
```bash
python scripts/delete_glossary.py --project_id=YOUR_PROJECT --project_num=YOUR_PROJECT_NUM --glossary_id=YOUR_GLOSSARY_ID
```

## 📄 许可协议 (License)
本项目基于 MIT 协议开源 - 详情请参阅 [LICENSE](LICENSE) 文件。
> This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
