"""
PyInstaller 打包脚本 —— 生成独立 .exe 文件
============================================
运行:
    pip install pyinstaller
    python build_exe.py

输出:
    dist/gofo-attendance.exe    (约 80-150 MB，包含 Python 运行时)
"""
import sys
import os
from pathlib import Path

# ---- 确保在项目根目录 ----
ROOT = Path(__file__).parent
os.chdir(str(ROOT))
sys.path.insert(0, str(ROOT))

# ---- PyInstaller 配置 ----
import PyInstaller.__main__

# 收集 pipeline 子包中的所有 .py 作为 hidden import
pipeline_modules = []
pipeline_dir = ROOT / "gofo_attendance" / "pipeline"
for root, dirs, files in os.walk(pipeline_dir):
    for f in files:
        if f.endswith(".py") and f != "__init__.py":
            rel = os.path.relpath(os.path.join(root, f), ROOT)
            mod = rel.replace(os.sep, ".").replace(".py", "")
            pipeline_modules.append(mod)

hidden_imports = []
for mod in pipeline_modules:
    hidden_imports.extend(["--hidden-import", mod])

print(f"检测到 {len(pipeline_modules)} 个 pipeline 模块")
print(f"开始 PyInstaller 打包...")
print()

PyInstaller.__main__.run([
    "gofo_attendance/cli.py",
    "--name=gofo-attendance",
    "--onefile",
    "--console",
    "--clean",
    "--noconfirm",
    *hidden_imports,
    "--add-data", f"gofo_attendance{os.sep}pipeline{os.pathsep}gofo_attendance{os.sep}pipeline",
])

exe_path = ROOT / "dist" / "gofo-attendance.exe"
if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"\n{'=' * 50}")
    print(f"✅ 打包成功！")
    print(f"   {exe_path}")
    print(f"   文件大小: {size_mb:.1f} MB")
    print(f"{'=' * 50}")
    print(f"\n使用方法:")
    print(f"   把 Excel 文件放到同一目录，双击 gofo-attendance.exe")
    print(f"   或命令行: gofo-attendance.exe --input ./data --output ./result")
else:
    print("❌ 打包失败，请检查上方错误信息")
    sys.exit(1)
