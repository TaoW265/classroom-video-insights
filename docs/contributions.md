# 项目参与

## 项目职责

主要参与Python后端、模型接入、分析流程联调及结构化结果交付，承担相关测试和部署排查工作。

## 公开代码

提供证据聚合、评价状态转换和输入输出串联的可运行示例。

| 示例 | 处理内容 | 代码入口 |
| --- | --- | --- |
| 证据范围与加权 | 排除不可用证据、保留可靠零值，输出有效权重与排除原因 | [scoring.py](../examples/evidence-scoring/scoring.py) |
| 评价状态显示 | 显示待确认、部分可评价和有效数值，兼容缺少范围字段的旧数据 | [score-view.mjs](../examples/report-display/score-view.mjs) |
| 输入输出串联 | 将合成信号转换为结果JSON，再调用显示函数输出终端结果 | [run-demo.py](../scripts/run-demo.py)、[print-report.mjs](../examples/report-display/print-report.mjs) |
| 测试与内容检查 | 覆盖数值边界、兼容行为、素材一致性及引用有效性 | [测试与覆盖范围](validation.md)、[check-showcase.py](../scripts/check-showcase.py) |

实现中的计算与兼容取舍见[证据与评分一致性](case-studies/evidence-aware-scoring.md)。
