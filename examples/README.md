# 运行示例

需要Python 3.10+和Node.js 22+，仅使用标准库。以下命令均在仓库根目录运行：

~~~sh
python3 scripts/run-demo.py
~~~

程序读取[合成信号](../samples/report/signals.synthetic.json)，经[聚合函数](evidence-scoring/scoring.py)生成[结果JSON](../samples/report/report.sample.json)，再调用[显示函数](report-display/score-view.mjs)输出终端结果。

| 场景 | score / evaluation | 显示结果 |
| --- | --- | --- |
| 正常可评价 | `85 / available` | 85 |
| 缺少证据 | `null / unavailable` | 待确认 |
| 部分可评价 | `80 / partial` | 80，附范围说明 |
| 可靠零值 | `0 / available` | 0 |

单独读取生成结果：

~~~sh
node examples/report-display/print-report.mjs samples/report/report.sample.json
~~~

## 字段映射

每章的`signals`交给`aggregate`，生成的`score`和`evaluation`原样交给`scoreView`。`included`、`excluded`和`effective_weights`保留计算依据；`id`、`title`和`narrative`用于显示，不参与评分。

缺少`scope`的旧输入继续使用合法数值；缺少`evaluation`的旧显示输入保留原值。计算与兼容取舍见[证据案例](../docs/case-studies/evidence-aware-scoring.md)。

## 一致性检查

~~~sh
python3 scripts/run-demo.py --check
~~~

该命令重新计算并比较JSON，不写文件，同时执行JavaScript显示转换。完整测试命令见[验证记录](../docs/validation.md)；内容检查另需Git读取文件索引。
