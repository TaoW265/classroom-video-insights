# 合成示例输入与结果

本目录全部为独立示例／合成数据，不含真实课堂转写或身份，也不是生产交付`analysis_delivery.json`。

| 文件 | 用途 |
| --- | --- |
| [signals.synthetic.json](signals.synthetic.json) | 人工编写的四种输入场景，包含数值、权重和证据范围 |
| [report.sample.json](report.sample.json) | Python聚合生成的结果，包含计入项、排除原因和有效权重 |

从仓库根目录运行`python3 scripts/run-demo.py`，重建JSON并调用JavaScript显示函数，在终端得到85、待确认、80（部分可评价）和0。运行`python3 scripts/run-demo.py --check`，验证JSON生成一致性而不写文件。完整命令、字段映射和兼容规则见[示例说明](../../examples/README.md)。

本目录的四种证据状态来自合成输入，实际前端另以用户提供的[截图](../../assets/screenshots/README.md)和[录屏](../../assets/demo/README.md)展示。两者的输入、数据与用途不同，不将前端已有报告说成此示例的输出，也不把终端示例当作生产算法的完整实现。
