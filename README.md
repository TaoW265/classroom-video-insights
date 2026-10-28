# Classroom Video Insights

**课堂视频复盘与证据分析平台 · 工程作品集**

面向教师和教研人员，把课堂视频整理成结构化课堂记录、分析指标和可回看的复盘报告，减少在长视频中反复查找片段的成本。本作品集展示实际前端报告界面，并通过独立编写的可运行示例，说明**证据缺失、评分计算与显示状态如何保持一致**。

**原平台：**课堂视频 → 预处理与转写 → 分析与校验 → 报告、图表和证据片段。

**公开代码示例：**合成信号 → Python 证据范围判断及聚合 → JSON → JavaScript 显示结果，无模型或付费服务依赖。

## 先看效果

[产品截图与图注](assets/screenshots/README.md) · [实际操作录屏](assets/demo/product-walkthrough.mp4) · [录屏说明](assets/demo/README.md) · [合成输入](samples/report/signals.synthetic.json) · [示例输出](samples/report/report.sample.json)

![实际前端的教学模式分析界面：章节诊断、课堂模式、发现与建议；用户提供素材的裁切版本](assets/screenshots/teaching-mode.png)

*截图来自用户提供的前端报告素材，展示已有结果的阅读方式；不是本轮新跑分析，也不是合成示例输出。界面中的分数和指标仅用于说明显示内容，不作为准确率或新验收结论。*

[![实际前端操作录屏封面](assets/demo/poster.png)](assets/demo/product-walkthrough.mp4)

*点击封面查看用户提供录屏的编辑版本。保留实际报告浏览过程，裁去身份信息、历史列表和课堂画面，去除音轨；[五张截图](assets/screenshots/README.md)分别展示报告总览、教学模式、Rt–Ch图、话语分布与指标说明。*

## 我负责什么

| 范围 | 可以核查的工作 | 贡献口径 |
| --- | --- | --- |
| 本公开代码示例 | 证据范围与加权规则、状态显示、合成输入到JSON及终端显示的生成、测试与内容检查 | 独立编写，可直接运行；不是实际前端源码 |
| 原平台维护 | 需求与流程、预处理和分析接口、任务与报告链路、前端状态及历史兼容、回归与部署排查 | 既有职责记录；具体模块的独立实现与主要维护范围待逐项核实 |
| 团队协作 | 核心生产代码被合作团队用于尚在内测的产品 | 合作团队的产品化、后续开发和上线成果不归为个人成果 |

[个人贡献与待核实分工](docs/contributions.md)。ASR、语言模型和框架属于外部能力。

## 架构与技术判断

~~~text
原平台：视频 → Step1 预处理 / ASR → Step2 指标与模型分析
                                      ↓
                       结构与一致性校验 → 报告 / 图表 / 证据

公开示例：signals.synthetic.json → aggregate(signals)
               → report.sample.json → scoreView → 终端显示结果
~~~

原系统使用 React、Vite、ECharts、Python、FastAPI 及外部 ASR/语言模型。公开代码只使用 Python 与 Node.js 标准库；截图和录屏用于展示真实前端，示例不重建该界面。详见[架构说明](docs/architecture.md)。

## 三个代表案例

**[证据与评分一致性](docs/case-studies/evidence-aware-scoring.md)**：缺少学生证据不能当成低分；可靠零值继续参与计算；部分可评价时缩小有效分母，并在显示端说明范围。包含输入输出、错误算例、旧数据兼容、测试和取舍。

| 合成场景 | Python结果 | JavaScript显示 | 判断 |
| --- | --- | --- | --- |
| 正常可评价 | 85 / available | 85 | 两项有效信号按权重聚合 |
| 缺少证据 | null / unavailable | 待确认 | 不把兼容数值50当成评价 |
| 部分可评价 | 80 / partial | 80，附范围说明 | 不可用项退出加权，保留有效教师侧信号 |
| 可靠零值 | 0 / available | 0 | 有效零值保留，不能按数值猜缺失 |

**[异步视频处理](docs/case-studies/asynchronous-video-processing.md)**：阶段进度、取消和失败应与“报告是否可评价”分开，说明原系统的流程和边界。

**[部署与数据保全](docs/case-studies/deployment-and-data-preservation.md)**：维护时核对实际运行来源、可写存储和历史数据，说明迁移与回滚所需判断。

## 运行公开示例

需要 **Python 3.10+、Node.js 22+**，不需要安装Python/npm依赖。从仓库根目录运行：

~~~sh
python3 scripts/run-demo.py
~~~

命令生成[结果JSON](samples/report/report.sample.json)，再调用JavaScript显示函数，在终端输出四种状态：**85、待确认、80（部分可评价）、0**。也可单独运行显示端：

~~~sh
node examples/report-display/print-report.mjs samples/report/report.sample.json
~~~

字段映射、兼容行为和完整命令见[examples](examples/README.md)。实际界面通过本页截图和录屏查看；仓库不提供替代前端或另建演示页面。

## 验证与展示范围

~~~sh
python3 -m unittest discover -s examples/evidence-scoring -p 'test_*.py' -v
node --test examples/report-display/*.test.mjs
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/run-demo.py --check
python3 scripts/check-showcase.py
~~~

[本次验证记录](docs/validation.md)列出实际测试及媒体检查；原系统历史数字单独存档。[历史性能记录](docs/performance.md)不是本示例基准，也不构成准确率或通用耗时承诺。

实际前端素材由仓库所有者提供并授权发布本次编辑版本，原件保留在本机且排除仓库交付；完整生产源码、课堂音视频、转写和内部数据不在公开代码范围。真实界面与合成代码示例分别标注，简化规则不等于生产完整量表或评价算法。职责细分及其他素材的公开范围见[贡献说明](docs/contributions.md)；[展示限制](docs/limitations.md)、[来源与第三方说明](THIRD_PARTY_NOTICES.md)、[许可核对](docs/license-review.md)。未为原系统声明MIT等许可证，未发布独立网站。有限内容扫描不替代完整隐私或法律审计。
