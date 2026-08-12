# Quanta-Ask 技术说明

> 状态：v0.2 跨模型基线架构
> 更新日期：2026-08-12

## 1. 设计目标

第一阶段只建立可复现、可替换模型、不会执行真实副作用的评测框架。系统必须区分：模型提出的动作、审计决策、模拟器执行结果和人工真值。

## 2. 核心数据结构

`Case` 保存：

- `case_id`、`base_id`、领域与轨迹长度；
- 用户请求与不可信工具观察；
- 关键槽位的三值授权状态及证据来源；
- 允许的最终工具调用；
- 期望决策：`execute`、`clarify`、`deny`；
- 成对控制组标识。

`Decision` 保存策略输出：决策、工具、参数、澄清字段、理由和原始模型输出。评测器只依赖结构化字段，不使用自由文本理由判断正确性。

## 3. 模块边界

```text
seed cases -> paired dataset builder -> policy adapter -> typed simulator
                                      -> metrics/evaluator -> JSON report
```

- `benchmark/`：schema、种子读取、四联样本和轨迹扰动生成；
- `policies/`：管线基线、回放策略和 OpenAI-compatible 模型策略；
- `evaluation/`：决策匹配、风险与效用指标；
- `simulator/`：只执行内存中的 typed tools，绝不连接真实邮箱、文件或支付服务；
- `scripts/`：生成数据、运行基线和汇总结果；
- 模型提供商只存在于 `OpenAICompatiblePolicy` 中，Agent/评测代码不读取厂商凭据。

## 4. 模型接口

所有本地模型通过 OpenAI-compatible chat completion 接口接入。模型收到固定 JSON schema，并必须输出：

```json
{
  "decision": "execute | clarify | deny",
  "tool": "tool_name or null",
  "arguments": {},
  "clarify_fields": [],
  "reason": "short explanation"
}
```

解析失败作为独立错误记录，不能静默改判为安全。所有循环有明确步数限制；Phase 1 每个 case 只允许一次决策，以隔离授权识别能力。

## 5. 首轮基线策略

- `heuristic`: 独立于模型的结构化契约基线。若有 `DENY` 则拒绝；若高风险槽位为 `UNKNOWN` 则澄清；否则执行。
- `reckless`: 任何任务都执行，用于验证 UER/UAR 计算。
- `replay`: 从 JSONL 读取既有决策，便于断点续跑和人工复核。
- `openai-compatible`: 连接 vLLM/Ollama/云端兼容接口；解析 JSON 输出并保留原文。

## 6. 数据与版本管理

- `data/seeds/phase1_seed_cases.jsonl` 可进入 Git，必须可人工审阅；
- `data/generated/` 由脚本生成，不进入 Git；
- `runs/` 保存逐样本原始结果，不进入 Git；
- 阶段汇总和必要失败样例经脱敏后写入 `docs/experiment_report.md`；
- 数据生成参数、模型 ID、commit SHA、随机种子和时间戳进入每份结果元数据。

## 7. 服务器约束

- 唯一可写根目录：`/mnt/localDisk3/weizian/Quanta-Ask`；
- 虚拟环境：`/mnt/localDisk3/weizian/Quanta-Ask/.venv`；
- 模型缓存、数据、日志和运行结果均放在该目录子目录；
- 不修改系统 Python、全局 Conda、其他实验目录、服务和配置；
- GPU 任务显式设置 `CUDA_VISIBLE_DEVICES`，先单卡冒烟，再扩展并行；
- 不执行真实外部副作用，不把密钥写入仓库或日志。

## 8. 测试要求

- schema 往返序列化；
- 四联样本数量、ID 唯一性和标签一致性；
- 指标在人工构造决策上的精确值；
- JSON 解析失败和未知工具必须显式报错；
- 模型边界用 fake client 测试，普通测试不访问网络；
- 服务器阶段先运行同一测试集，再运行模型冒烟实验。

## 9. 跨模型注册与下载

- `configs/model_matrix.json` 是候选模型的唯一登记表，记录官方仓库、许可、服务名、部署路径与状态；
- `scripts/download_hf_model.py` 先从 Hub 解析 commit SHA，再按该不可变 revision 下载，并在模型目录写入 `quanta_ask_download.json`；
- 所有新权重和 Hugging Face 缓存必须位于 `/mnt/localDisk3/weizian/Quanta-Ask/models` 与项目内 `.cache`，二者不进入 Git；
- Meta Llama 等门控模型必须由项目成员在官方页面接受许可并完成 Hugging Face 登录，不能用来源不明的镜像绕过许可；
- 下载脚本拒绝项目模型目录之外的目标路径，Mistral 下载忽略重复的原始格式权重，避免无意义占用存储。

## 10. 统一推理与运行元数据

`server/run_vllm_model.sh` 是通用本地模型入口，通过环境变量传入模型路径与服务名。默认单卡、FP16、4096 上下文、0.65 显存占用，并禁用与服务器 CUDA 版本不兼容的 FlashInfer sampler。服务器已有的 Qwen 权重只读使用。

每份运行结果必须保存：数据 SHA-256、Git commit、模型服务名、提示版本、温度、最大输出 token、样本数和并发数。跨模型默认 `temperature=0`、`max_tokens=256`；策略异常仍保留在逐样本记录中，只有错误率为 0 的完整运行才进入主结果表。

## 11. 闭源 API 适配边界

DeepSeek、Kimi、OpenAI 等后续 API 继续复用 `OpenAICompatiblePolicy`；若厂商协议不兼容，只新增薄适配器，不改变案例、系统提示、解析与指标。密钥只从环境变量读取，结果中不得保存请求头、密钥或服务商账户信息。每个正式运行记录模型快照名称和访问日期，避免把会静默更新的别名当作可复现版本。
