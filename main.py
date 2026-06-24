# ============================================================
# 考勤数据处理 Web 版 —— FastAPI 后端
# 基于 attendance-pipeline skill 封装
# ============================================================
import sys, os, shutil, uuid, json, time
from pathlib import Path
from typing import List

# =========================================================
# 路径初始化：项目自包含，pipeline/config 都在本目录下
# =========================================================
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# 本地 venv site-packages（仅本地开发时需要，云端通过 pip install 解决）
_LOCAL_VENV = BASE_DIR / ".venv" / "Lib" / "site-packages"
if _LOCAL_VENV.exists():
    sys.path.insert(0, str(_LOCAL_VENV))

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import config as pipeline_config
from pipeline.steps.clean_data    import run as run_clean
from pipeline.steps.add_metrics    import run as run_metrics
from pipeline.steps.pivot_analysis import run as run_pivot

from fastapi                import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses      import FileResponse
from fastapi.staticfiles     import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 常量
# ============================================================
MAX_FILE_BYTES  = 50 * 1024 * 1024   # 单文件最大 50MB
TEMP_ROOT       = BASE_DIR / "temp"
TEMP_ROOT.mkdir(exist_ok=True)

# 上传字段名 → 保存时的文件名
FILE_SAVE_NAMES = {
    "raw_file":      "原始考勤数据.xlsx",
    "leave_file":    "离职流程.xlsx",
    "roster_file":   "花名册 (12).xlsx",
    "shift_file":    "班次.xlsx",
    "resign_file":   "补签管理.xlsx",
    "gus_whitelist": "GUS白名单.xlsx",
    "sign_this":     "美区签字报表.xlsx",
    "sign_last":     "美区签字报表 (1).xlsx",
    "sign_biweek":   "美区签字报表 (2).xlsx",
}

# 输出产物列表
OUTPUT_FILES = [
    "清洗后数据.xlsx",
    "指标计算后数据.xlsx",
    "透视分析.xlsx",
]

# ============================================================
# FastAPI 应用
# ============================================================
app = FastAPI(title="考勤数据处理 Web 版", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件（index.html 在同目录）
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")


# —— 健康检查 ——
@app.get("/health")
def health():
    return {"status": "ok"}


# —— 核心：上传 + 处理（同步） ——
@app.post("/api/process")
async def process_files(
    raw_file:      UploadFile = File(...),
    leave_file:    UploadFile = File(...),
    roster_file:   UploadFile = File(...),
    shift_file:    UploadFile = File(...),
    resign_file:   UploadFile = File(...),
    gus_whitelist: UploadFile = File(...),
    sign_this:     UploadFile = File(...),
    sign_last:     UploadFile = File(...),
    sign_biweek:   UploadFile = File(...),
    roster_index:  int        = Form(12),
):
    task_id  = uuid.uuid4().hex[:8]
    work_dir = TEMP_ROOT / task_id
    work_dir.mkdir(parents=True)

    # ---- 读取所有文件到内存（同时校验格式和大小）----
    upload_keys = [
        ("原始数据",     "raw_file",      raw_file),
        ("离职流程",     "leave_file",    leave_file),
        ("花名册",       "roster_file",   roster_file),
        ("班次",         "shift_file",    shift_file),
        ("补签管理",     "resign_file",   resign_file),
        ("GUS白名单",   "gus_whitelist", gus_whitelist),
        ("美区签字(本周)", "sign_this",     sign_this),
        ("美区签字(上周)", "sign_last",     sign_last),
        ("美区签字(双周)", "sign_biweek",   sign_biweek),
    ]
    file_bytes = {}
    for label, key, uf in upload_keys:
        # 格式校验
        if not uf.filename.endswith(".xlsx"):
            # 清理已创建的目录
            shutil.rmtree(work_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"{label}「{uf.filename}」格式错误，仅支持 .xlsx")
        # 读取内容
        content = await uf.read()
        # 大小校验
        if len(content) > MAX_FILE_BYTES:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f"{label} 文件过大（最大 50MB）")
        file_bytes[key] = content

    # ---- 保存上传文件到工作目录 ----
    for key, content in file_bytes.items():
        dest = work_dir / FILE_SAVE_NAMES[key]
        dest.write_bytes(content)

    # 花名册文件名含序号
    roster_path = work_dir / f"花名册 ({roster_index}).xlsx"
    (work_dir / FILE_SAVE_NAMES["roster_file"]).rename(roster_path)

    # ---- 构造 config 字典（key 名与 pipeline 步骤一致）----
    config = {
        "raw_file":               str(work_dir / "原始考勤数据.xlsx"),
        "leave_file":             str(work_dir / "离职流程.xlsx"),
        "roster_pattern":         str(roster_path),
        "shift_file":             str(work_dir / "班次.xlsx"),
        "resign_file":            str(work_dir / "补签管理.xlsx"),
        "gus_whitelist_file":     str(work_dir / "GUS白名单.xlsx"),
        "sign_report_this_week":  str(work_dir / "美区签字报表.xlsx"),
        "sign_report_last_week":  str(work_dir / "美区签字报表 (1).xlsx"),
        "sign_report_biweek":     str(work_dir / "美区签字报表 (2).xlsx"),
        "cleaned_file":           str(work_dir / "清洗后数据.xlsx"),
        "metrics_file":           str(work_dir / "指标计算后数据.xlsx"),
        "pivot_file":             str(work_dir / "透视分析.xlsx"),
        "workspace":              str(work_dir),
    }

    # ---- 按顺序执行 3 大步骤 ----
    errors = []
    try:
        run_clean(config)
    except Exception as e:
        errors.append(f"步骤1（清洗）失败：{e}")

    if not errors:
        try:
            run_metrics(config)
        except Exception as e:
            errors.append(f"步骤2（指标计算）失败：{e}")

    if not errors:
        try:
            run_pivot(config)
        except Exception as e:
            errors.append(f"步骤3（透视分析）失败：{e}")

    # 收集成功生成的产物
    products = {}
    for fname in OUTPUT_FILES:
        fpath = work_dir / fname
        if fpath.exists():
            products[fname] = f"/api/download/{task_id}/{fname}"

    # 10 分钟后异步清理
    def _cleanup(path: Path):
        time.sleep(600)
        shutil.rmtree(path, ignore_errors=True)
    import threading
    t = threading.Thread(target=_cleanup, args=(work_dir,), daemon=True)
    t.start()

    if errors:
        # 返回部分产物（如果有）+ 错误信息
        return {
            "task_id":  task_id,
            "status":   "error",
            "products": products,
            "error":    "\n".join(errors),
        }

    return {
        "task_id":  task_id,
        "status":   "done",
        "products": products,
        "error":    None,
    }


# —— 下载产物 ——
@app.get("/api/download/{task_id}/{filename}")
def download_file(task_id: str, filename: str):
    # 路径遍历防护
    if ".." in filename or filename.startswith("/") or "/" in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    # 只允许下载已知产物
    if filename not in OUTPUT_FILES:
        raise HTTPException(status_code=400, detail="不支持的文件名")

    file_path = TEMP_ROOT / task_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在，可能已被清理（10分钟有效期）")

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return FileResponse(path=str(file_path), filename=filename, media_type=media_type)


# —— 启动入口 ——
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
