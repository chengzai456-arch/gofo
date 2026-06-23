# 考勤排班数据分析 Web 版

基于现有 `attendance-pipeline` skill 的 Python 数据处理逻辑，封装为 Web 服务。用户通过浏览器上传 9 个 Excel 原始文件，后端异步执行完整处理流程（清洗 → 指标计算 → 透视分析），处理完成后提供结果文件下载。

---

## 功能特性

- **一键上传**：单页表单上传全部 9 个原始 Excel 文件，支持拖拽
- **异步处理**：提交后立即返回任务 ID，后端后台顺序执行，前端轮询进度
- **实时进度**：处理日志实时展示（清洗中 / 指标计算中 / 透视分析中）
- **产物下载**：处理完成后展示 3 个结果文件下载链接
- **并发隔离**：每个请求独立 UUID 临时目录，互不干扰
- **安全防护**：文件大小限制（50MB）、路径遍历防护、文件类型限制（.xlsx）

---

## 项目结构

```
attendance-web/
├── main.py              # FastAPI 后端（接口 + pipeline 封装）
├── requirements.txt     # Python 依赖
├── static/
│   └── index.html     # 前端页面（单页，含 CSS + JS）
├── temp/                 # 运行时临时目录（自动创建，按需清理）
├── run.py               # 启动脚本
├── Dockerfile           # 容器化部署
└── README.md            # 本文件
```

---

## 快速启动

### 环境要求

- Python 3.10+
- 依赖：见 `requirements.txt`
- 现有 `attendance-pipeline` skill（pipeline 模块从这个 skill 目录导入）

### 安装依赖

```bash
# 使用 managed Python
PYTHON="C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
PIP="$PYTHON -m pip"

$PIP install -r requirements.txt
```

### 启动服务

```bash
python run.py
# 或直接使用 uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问 `http://localhost:8000`。

---

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/` | 前端页面 |
| POST | `/api/tasks` | 创建处理任务（上传 9 个文件） |
| GET  | `/api/tasks/{task_id}` | 查询任务状态 + 进度日志 |
| GET  | `/api/download/{task_id}/{filename}` | 下载结果文件 |
| POST | `/api/cleanup/{task_id}` | 手动清理任务临时目录 |
| GET  | `/health` | 健康检查 |

### 创建任务 POST `/api/tasks`

**请求**：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `roster_index` | int |  | 花名册文件名序号，默认 12 |
| `raw_file` | file | ✅ | 原始考勤数据.xlsx |
| `leave_file` | file | ✅ | 离职流程.xlsx |
| `roster_file` | file | ✅ | 花名册.xlsx |
| `shift_file` | file | ✅ | 班次.xlsx |
| `resign_file` | file | ✅ | 补签管理.xlsx |
| `gus_whitelist` | file | ✅ | GUS白名单.xlsx |
| `sign_this` | file | ✅ | 美区签字报表.xlsx（本周） |
| `sign_last` | file | ✅ | 美区签字报表(1).xlsx（上周） |
| `sign_biweek` | file | ✅ | 美区签字报表(2).xlsx（双周） |

**响应**：

```json
{
  "task_id": "a3f8c1d2",
  "status": "processing",
  "message": "任务已创建，正在处理中"
}
```

### 查询状态 GET `/api/tasks/{task_id}`

**响应**：

```json
{
  "task_id": "a3f8c1d2",
  "status": "done",
  "log": ["[1/3] 数据清洗中...", "  ✓ 清洗完成 → 清洗后数据.xlsx", "..."],
  "products": {
    "清洗后数据.xlsx": "/api/download/a3f8c1d2/清洗后数据.xlsx",
    "指标计算后数据.xlsx": "/api/download/a3f8c1d2/指标计算后数据.xlsx",
    "透视分析.xlsx": "/api/download/a3f8c1d2/透视分析.xlsx"
  },
  "error": ""
}
```

`status` 枚举：`processing` / `done` / `error`

---

## 部署

### 开发环境

```bash
python run.py
```

### 生产环境（uvicorn + nginx）

```bash
# 安装 gunicorn（Windows 下用 uvicorn workers）
pip install gunicorn

# 启动（4 workers）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

nginx 反向代理配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker 部署

```bash
docker build -t attendance-web .
docker run -p 8000:8000 -v ./temp:/app/temp attendance-web
```

---

## 注意事项

1. **skill 路径**：`main.py` 中 `SKILL_DIR` 指向 `attendance-pipeline` skill 目录，部署时如需修改请更新该变量
2. **临时目录清理**：任务完成后建议调用 `/api/cleanup/{task_id}` 清理；也可配置定时任务清理超过 24h 的临时目录
3. **并发限制**：当前任务状态存储在内存（`tasks` 字典），重启后丢失；生产环境建议换 Redis
4. **文件大小**：单个上传文件限制 50MB，可在 `main.py` 中修改 `MAX_FILE_BYTES`
5. **进程模型**：pipeline 为 CPU 密集型（pandas），建议生产环境使用多 worker，每个 worker 独立处理请求

---

## 扩展方向

- **步骤4-5（HTML 报告 + 同比注入）**：在 `_run_pipeline()` 中补充 `run_report_data` / `run_render` / `run_comparison` / `run_inject` 调用
- **步骤6（SSO 权限守卫）**：对下载接口增加 JWT 鉴权
- **Celery 异步任务**：大数据量时换用 Celery + Redis，支持任务队列和进度推送
- **邮件通知**：处理完成后自动发送邮件通知（含下载链接）
