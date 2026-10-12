# Classroom Video Insights
课堂视频复盘与证据分析平台 · 项目展示与精选实现

> 展示初稿。真实截图、报告和演示视频暂未公开。以下样例全部为合成数据，代码独立编写；生产代码公开权限尚待确认。

面向教师和教研人员，将课堂视频处理为可追溯的课堂记录、分析指标和复盘报告。关注长任务处理、证据边界、报告展示与部署可靠性。

## 我的职责
全流程负责：需求分析、产品流程、技术架构、视频预处理与分析流水线、前后端实现、接口兼容、测试、部署迁移与故障定位。详见[职责说明](docs/contributions.md)。

## 展示入口
| 内容 | 状态 |
| --- | --- |
| [任务处理、报告总览、证据回看截图](assets/screenshots/README.md) | 真实脱敏材料待补充 |
| [一分钟演示视频](assets/demo/README.md) | 待补充 |
| [合成报告预览](samples/report/report-preview.html) | 可本地打开的独立静态展示页面 |
| [样例 JSON](samples/report/report.sample.json) | 合成展示数据，不是生产交付 JSON |

预览页面独立编写，不代表原产品真实界面或课堂评价。

## 技术与架构
原系统采用 React、Vite、ECharts、Python、FastAPI，以及视频处理、ASR HTTP 服务和可配置语言模型。任务与运行产物持久化，部署经历原生进程和 Docker 环境。[架构说明](docs/architecture.md)

本仓库示例仅使用 Python 与 Node.js 标准库，无模型、密钥、视频或付费服务依赖。

## 三个工程案例
1. [证据与评分一致性](docs/case-studies/evidence-aware-scoring.md)：区分缺失证据、可靠零观测和部分可评价。
2. [异步视频处理](docs/case-studies/asynchronous-video-processing.md)：阶段状态、取消和失败恢复。
3. [部署与数据保全](docs/case-studies/deployment-and-data-preservation.md)：运行来源核对、历史保全与回滚。

## 运行精选示例
Python 3.10+、Node.js 22+：
~~~sh
python3 -m unittest discover -s examples/evidence-scoring -p 'test_*.py' -v
node --test examples/report-display/score-view.test.mjs
node scripts/render-report.mjs
python3 scripts/check-showcase.py
~~~
用浏览器打开 samples/report/report-preview.html。若需 HTTP 浏览：
~~~sh
python3 -m http.server 8000 --bind 127.0.0.1
~~~
访问 http://127.0.0.1:8000/samples/report/report-preview.html 。

## 验证、性能和许可
[验证记录](docs/validation.md)区分原系统验收与示例测试。
[性能核对](docs/performance.md)记录两个历史完整任务；它们不是新基准或普遍耗时承诺。
[第三方说明](THIRD_PARTY_NOTICES.md)、[许可核对](docs/license-review.md)、[限制](docs/limitations.md)。

原系统四仓库及内嵌分析包未发现许可证文件；未复制生产源码、依赖包或真实课堂材料，也未为其声明 MIT 许可。
