# 证据与评分一致性

## 问题

学生侧记录缺失不等于学生没有参与。若教师侧为80分、权重1，学生侧为20分、权重3，但学生证据不可用，直接计算会得到：

~~~text
(80 × 1 + 20 × 3) ÷ 4 = 35
~~~

这个结果把证据不足解释成了表现较差。反过来，若将所有零值视为缺失，又会丢掉可靠观测。

## 原因

数值、证据范围和显示状态需要分别表达。分数非空不能证明证据可用，分数为0也不能证明记录缺失。

## 处理

[aggregate](../../examples/evidence-scoring/scoring.py)先校验数值与权重，再逐项决定是否计分：

- `scope="unavailable"`或`score=null`：有效权重置0，记录排除原因。
- 其他合法数值：按原权重参与，包括0；`directional`不自动变为不可用。
- 以纳入项计算`Σ(score×weight) ÷ Σ(weight)`。全部排除时输出`null / unavailable`，部分纳入时输出`partial`，全部纳入时输出`available`。

上例排除学生侧信号后，有效权重为`{teacher:1, student:0}`，结果为80。它只描述剩余信号，显示时需要说明评价范围。

[scoreView](../../examples/report-display/score-view.mjs)同时读取分数和`evaluation`：不可评价显示“待确认”、比较取值为`null`；部分可评价保留分数并附范围说明；可靠零值继续显示0。

### 合成测试输入与输出

| 场景 | 输入 | 聚合结果 | 显示 |
| --- | --- | --- | --- |
| 正常可评价 | 80、90，各权重1，均为`standard` | `85 / available` | 85 |
| 缺少证据 | 50但`unavailable`，另一项为`null` | `null / unavailable` | 待确认 |
| 部分可评价 | 教师80、权重1；学生20、权重3但`unavailable` | `80 / partial` | 80，附范围说明 |
| 可靠零值 | 0、权重1、`standard` | `0 / available` | 0 |

[输入数据](../../samples/report/signals.synthetic.json)与[结果JSON](../../samples/report/report.sample.json)保留`included`、`excluded`和`effective_weights`，可核对分母和排除项。

### 旧数据兼容

缺少`scope`的旧信号按合法数值继续计分；缺少`evaluation`的旧显示输入保留原数值，例如`scoreView(50)`仍显示50。只有显式`unavailable`才隐藏兼容数值，不按分数高低猜测证据范围。

## 验证

~~~sh
python3 scripts/run-demo.py
python3 scripts/run-demo.py --check
~~~

行为测试覆盖不可用信号退出计分、可靠零值、有效分母、旧字段兼容、非法输入与溢出，以及JSON到实际显示函数的转换。完整命令见[测试与覆盖范围](../validation.md)。

部分可评价分数不宜与覆盖范围不同的分数直接排序；信号项数也不等于课堂覆盖率。证据可靠性与置信度校准的边界见[适用范围](../limitations.md)。
