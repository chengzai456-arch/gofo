"""
CLI 便利脚本 —— 绕过 pip install，直接 python cli.py 运行。

项目已重组为 pip 可安装包。推荐安装方式:

    pip install -e .          # 开发模式安装，之后用 'gofo' 命令
    gofo --input ./data --output ./result

如果不想安装，也可以用本脚本:
    python cli.py --input ./data --output ./result

本脚本只是 gofo_attendance.cli:main 的薄包装。
"""
import sys, os

# 确保 gofo_attendance 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gofo_attendance.cli import main

if __name__ == "__main__":
    main()
