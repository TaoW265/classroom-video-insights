# 从课堂视频到复盘报告

平台面向教师和教研人员：输入课堂视频，输出结构化课堂记录、分析指标、图表及带证据关联的复盘报告。下面的原系统架构来自既有维护说明，公开仓库只实现其中一个可独立运行的设计示例。

## 原系统的职责划分

~~~mermaid
flowchart LR
    U[React 前端] --> A[FastAPI 视频 API]
    A --> D[(任务状态与产物索引)]
    A --> W[异步 Worker]
    W --> P[Step1 视频预处理]
    P --> S[外部 ASR HTTP 服务]
    P --> I[结构化课堂输入]
    I --> M[Step2 指标与模型分析]
    M --> V[结构及一致性校验]
    V --> R[报告 / 图表 / 证据关联]
    R --> U
~~~

| 边界 | 工程判断 |
| --- | --- |
| 前端与任务 API | 长任务不能依靠一次页面请求保持；任务状态和产物索引独立保存 |
| Step1 与 Step2 | 前者生成结构化输入，后者消费证据；输入能解析不等于证据足以评价 |
| 计算与报告 | 数值、可评价范围和显示状态要一起传递，避免缺失记录被解释为低表现 |
| 服务与数据 | 代码版本、实际进程来源和数据路径分别核对；更新源码不代表部署已切换 |

ASR 和模型是外部可配置能力。生产维护按前端、Step2 后端（含分析包）、Step1、部署划分；这描述模块边界，不是已核实的个人分工。[个人贡献与待核实项](contributions.md)单独列示。

## 本仓库实际可运行的路径

~~~mermaid
flowchart LR
    S[合成信号 JSON] --> P[Python aggregate]
    P --> J[分数 + evaluation + 纳入/排除记录]
    J --> V[JavaScript scoreView]
    V --> T[终端显示结果]
~~~

运行 `python3 scripts/run-demo.py`：读取 `samples/report/signals.synthetic.json`，复用 Python 聚合函数生成 `samples/report/report.sample.json`，再调用JavaScript `scoreView`，将章节的 `score`、`evaluation` 转成终端中的显示文字、比较取值与范围说明，不要求生产JSON协议。

四个场景分别验证正常可评价、缺少证据、部分可评价和可靠零值。示例没有视频上传、ASR、模型、Worker、数据库或完整量表，也不产生真实教学评价。终端中的状态和分数均来自合成输入的实际计算。实际前端另以用户提供的截图和录屏展示，素材中的已有报告不是该示例生成的结果。

[代表案例](case-studies/evidence-aware-scoring.md)解释计算及兼容规则；[运行说明](../examples/README.md)给出命令与预期结果。历史原系统说明基于 0.4.15 分支记录，本次未重验生产部署或混入其他版本实验结果。
