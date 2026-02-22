## AutoResume — 自动化投递管理系统 (MVP + 架构评审 + 改进方案)

**Current Status:** MVP完成 + 企业级架构评审已交付 ✅

### 你现在有什么：
1. **MVP (MVP 能用):** CSV数据层 + 关键词分类器 + espanso快捷短语
2. **架构评审 (详细计划):** 完整的改进路线图、代码示例、优先级、时间估算
3. **行动计划:** 第一天怎么开始的分步指南

---

## 📂 项目文件

### 核心数据文件
- `data/Profiles.csv` — 身份库（Airtable 导入模板）
- `data/ResumeVariants.csv` — 简历版本库
- `data/QuestionBank.csv` — 问答库（短/中/长三档）
- `data/Applications.csv` — 投递追踪模板

### 工具 & 脚本
- `classify_jd.py` — 关键词分类器（输入JD → 输出岗位类别 + 建议简历）
- `test_classify.py` — 测试脚本
- `espanso/snippets.yml` — 快捷短语示例

### 简历
- `Resumes/2026_Summer/` — 简历文件（占位PDF，请替换为真实版本）

快速开始

### 方案 1: MVP 模式（现在就开始投递）

1. 导入 Airtable
   - 新建一个 Base，分别创建四张表：Profiles / Resume Variants / Question Bank / Applications
   - 在每张表中使用 CSV 导入（Airtable 的 + 按钮 → Import → CSV）并选择对应 CSV 文件。

2. 替换简历 PDF
   - 把你真实的 PDF 放进 `Resumes/2026_Summer/`，并在 `ResumeVariants.csv` 中更新 `File` 字段为对应文件名。

3. 安装 espanso（选配）并导入片段
   - macOS: `brew install espanso`（或从官网安装）
   - 将 `espanso/snippets.yml` 的内容合并到 `~/.config/espanso/match/` 下的 yml 文件，或直接替换 espanso 配置。

4. 运行本地 JD 分类器（可选）
   - 测试：

```bash
python3 classify_jd.py --text "We are hiring for a Quant Equity Researcher to build factor models and backtest signals."
```

输出示例：建议 Role Category = Quant Equity Research，Resume = ZhouShuyi_QuantEquity_Resume_2026.pdf

### 方案 2: 企业级重构（如果你想投入1-2周）

如果你想把这个项目变成**生产级质量**，我已经准备好了完整的架构评审和改进方案。

**从这里开始：**

1. **5分钟快速了解:** 读 `QUICK_REFERENCE.md`
2. **做决策:** 读 `ARCHITECTURE_SUMMARY.md` + `DECISION_MATRIX.md`（选择场景 A/B/C）
3. **开始编码:** 按照 `DAY1_ACTION_PLAN.md`
4. **获取完整计划:** 读 `ARCHITECTURE_REVIEW.md`（所有代码示例和实现细节）

**文档导航：** 看 `DOCS_INDEX.md` 了解如何导航这些文档

---

## 📖 新增文档 - 架构评审 & 改进方案

### 核心文档

| 文档 | 大小 | 用途 |
|------|------|------|
| **QUICK_REFERENCE.md** | 2页 | ⚡ 5分钟快速概览 |
| **ARCHITECTURE_SUMMARY.md** | 4页 | 📊 决策文档（要不要重构？） |
| **DECISION_MATRIX.md** | 6页 | 🎯 优先级 + 3个场景 + 时间表 |
| **ARCHITECTURE_REVIEW.md** | 12页 | 🔍 完整深度分析（1200+行） |
| **DAY1_ACTION_PLAN.md** | 8页 | ✍️ 第一天编码指南（复制即用） |
| **DOCS_INDEX.md** | 5页 | 📚 文档导航和阅读路径 |

**总计:** ~37页的生产级架构和改进方案

### 覆盖的 8 个方面

