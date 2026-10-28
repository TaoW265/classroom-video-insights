# 系统架构

平台将课堂视频转换为结构化输入，经指标计算、模型分析与校验后，生成报告、图表和证据关联。

~~~mermaid
flowchart LR
    U[React 前端] --> A[FastAPI 视频 API]
    A --> D[(任务状态与产物索引)]
    A --> W[异步 Worker]
    W --> P[Step1 视频预处理]
    P --> S[外部 ASR 服务]
    P --> I[结构化课堂输入]
    I --> M[Step2 指标与模型分析]
    M --> V[结构及一致性校验]
    V --> R[报告 / 图表 / 证据关联]
    R --> U
~~~

| 模块边界 | 设计判断 |
| --- | --- |
| 页面与任务API | 任务状态独立保存，页面离开后仍能查询处理进度 |
| Step1与Step2 | 预处理生成结构化记录，分析按具体指标判断证据是否可用 |
| 计算与显示 | 分数、可评价范围和排除原因一起传递 |
| 代码与运行环境 | 分别核对提交、进程工作目录、解释器和数据路径 |

前端使用React、Vite与ECharts；后端使用Python和FastAPI。ASR与语言模型是可配置的外部服务。架构依据0.4.15分支的维护记录。

## 代码运行路径

~~~text
signals.synthetic.json → aggregate(signals) → report.sample.json
                      → scoreView(score, evaluation) → 终端结果
~~~

`run-demo.py`负责读取输入与生成JSON，`print-report.mjs`复用显示函数，输出文字、比较取值和范围说明。运行方法见[examples](../examples/README.md)，计算规则见[证据案例](case-studies/evidence-aware-scoring.md)。
