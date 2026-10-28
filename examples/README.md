# 独立可运行示例

这些代码独立编写，使用合成数据演示“证据范围影响计算与显示”。Python3.10+、Node.js22+，仅用标准库；不需要安装依赖、密钥或模型服务。

从仓库根目录运行：

```sh
python3 scripts/run-demo.py
```

命令读取[合成输入](../samples/report/signals.synthetic.json)，复用[Python聚合函数](evidence-scoring/scoring.py)，生成[结果JSON](../samples/report/report.sample.json)，再通过[终端入口](report-display/print-report.mjs)调用[显示函数](report-display/score-view.mjs)。预期结果：

| 场景 | JSON的score / evaluation | 终端显示 |
| --- | --- | --- |
| 正常可评价 | `85 / available` | 85 |
| 缺少证据 | `null / unavailable` | 待确认 |
| 部分可评价 | `80 / partial` | 80，并说明可评价范围 |
| 可靠零值 | `0 / available` | 0 |

也可单独核对JavaScript显示端：

```sh
node examples/report-display/print-report.mjs samples/report/report.sample.json
```

转换规则很小：输入章的`signals`送入`aggregate`；结果的`score`、`evaluation`原样交给`scoreView`。`included`、`excluded`和`effective_weights`保留计算依据。`id`、`title`、`narrative`不参与评分。缺少证据不补分，部分可评价按保留权重重新归一化；这里的80只代表保留的一项。

兼容规则保持原行为：旧输入没有`scope`时，不会自动变成不可用；旧显示输入没有`evaluation`时，合法数值仍显示。它们是兼容约定，不代表已重新认证旧数据。显示函数仍可接受只有`score`、`evaluation`的输入，不要求聚合审计字段。

生成与显示仅需Python和Node；仓库交付检查另用Git核对暂存索引。

```sh
python3 -m unittest discover -s examples/evidence-scoring -p 'test_*.py' -v
node --test examples/report-display/*.test.mjs
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/run-demo.py --check
python3 scripts/check-showcase.py
```

`--check`重新计算并检查JSON是否与输入一致，不写文件，同时运行JavaScript显示端。测试数与实际执行结果见[验证记录](../docs/validation.md)。

实际前端通过[截图](../assets/screenshots/README.md)与[录屏](../assets/demo/README.md)展示，公开示例不另建界面，也不生成素材中的课堂报告。示例没有生产量表、完整评级、课堂角色识别或任务服务；`scope`是合成输入中明确给出的条件。代码通过不能推导出完整平台或教学评价准确性通过。