✅ **1. 架构评审** — 识别了 9 个主要弱点，按严重程度分类  
✅ **2. 结构化重构** — 提议的新文件夹结构和模块化  
✅ **3. CLI 改进** — 子命令、JSON输出、日志、exit codes  
✅ **4. 数据建模** — 规范化、ID、外键、验证  
✅ **5. 有意义的特性** — 置信度评分、问题建议、应用追踪  
✅ **6. 工程质量** — 类型提示、文档、测试、linting  
✅ **7. 安全与隐私** — PII掩码、文件验证、样本数据模式  
✅ **8. 优先级和时间表** — Tier 1/2/3 细分，时间估算 1-2 周  

### Tier 系统

**Tier 1 (12-18小时): MVP → 生产级**
- P0.1: 域模型 (RoleCategory enum, dataclasses)
- P0.2: 数据层抽象 (CSV → 类型化模型)
- P0.3: 分类器接口 (可插拔)
- P0.4: 配置系统 (config.yaml)
- P0.5: CLI 重构 (JSON + 日志)
- P0.6: 单元测试

**Tier 2 (8-12小时): 功能增强**
- P1.1: 置信度评分 (加权关键词)
- P1.3: 问题推荐
- P1.5: 应用分析
- P1.6: 状态枚举

**Tier 3 (未来): 可选**
- SQLite 迁移
- 浏览器扩展
- Airtable API 同步

### 快速对比

| 方面 | MVP (现在) | Tier 1后 |
|------|-----------|----------|
| 硬编码 | ❌ 关键词在代码里 | ✅ config.yaml 驱动 |
| 数据验证 | ❌ 无 | ✅ Pydantic schemas |
| 类型安全 | ❌ 无 | ✅ 90%+ 类型注解 |
| 可扩展性 | ⚠️ 困难 | ✅ 模块化设计 |
| 测试覆盖 | 🟡 10% | ✅ 70%+ |
| 错误处理 | ⚠️ 基础 | ✅ 结构化日志 + 出错代码 |

---

## 🚀 建议路径

### 📍 如果你现在用 MVP:
1. 用 Airtable 导入 CSV
2. 用 espanso 快速填答
3. 每天 2-6 分钟完成投递
4. 遇到新问题加入 QuestionBank

### 📍 如果你想下个月升级:
1. 读 `QUICK_REFERENCE.md` (5 min)
2. 读 `DECISION_MATRIX.md` (15 min)
3. 选择场景 (A=完整 / B=快速 / C=最小)
4. 按 `DAY1_ACTION_PLAN.md` 开始编码

### 📍 如果你现在想理解全部:
1. 读 `DOCS_INDEX.md` (找你的角色)
2. 按推荐顺序读文档
3. 参考 `ARCHITECTURE_REVIEW.md` 所有代码示例

---

## ✅ 本轮完成清单

**MVP (第1周已完成):**
- ✅ CSV 数据模板 (Airtable 导入)
- ✅ 关键词分类器
- ✅ espanso 快捷短语
- ✅ 投递追踪表

**架构评审 (本轮新增):**
- ✅ 完整的架构分析 (1200+行)
- ✅ 改进路线图 (Tier 1/2/3)
- ✅ 优先级矩阵
- ✅ 第一天编码指南
- ✅ 所有代码示例
- ✅ 时间和努力估算

**你现在可以:**
1. ✅ 立刻开始用 MVP 投递（2-6分钟/份）
2. ✅ 理解需要什么工程投入来升级
3. ✅ 决定何时重构、优先什么特性
4. ✅ 按照计划分步实施

---

## 💡 下一步

**立刻可做:**
- 用 MVP 模式投递 → 尽快熟悉流程
- 把真实简历 PDF 放进 `Resumes/2026_Summer/`
- 用 espanso 快速短语节省时间

**之后可选:**
- 阅读架构文档（决定要不要重构）
- 如果要升级，按 `DAY1_ACTION_PLAN.md` 开始

---

**祝投递顺利！🚀**

有问题？参考 `DOCS_INDEX.md` 里的常见问题和文档导航。
