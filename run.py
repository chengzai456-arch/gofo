"""
考勤排班 Web — 启动脚本
自动找到 managed Python，启动 uvicorn
"""
import sys
import os
import subprocess

# managed Python 路径
PYTHON = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
VENV  = r"C:\Users\Administrator\.workbuddy\binaries\python\envs\default"

# 将 venv site-packages 加到 PYTHONPATH，使 pandas/openpyxl 等可被找到
VENV_SITE = os.path.join(VENV, "Lib", "site-packages")
env = os.environ.copy()
env["PYTHONPATH"] = VENV_SITE + ";" + env.get("PYTHONPATH", "")
env["PYTHONIOENCODING"] = "utf-8"

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")
reload_flag = "--reload" if os.getenv("ENV", "dev") == "dev" else ""

cmd = [
    PYTHON, "-m", "uvicorn",
    "main:app",
    "--host", host,
    "--port", port,
    "--workers", "1",
]
if reload_flag:
    cmd.append("--reload")

print(f"启动命令: {' '.join(cmd)}")
print(f"访问地址: http://localhost:{port}")
print(f"API 文档: http://localhost:{port}/docs")
print("-" * 50)

subprocess.run(cmd, env=env)
