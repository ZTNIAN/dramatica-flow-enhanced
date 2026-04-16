# Dramatica-Flow Enhanced — 项目交接文档 V1

> 最后更新：2026-04-17
> 下次交接时，把本文件发给 AI，它就能一次读懂整个项目。

---

## 一、项目概述

### 这是什么？

**Dramatica-Flow Enhanced** 是一个 AI 自动写小说系统。你给它一句话设定，它帮你：
1. 构建完整世界观（角色/势力/地点/规则）
2. 生成三幕结构大纲 + 逐章规划
3. 一章一章自动写（每章2000字）
4. 写完自动审计（9维度打分 + 17条红线）
5. 不合格自动修订，最多返工3轮

### 核心卖点

**它不只是"AI写字"，而是"AI理解故事"。**
- 因果链管理：每个事件必须回答"因为什么→发生了什么→导致了什么"
- 信息边界：角色不能知道他没见过的事（杜绝全知视角污染）
- 伏笔生命周期：埋设→追踪→预警→回收
- 情感弧线：1-10级追踪角色情绪变化
- 多线叙事：主线/支线/并行线/闪回线

### 技术栈

- **语言**：Python 3.11+
- **后端**：FastAPI
- **CLI**：Typer
- **数据库**：文件系统（JSON + Markdown）
- **LLM**：DeepSeek API（默认）/ Ollama（本地免费）
- **前端**：单文件 HTML（dramatica_flow_web_ui.html）

---

## 二、项目来源与演进

### 原版：dramatica-flow

- GitHub: https://github.com/ydsgangge-ux/dramatica-flow
- 特点：叙事逻辑强（因果链/信息边界/伏笔），但缺乏前期规划能力和写作质量管控
- 5个Agent：建筑师、写手、审计员、修订者、摘要生成

### 增强来源：OpenMOSS

- 多Agent协作平台，擅长前期设计（世界观/大纲/市场调研）
- 4种角色：Planner/Executor/Reviewer/Patrol
- 知识库系统 + 去AI味规则 + 95分加权评分
- 操作手册：https://github.com/user/openmoss（用户的私有项目）

### 增强版：dramatica-flow-enhanced

- GitHub: https://github.com/ZTNIAN/dramatica-flow-enhanced
- = 原版核心 + OpenMOSS优点 + 新增3个规划Agent
- 12个增强点全部完成（见下方清单）

---

## 三、12个增强点清单

| # | 增强点 | 类型 | 文件位置 |
|---|--------|------|----------|
| 1 | 9维度加权评分 | 审计 | core/agents/__init__.py |
| 2 | 17条红线一票否决 | 审计 | core/agents/__init__.py |
| 3 | 禁止词汇清单+正则扫描 | 验证 | core/validators/__init__.py |
| 4 | 知识库目录+prompt注入 | 知识 | core/knowledge_base/ + core/agents/__init__.py |
| 5 | 45条写作风格约束 | 写作 | core/agents/__init__.py（WRITER_SYSTEM_PROMPT） |
| 6 | Show Don't Tell转换表 | 写作 | core/validators/__init__.py + core/agents/__init__.py |
| 7 | 修改前后对比示例库 | 知识 | core/knowledge_base/before_after_examples.md |
| 8 | 返工上限改3+监控 | 管线 | core/agents/__init__.py + core/pipeline.py |
| 9 | 动态分层规划 | 规划 | core/dynamic_planner.py |
| 10 | 巡查Agent | 管线 | core/agents/__init__.py（PatrolAgent） |
| 11 | 质量统计仪表盘 | 统计 | core/quality_dashboard.py |
| 12 | 知识库查询激励 | 统计 | core/kb_incentive.py |

---

## 四、文件结构

```
dramatica-flow-enhanced/
├── cli/
│   └── main.py                    # CLI入口，13个命令
├── core/
│   ├── agents/
│   │   └── __init__.py            # 9个Agent（核心文件，最大）
│   ├── knowledge_base/            # 知识库（新增）
│   │   ├── anti_ai_rules.md       # 去AI味规则
│   │   ├── writing_techniques.md  # 写作技巧
│   │   └── before_after_examples.md # 对比示例
│   ├── llm/
│   │   └── __init__.py            # LLM抽象层（DeepSeek/Ollama）
│   ├── narrative/
│   │   └── __init__.py            # 叙事引擎（因果链/伏笔/时间轴）
│   ├── state/
│   │   └── __init__.py            # 状态管理（world_state/truth files）
│   ├── types/
│   │   ├── narrative.py           # 核心类型（角色/线程/事件）
│   │   └── state.py               # 状态类型（因果链/情感/伏笔）
│   ├── validators/
│   │   └── __init__.py            # 写后验证器（13类规则扫描）
│   ├── pipeline.py                # 写作管线（建筑师→写手→巡查→审计→修订）
│   ├── server.py                  # FastAPI服务器（Web UI + API）
│   ├── setup.py                   # 项目初始化
│   ├── dynamic_planner.py         # 动态分层规划（新增）
│   ├── quality_dashboard.py       # 质量仪表盘（新增）
│   └── kb_incentive.py            # 知识库查询激励（新增）
├── templates/                     # JSON配置模板
├── books/                         # 书籍数据目录
├── docs/                          # 文档+截图
├── .env                           # 环境变量（API Key等）
├── pyproject.toml                 # 项目配置
├── PROJECT_HANDOFF.md             # 本文件
├── USER_MANUAL.md                 # 操作手册
└── dramatica_flow_web_ui.html     # Web UI单文件
```

