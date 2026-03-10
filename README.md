# math_enthusiast

## 考拉兹猜想（冰雹猜想）前 10000 位导出 Excel

生成 1–10000 的考拉兹（Collatz）计算轨迹，并导出到 Excel。

Excel 三列含义：

- **第 1 列**：数字（默认 1–10000）
- **第 2 列**：中间计算结果（例如 `1->4->2->1`），**一旦出现循环（数值重复）就结束**（重复的那个值也会写入结尾）
- **第 3 列**：操作串，`e` 表示“除以 2”，`m` 表示“乘以 3 加 1”（例如 `1->4->2->1` 对应 `mee`）

### 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

### 运行（默认 1–10000）

```bash
python3 collatz_to_excel.py
```

输出文件默认是 `collatz_1_10000.xlsx`。

### 自定义范围与输出文件名

```bash
python3 collatz_to_excel.py --start 1 --end 5000 --out collatz_1_5000.xlsx
```

