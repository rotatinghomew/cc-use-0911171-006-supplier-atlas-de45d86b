# supplier-atlas

供应商观察窗画像、混合车次质量记录和经营跟进策略。

## 当前产品

这是可独立运行的本地分析应用，提供业务记录核对和确定性基线结果。各业务职责可直接作为 Python 接口调用，`app.py` 负责组合一次只读业务检查。结果可保存为 JSON，不依赖远端服务。

- `profiles.py`：有观察窗的供应商画像。
- `segments.py`：有效组身份和成员关系。
- `strategies.py`：经营策略绑定及执行清单。

## 运行

使用 Python 3.11.14，无需安装第三方包。

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
python3 app.py demo
```

`inspect` 与 `demo` 使用相同业务入口；`--as-of` 选择已知日期，`--data` 可选本地数据文件，`--output` 可将本次业务核对结果写入文件。默认数据位于 `fixtures/data.json`，默认日期为 `2026-10-31`。这些命令仅展示当前已经存在的能力。

## 容器

`Dockerfile` 固定到 Python 基础镜像内容摘要。构建后运行不联网：

```bash
docker build -t supplier-atlas:local .
docker run --rm --network none supplier-atlas:local python -m unittest discover -s tests -v
docker run --rm --network none supplier-atlas:local
```

## 数据与业务契约

样例记录全部为本地合成数据，不代表真实农户、市场成交或实际试验结果。日期采用 `YYYY-MM-DD`，有记录时点的条目以 `recorded_at` 表示系统已知日期；同一业务键存在多个修订时选已知范围内最新记录，同日由 `revision` 区分，`withdrawn` 表示撤回。可修改样例验证业务边界，不能将演示数据的统计方向视为真实结论。

画像窗口按交付业务日期筛选且受recorded_at约束。空观察的比率为null而不是0。当前分组为公开固定规则，data_group和人工group分开返回。经营策略以业务group为键，派发保留画像与分组版本标识；尚无数据聚类候选、审批与发布。 mixed_loads只记录拼车来源重量及整车抽检结果，不表示每位供应商分别有相同异常率。individual deliveries是此前可直接观察的历史交付，不等于新拼车批次的独立质量真值。mixed_exposure不进行责任分摊。

接口细节见 `docs/contracts.md`。测试使用各自的内存副本和临时目录，不修改原始数据或依赖固定端口。
