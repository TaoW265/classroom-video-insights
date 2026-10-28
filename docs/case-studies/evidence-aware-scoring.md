# 案例：证据与评分一致性

## 问题背景

课堂记录可能只支持一部分评价。学生侧记录缺失，并不说明学生没有参与；教师侧证据可用，也不代表学生侧指标可以随之评价。若接口只传一个数值，使用者无法区分可靠观测、缺失记录和兼容旧协议保留的数值。

本案例用独立编写的简化示例说明这项判断。它没有生产完整量表、角色识别、评级体系或交付协议；所有输入均为合成信号。

## 错误表现

假设教师侧信号为 80 分、权重 1，学生侧信号为 20 分、权重 3，但学生证据已明确不可用。直接计算会得到 `(80×1 + 20×3) ÷ 4 = 35`。这把证据不足误写成了课堂表现差。

另一个相反的错误是用“分数等于 0”判断缺失。可靠证据支持的零值有意义，应参与加权并显示为 0。把所有低值或兼容占位值统一隐藏，同样会丢失有效结果。

## 原因

问题在于把三件事混在一起：信号的数值、证据是否可用于本项评价、结果如何展示。数值非空不能证明证据可用；数据来自旧结构也不能证明它不可用。

## 处理方式

Python [aggregate](../../examples/evidence-scoring/scoring.py)逐项读取 `score`、`weight` 和可选 `scope`：

- `scope="unavailable"`：该项退出加权，有效权重记为 0，保留排除原因。
- `score=null`：作为数值缺失退出加权，不补成 0 或 50。
- 其余合法数值：按原权重参与，包括 0；`directional` 在这个简化示例中仍可参与，不自动等同于不可用。

对保留下来的集合计算 `Σ(score×weight) ÷ Σ(weight)`。没有纳入项时分数为 `null`、`evaluation="unavailable"`；部分纳入时为 `partial`；全部纳入时为 `available`。`included`、`excluded` 和 `effective_weights` 与分数一起输出，便于核对分母。

JavaScript [scoreView](../../examples/report-display/score-view.mjs)消费 `score` 与 `evaluation`：不可评价显示“待确认”，比较值为 `null`；部分可评价保留分数并加范围说明；可靠零值显示“0”。终端显示脚本不从分数高低反推评价状态。

## 输入与输出

下表对应 [合成输入](../../samples/report/signals.synthetic.json)，运行 `python3 scripts/run-demo.py` 可重建[结果JSON](../../samples/report/report.sample.json)，并调用JavaScript显示函数输出四种状态。

| 场景 | 合成信号 | 计算输出 | 展示 |
| --- | --- | --- | --- |
| 正常可评价 | 80、90；各权重 1，均 `standard` | `85 / available` | 85，两项均纳入 |
| 缺少证据 | 50，`unavailable`；另一项为 `null` | `null / unavailable` | 待确认，两项均排除 |
| 部分可评价 | 教师 80，权重 1；学生 20，权重 3 且 `unavailable` | `80 / partial` | 80，说明仅基于可评价内容 |
| 可靠零值 | 0，权重 1，`standard` | `0 / available` | 0，参与加权与展示 |

部分场景的有效权重从 `{teacher:1, student:3}` 变成 `{teacher:1, student:0}`，分母由 4 变成 1。这里只有 1/2 个合成信号可评价；这个比例不是课堂覆盖率、学生人数覆盖率，也不是分数置信度。

缺少证据场景中的 50 用来说明“有数值但不可评价”：它不会成为本次输出分数。可靠零值场景中的 0 则有明确的可用证据标记，会被保留。相同的数值可以有不同含义，判断必须来自元数据。

## 旧数据兼容

旧信号缺少 `scope` 时，聚合函数保留原合法数值参与计算，不自动将它判为不可用。旧展示输入缺少 `evaluation` 时，`scoreView(50)` 仍显示 50；显式 `unavailable` 才隐藏兼容数值。该策略维持旧调用行为，不能被理解为重新认证了旧证据。

聚合输出保留显示函数使用的章节 `score`、`evaluation` 字段，额外附上纳入和排除记录。因此两个既有示例用一个最小转换衔接，不需要模拟生产交付 JSON。完整的转换说明见[示例文档](../../examples/README.md)。

## 测试与复现

~~~sh
python3 scripts/run-demo.py
python3 -m unittest discover -s examples/evidence-scoring -p 'test_*.py' -v
node --test examples/report-display/*.test.mjs
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/run-demo.py --check
python3 scripts/check-showcase.py
~~~

行为测试检查不可用学生信号不拉低教师侧结果、可靠零值继续计分、旧元数据兼容、无有效信号、有效权重、非法输入及溢出拒绝；展示测试检查待确认、部分说明、零值和旧值。生成一致性检查确认提交的 JSON可由同一合成输入重建，JavaScript显示结果与JSON一致。实际执行结果见[验证记录](../validation.md)，不与原系统历史测试数合并。

## 取舍

示例优先说明“哪些证据参与计算”，没有增加新的评级模型。它信任输入提供的证据范围，不负责从音视频自动判定 `scope`。`directional` 不会降低数值权重；需要置信度校准的场景必须另行设计和验证。

部分可评价的 80 只描述剩余信号，不宜与覆盖范围不同的结果直接排序。旧数据兼容保留行为，也保留了元数据不足的限制。通过这些测试只能证明简化规则与展示一致，不能证明真实课堂评价准确、学生角色识别改善或完整生产系统已经通过验收。
