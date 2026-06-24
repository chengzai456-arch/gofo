# gofo-attendance — 考勤数据处理工具

> 一键处理考勤 Excel 数据：清洗 → 指标计算 → 透视分析

[![GitHub](https://img.shields.io/badge/GitHub-chengzai456--arch%2Fgofo-blue)](https://github.com/chengzai456-arch/gofo)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB)](https://www.python.org/)

---

## 下载 .exe（无需安装 Python）

> 下载 `gofo-attendance.exe`，放到 Excel 文件所在目录，双击运行即可。

📥 **[最新 Release](https://github.com/chengzai456-arch/gofo/releases)** — 找到 `gofo-attendance.exe` 下载

---

## 安装

### 方式一：pip 安装（推荐）

```bash
pip install git+https://github.com/chengzai456-arch/gofo.git
```

安装后在终端直接输入 `gofo` 即可使用。

### 方式二：克隆本地安装

```bash
git clone https://github.com/chengzai456-arch/gofo.git
cd gofo
pip install -e .
gofo
```

### 方式三：下载 .exe（无需 Python）

从 [GitHub Releases](https://github.com/chengzai456-arch/gofo/releases) 下载 `gofo-attendance.exe`，放到 Excel 文件所在目录，双击即可运行。

### 方式四：直接运行（不安装）

```bash
git clone https://github.com/chengzai456-arch/gofo.git
cd gofo
pip install pandas numpy openpyxl
python cli.py
```

---

## 使用方法

### 最简模式

把所有 Excel 文件放到当前目录，直接运行：

```bash
gofo
```

### 指定目录

```bash
gofo --input ./6月考勤数据 --output ./结果
```

### 完整参数

```bash
gofo \
  --raw "原始考勤数据.xlsx" \
  --leave "离职流程.xlsx" \
  --roster "花名册 ({n}).xlsx" \
  --shift "班次.xlsx" \
  --resign "补签管理.xlsx" \
  --sign-this "美区签字报表.xlsx" \
  --sign-last "美区签字报表 (1).xlsx" \
  --sign-biweek "美区签字报表 (2).xlsx" \
  --roster-index 12 \
  --output ./result
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入文件目录 | `.` (当前目录) |
| `-o, --output` | 输出目录 | `./output` |
| `--roster-index` | 花名册 Sheet 序号 | `12` |
| `--raw` | 原始考勤数据 | `原始数据.xlsx` |
| `--leave` | 离职流程 | `离职流程.xlsx` |
| `--roster` | 花名册模板 | `花名册 ({n}).xlsx` |
| `--shift` | 班次 | `班次.xlsx` |
| `--resign` | 补签管理 | `补签管理.xlsx` |
| `--gus` | GUS白名单 | `GUS白名单.xlsx` |
| `--sign-this` | 美区签字(本周) | `美区签字报表.xlsx` |
| `--sign-last` | 美区签字(上周) | `美区签字报表 (1).xlsx` |
| `--sign-biweek` | 美区签字(双周) | `美区签字报表 (2).xlsx` |
| `--skip-check` | 跳过文件检查 | (调试用) |

---

## 输出产物

| 文件 | 说明 |
|------|------|
| `清洗后数据.xlsx` | 步骤1：清洗后数据 |
| `指标计算后数据.xlsx` | **核心产物**：含 HUB标记、排班正确性、缺卡、超8H 等指标 |
| `透视分析.xlsx` | 步骤3：多维度透视分析 |

---

## Web 版（可选）

项目还包含一个 Web 版本，在浏览器中操作：

```bash
pip install -e ".[web]"
python run.py
# 访问 http://localhost:8000
```

---

## 构建 .exe

```bash
pip install pyinstaller
python build_exe.py
# 输出: dist/gofo-attendance.exe
```

推送 `v*` 标签后，GitHub Actions 会自动构建并发布 .exe：

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 许可

MIT License
