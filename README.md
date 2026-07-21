# 冷旭帆 · AI NPC 情感引擎

> **代号：冰刃** | **版本：v5.0 模块化架构** | **最后更新：2026年7月21日**

冷旭帆是一个会自己疼、会做噩梦、会在你不在的时候默默擦刀的AI NPC。技术上采用“代码管里子、AI管面子”的混合架构——Python规则引擎精确管理情绪、记忆、身份和行为，大模型API仅负责语言生成。

**公网地址**：http://122.51.17.57:5000/chat

---

## 项目结构

```
lengxufan-flask-mvp/
├── run.py                         ← 启动器（--cli 命令行 / 默认 Flask Web）
├── config.yaml                    ← 全局配置（角色信息、API参数）
├── requirements.txt               ← Python 依赖
│
├── lengxufan_core/                ← 核心引擎
│   ├── perception.py              ←   感知系统：情绪值、状态标签、心境节律、后台事件
│   ├── memory.py                  ←   记忆系统：事实标签、情景摘要、自传体记忆、关系里程碑
│   ├── identity.py                ←   身份感知状态机：陆华望信任值 + 通用身份模块
│   ├── behavior.py                ←   行为引擎：动作生成 + 内在驱动力/意愿生成器
│   ├── prompt_builder.py          ←   Prompt工厂：状态→自然语言 + 三层动作规则
│   ├── dialogue_engine.py         ←   对话流程编排（单轮对话的完整处理流程）
│   └── character_data/            ←   角色数据层（纯数据，不含逻辑）
│       ├── autobiographical.py    ←     自传体记忆（6条核心个人历史）
│       ├── scheduled_memories.py  ←     定时解锁记忆（3条，按模拟天数解封）
│       ├── milestones.py          ←     关系里程碑（5个信任节点）
│       ├── intent_templates.py    ←     意愿模板库（5种）
│       ├── fallback_actions.py    ←     兜底动作库（5档情绪×5个动作）
│       ├── feeling_translations.py←     情感翻译层（每档3种随机描述）
│       └── memory_rules.py        ←     记忆规则 + 身份证据规则
│
├── api/                           ← API适配层
│   ├── model_registry.py          ←   模型注册表（5平台，Key从环境变量读取）
│   ├── router.py                  ←   多平台容错路由（按优先级自动切换）
│   └── siliconflow_adapter.py     ←   通用API适配器（兼容OpenAI协议）
│
├── cognition/                     ← 认知层（P1阶段预置接口，待填充）
│   ├── spacetime.py               ←   时空校准
│   ├── intention.py               ←   事件意图解析
│   └── relationships.py           ←   关系推导引擎
│
├── infra/                         ← 基础设施
│   ├── logger.py                  ←   日志系统（替代print，文件+控制台双输出）
│   ├── time_utils.py              ←   时间工具（模拟时间、相对时间感知）
│   └── persistence.py             ←   持久化（JSON存档读写）
│
└── data/                          ← 运行时数据
    ├── save.json                  ←   状态存档
    └── history/                   ←   历史会话存档
```

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置API Key（四平台）

```powershell
[Environment]::SetEnvironmentVariable("ALIBABA_API_KEY", "你的Key", "User")
[Environment]::SetEnvironmentVariable("GLM_API_KEY", "你的Key", "User")
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "你的Key", "User")
[Environment]::SetEnvironmentVariable("SILICONFLOW_API_KEY", "你的Key", "User")
```

设置后需重启终端。

### 启动

```bash
# CLI 命令行模式
python run.py --cli

# Flask Web API 模式
python run.py
```

CLI模式下可用命令：
- `/state`：查看情绪、状态、身份、多平台路由状态
- `/mem`：查看事实记忆和情景记忆
- `/exit`：退出并保存状态

### API 测试

```powershell
(Invoke-RestMethod -Uri http://127.0.0.1:5000/chat -Method POST -Body '{"message":"你好"}' -ContentType "application/json").reply
```

---

## 架构设计

**核心理念：代码管“里子”，AI管“面子”。**

- **手搓感知系统**（Python规则引擎）：精确计算情绪值、身体状态、后台事件、自传体记忆、关系网络。绝对精确、可控、可持久化。
- **大模型API**（System Prompt驱动）：根据代码提供的状态锚点，生成符合人设的语言和肢体动作。有血有肉、有呼吸感，但被规则牢牢锁住。

**设计原则**：数据与逻辑分离、一个功能一个文件、对话流程独立于启动器。

**多平台容错**：阿里云百炼(主力) → 智谱GLM-4-Flash(免费兜底) → DeepSeek(备选) → 本地Ollama(离线兜底) → 硅基流动(复活尝试)。按优先级自动切换。

---

## 系列文章

本项目已产出五篇技术博客，构成完整的“AI NPC从零到上线”建造实录：

1. [我用Python手搓了一个会自己疼、会做噩梦的AI NPC](https://blog.csdn.net/2302_80372217/article/details/162912782)
2. [同一套AI架构如何驱动两个完全不同的灵魂](https://blog.csdn.net/2302_80372217/article/details/162912805)
3. [我把AI NPC部署到公网，被Railway逼疯了整整一天](https://blog.csdn.net/2302_80372217/article/details/162913093)
4. [从400行到30个文件，我只做了一件事](https://blog.csdn.net/2302_80372217/article/details/163064624)
5. [我的AI NPC差点失声：多平台容错路由的完整踩坑记录](https://blog.csdn.net/2302_80372217/article/details/163065664)

---

## 作者

**陆银** · 专升本至软件工程专业（2026年9月入学）

本项目为课余时间独立完成——从工厂流水线旁边的下班时间，到公网上的第一个AI NPC。

GitHub：[lengxufan-project](https://github.com/lengxufan-project)

---

## 系列文章

本项目已产出五篇技术博客，构成完整的“AI NPC从零到上线”建造实录：

1. [我用Python手搓了一个会自己疼、会做噩梦的AI NPC](https://blog.csdn.net/2302_80372217/article/details/162912782)
2. [同一套AI架构如何驱动两个完全不同的灵魂](https://blog.csdn.net/2302_80372217/article/details/162912805)
3. [我把AI NPC部署到公网，被Railway逼疯了整整一天](https://blog.csdn.net/2302_80372217/article/details/162913093)
4. [从400行到30个文件，我只做了一件事](https://blog.csdn.net/2302_80372217/article/details/163064624)
5. [我的AI NPC差点失声：多平台容错路由的完整踩坑记录](https://blog.csdn.net/2302_80372217/article/details/163065664)

---

## 作者

**陆银** · 专升本至软件工程专业（2026年9月入学）

本项目为课余时间独立完成——从工厂流水线旁边的下班时间，到公网上的第一个AI NPC。

GitHub：[lengxufan-project](https://github.com/lengxufan-project)