---

## 五、9个Agent详解

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **WorldBuilderAgent** | 从一句话生成世界观 | 一句话设定+题材 | 角色/势力/地点/规则JSON |
| **OutlinePlannerAgent** | 生成三幕大纲+章纲 | 世界观JSON | 章纲JSON+张力曲线 |
| **MarketAnalyzerAgent** | 市场分析 | 题材+平台 | 风格指南+读者偏好 |
| **ArchitectAgent** | 规划单章蓝图 | 章纲+世界状态 | 蓝图（核心冲突/伏笔/情感弧） |
| **WriterAgent** | 生成章节正文 | 蓝图+世界状态 | 正文+结算表 |
| **PatrolAgent** | 快速扫描（P0/P1/P2） | 正文+蓝图 | 通过/打回 |
| **AuditorAgent** | 9维加权审计 | 正文+蓝图+真相文件 | 评分+问题清单 |
| **ReviserAgent** | 修订正文 | 正文+问题清单 | 修订后正文 |
| **SummaryAgent** | 生成章节摘要 | 正文+结算表 | 结构化摘要 |

---

## 六、写作管线流程

```
[世界构建] 一句话设定 → WorldBuilderAgent → 世界观JSON
    ↓
[大纲规划] 世界观 → OutlinePlannerAgent → 三幕结构 + 章纲
    ↓
[单章循环]（每章重复以下流程）
    ├── 快照备份
    ├── 建筑师：规划蓝图（核心冲突/伏笔/情感弧/状态卡）
    ├── 写手：生成正文（2000字硬限制）+ 结算表
    ├── 验证器：零LLM硬规则扫描（13类禁止词/Tell式表达）
    ├── 巡查者：P0/P1/P2快速扫描 → 打回修正
    ├── 审计员：9维度加权评分（≥95分+单项≥85+无红线）
    │   └── 不通过 → 修订者修正 → 再审（最多3轮）
    ├── 保存最终稿
    ├── 因果链提取
    ├── 摘要生成 → chapter_summaries.md
    └── 状态结算 → world_state.json
```

---

## 七、踩坑记录（重要！）

### 坑1：heredoc写中文文件会损坏
- **现象**：用 `cat > file << 'EOF' ... EOF` 写中文内容到文件，结果文件出现乱码
- **原因**：heredoc对中文字符+特殊符号处理不可靠，内容太长更容易出错
- **解决**：用 `python3 -c "with open('file','w') as f: f.write('内容')"` 或 `python3 << 'PYEOF' ... PYEOF`
- **教训**：**别用heredoc写中文代码文件，用python3的文件读写**

### 坑2：sed无法匹配中文字符
- **现象**：`sed -i 's/中文/替换/' file` 不报错但不生效
- **原因**：sed对UTF-8多字节中文字符的正则匹配不可靠
- **解决**：用 `python3 -c "import pathlib; p=pathlib.Path('file'); p.write_text(p.read_text().replace('中文','替换'))"`
- **教训**：**涉及中文内容修改，别用sed，用python3**

### 坑3：catbox文件链接72小时过期
- **现象**：litter.catbox.moe 链接全部404
- **解决**：需要重新上传。上传命令：
  ```
  curl -F "reqtype=fileupload" -F "time=72h" -F "fileToUpload=@/路径/文件" https://litterbox.catbox.moe/resources/internals/api.php
  ```

