# 考勤排班数据分析工具

基于现有 `attendance-pipeline` skill 的 Python 数据处理逻辑，提供 **CLI 离线脚本** 和 **Web 服务** 两种使用方式。

---

## 项目结构

```
attendance-web/
├── cli.py               # 离线 CLI 脚本（推荐日常使用）
├── main.py              # FastAPI Web 后端
├── config.py            # 路径配置
├── pipeline/            # 数据处理核心模块（自包含）
│   ├── steps/
│   │   ├── clean_data.py       # 步骤1：数据清洗
│   │   ├── add_metrics.py      # 步骤2：指标计算
│   │   ├── pivot_analysis.py   # 步骤3：透视分析
│   │   └── ...
│   └── utils.py
├── static/
│   └── index.html       # Web 前端页面
├── requirements.txt
├── run.py               # Web 服务启动脚本
├── Dockerfile
└── README.md
```

---

## 方式一：离线 CLI（推荐）

适合日常使用，无需启动 Web 服务，直接命令行运行即可输出 Excel 结果。

### 最简用法

把所有 `.xlsx` 源文件放在当前目录下，直接运行：

```bash
python cli.py
```

输出文件在 `./output/` 目录：
- `清洗后数据.xlsx`
- `指标计算后数据.xlsx` ← 核心产物
- `透视分析.xlsx`

### 指定输入/输出目录

```bash
# 源文件放在 input/ 目录
python cli.py --input ./input --output ./result
```

### 命令行指定每个文件

```bash
python cli.py \
  --raw "原始数据.xlsx" \
  --leave "离职流程.xlsx" \
  --roster "花名册 (12).xlsx" \
  --shift "班次.xlsx" \
  --resign "补签管理.xlsx" \
  --gus "GUS白名单.xlsx" \
  --sign-this "美区签字报表.xlsx" \
  --sign-last "美区签字报表 (1).xlsx" \
  --sign-biweek "美区签字报表 (2).xlsx" \
  --output ./result
```

### 完整参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input`, `-i` | `.` (当前目录) | 输入文件目录 |
| `--output`, `-o` | `./output` | 输出目录 |
| `--roster-index` | `12` | 花名册 Sheet 序号 |
| `--raw` | — | 原始考勤数据路径 |
| `--leave` | — | 离职流程路径 |
| `--roster` | — | 花名册路径（支持 `{n}` 占位符） |
| `--shift` | — | 班次路径 |
| `--resign` | — | 补签管理路径 |
| `--gus` | — | GUS白名单路径 |
| `--sign-this` | — | 美区签字报表(本周)路径 |
| `--sign-last` | — | 美区签字报表(上周)路径 |
| `--sign-biweek` | — | 美区签字报表(双周)路径 |
| `--skip-check` | `false` | 跳过文件存在检查 |

---

## 方式二：Web 服务

适合团队多人在线使用，通过浏览器上传文件。

### 启动

```bash
python run.py
# 访问 http://localhost:8000
```

### API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/` | 前端页面 |
| POST | `/api/process` | 上传 9 个文件，同步处理 |
| GET  | `/api/download/{id}/{name}` | 下载结果文件 |
| GET  | `/health` | 健康检查 |

---

## 安装依赖

```bash
pip install -r requirements.txt
```

---

## 部署

### Docker

```bash
docker build -t attendance-web .
docker run -p 8000:8000 attendance-web
```

---

## 数据处理流程

```
源文件(9个) → [步骤1] 清洗 → [步骤2] 指标计算 → [步骤3] 透视分析 → 输出 Excel
```

详见 `考勤数据处理逻辑说明.md`。

---

## 注意事项

- 项目已自包含，不再依赖外部 skill 目录
- 处理数千行数据通常 1~3 分钟
- GUS白名单可选，不存在时自动跳过
- 花名册模板使用 `{n}` 替换序号
