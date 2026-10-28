# 测试与覆盖范围

## 运行检查

需要Python 3.10+、Node.js 22+和Git。从仓库根目录运行：

~~~sh
python3 -m unittest discover -s examples/evidence-scoring -p 'test_*.py' -v
node --test examples/report-display/*.test.mjs
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/run-demo.py --check
python3 scripts/check-showcase.py
~~~

2026-10-28验证结果：**38项行为测试通过，零失败、零跳过**。

| 测试组 | 数量 | 覆盖内容 |
| --- | ---: | --- |
| Python聚合与输入转换 | 11 | 证据范围、零值、有效权重、旧字段、非法输入和溢出 |
| JavaScript显示与终端入口 | 10 | 四种显示状态、旧值兼容、输入校验及实际CLI输出 |
| 内容检查器 | 17 | 素材哈希与来源、引用、敏感文件、Git索引及本机文件排除 |

`run-demo.py --check`验证结果JSON可由输入逐字节重建，且不写文件；`check-showcase.py`核对7项素材与本地引用。CI使用Python 3.12和Node.js 22，[已完成的运行记录](https://github.com/TaoW265/classroom-video-insights/actions/runs/40673280654)。

## 媒体检查

截图已逐张查看。28秒录屏通过完整解码、浏览器播放和中段、末尾定位检查；编码为H.264/yuv420p、1920×1080、15fps，仅含视频流。

媒体来源、SHA256和编辑参数见[素材清单](../assets/media-manifest.json)。内容扫描与画面复核的边界见[适用范围](limitations.md)。

## 平台历史验收

2026-10-12的维护迁移记录与上面的示例测试分开统计：

| 模块 | 结果 | 来源提交 |
| --- | --- | --- |
| 后端与分析包 | 751通过、1跳过 | `6493fa589f8172ecbbaf964ade1d5538e780aa1e` |
| Step1 | 41通过 | `821d8e9e7bfe4ae70ed748eccdd53347d3ab0ba7` |
| 前端 | 85通过、构建成功 | `b8a93044d262c11bfc4cceb00831a3c3e72c8bec` |
| 模型选择适配 | 8通过 | 同次维护记录 |

迁移检查另包含68条任务状态、已登记报告哈希与三个结果接口。部署记录为`76f82a4a856ec20001d608070007582b51380a0d`。这些记录描述当时的回归与迁移范围，不能据此推导全部课堂或当前部署的稳定性。[性能计时口径](performance.md)