### 坑4：Python虚拟环境
- **现象**：`pip install -e .` 报 `externally-managed-environment`
- **原因**：Python 3.12+ 系统级pip被锁定
- **解决**：
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  ```

### 坑5：entry point缓存
- **现象**：修改了cli/main.py但`df --help`不显示新命令
- **原因**：pip entry point缓存 + __pycache__
- **解决**：
  ```bash
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
  pip install --force-reinstall --no-deps -e .
  ```

### 坑6：git pull不更新
- **现象**：`git pull` 说 Already up to date 但本地文件不是最新
- **原因**：本地HEAD和远程HEAD不一致（可能有reset等操作）
- **解决**：
  ```bash
  git fetch origin
  git reset --hard origin/main
  ```

### 坑7：from ..llm 导入bug
- **现象**：从GitHub下载文件后出现 `from ..llm` 报错
- **解决**：改成 `from .llm`
  ```bash
  python3 -c "import pathlib; p=pathlib.Path('file.py'); p.write_text(p.read_text().replace('from ..llm','from .llm'))"
  ```

### 坑8：DeepSeek API Key安全
- **警告**：API Key不要发在聊天记录里！用.env文件配置
- **.env文件不要提交到git**（.gitignore已排除）

---

## 八、已知未完成/待优化

### 功能层面
1. **Web UI未集成新功能**：worldbuild/outline/market三个新命令只有CLI，Web UI没有对应页面
2. **知识库prompt注入不完整**：知识库文件已创建，但只有WriterAgent的prompt注入了去AI味规则，Architect/Auditor没有注入写作技巧库
3. **质量仪表盘未接入管线**：quality_dashboard.py已创建，但pipeline.py没有调用它来记录每章的统计数据
4. **知识库查询激励未接入**：kb_incentive.py已创建，但没有Agent实际调用它
5. **动态规划器未接入管线**：dynamic_planner.py已创建，但pipeline和CLI都没有使用它
6. **对比示例库未注入prompt**：before_after_examples.md已创建，但没有注入到任何Agent的prompt里

### 代码层面
7. **server.py未更新**：API端点没有暴露新Agent的功能
8. **setup.py未更新**：包安装配置可能缺少新模块的依赖
9. **没有测试覆盖**：新Agent和增强功能没有单元测试
10. **错误处理不完善**：LLM调用失败时的降级策略不明确

### 数据层面
11. **番茄小说市场数据未集成**：OpenMOSS有完整的番茄小说调研报告，增强版没有引入
12. **示例库太小**：before_after_examples.md只有7组示例，OpenMOSS有更多好/坏示例

---

## 九、下一步优化建议（按优先级）

### P0 - 立即做（效果最直接）
1. **接入质量仪表盘到管线**：pipeline.py每章写完后自动记录ChapterStats
2. **对比示例库注入Writer prompt**：在WRITER_SYSTEM_PROMPT中追加3-5组示例
3. **知识库注入Architect prompt**：让建筑师也能参考写作技巧

### P1 - 尽快做
4. **Web UI添加世界观构建页面**：一个表单输入设定，点击生成，可视化展示结果
5. **Web UI添加大纲规划页面**：展示三幕结构+章纲表格+张力曲线图
6. **完善错误处理**：LLM超时/返回格式错误时的重试和降级

### P2 - 后续做
7. **引入番茄小说市场数据**：作为知识库文件注入MarketAnalyzerAgent
8. **动态规划器接入管线**：根据实际写作进度自动调整后续章纲
9. **知识库查询激励可视化**：在Web UI展示Agent查询知识库的频率
10. **添加单元测试**：至少覆盖validators和新增Agent的基本功能

---

## 十、环境配置速查

### .env 文件内容
```
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEFAULT_WORDS_PER_CHAPTER=2000
DEFAULT_TEMPERATURE=0.7
AUDITOR_TEMPERATURE=0.0
BOOKS_DIR=./books
```

### 启动方式
```bash
# CLI模式
cd ~/dramatica-flow-enhanced && source .venv/bin/activate
df --help

# Web UI模式
uvicorn core.server:app --reload --host 0.0.0.0 --port 8766
# 浏览器打开 http://127.0.0.1:8766/
```

### Git操作
```bash
# 拉取最新代码
git fetch origin && git reset --hard origin/main

# 推送改动（需要有写权限的token）
git add -A && git commit -m "描述" && git push origin main
```

---

## 十一、关键配置文件

### pyproject.toml
- 入口点：`df = "cli.main:app"`
- Python要求：>=3.11
- 核心依赖：typer, rich, pydantic, httpx, fastapi, uvicorn

### .gitignore
- 排除：.env, __pycache__, .venv, books/, *.db

---

## 十二、联系与资源

- 原版仓库：https://github.com/ydsgangge-ux/dramatica-flow
- 增强版仓库：https://github.com/ZTNIAN/dramatica-flow-enhanced
- DeepSeek API：https://platform.deepseek.com
- Dramatica理论：https://dramatica.com

---

*本文档由AI自动生成，下次交接时发给AI即可快速理解整个项目。*
