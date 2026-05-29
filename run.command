#!/bin/bash
# 考勤排班数据分析工具 - macOS/Linux 启动脚本
# 双击 .command 文件即可运行（需先 chmod +x）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  考勤排班数据分析工具 v1.0"
echo "========================================"
echo ""

# 检查 Python3
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[错误] 未找到 Python，请先安装 Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

echo "[1/3] Python: $($PYTHON --version)"

# 检查/安装依赖
echo "[2/3] 检查依赖..."
$PYTHON -c "import pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "       安装依赖包 (pandas, numpy, openpyxl)..."
    $PYTHON -m pip install pandas numpy openpyxl -q
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        echo "请手动执行: $PYTHON -m pip install pandas numpy openpyxl"
        read -p "按回车键退出..."
        exit 1
    fi
else
    echo "       依赖已就绪"
fi

# 询问参数
echo ""
echo "用法: 将 Excel 文件放在当前目录下"
echo "      然后输入工作目录路径，或直接回车使用当前目录"
echo ""
read -p "工作目录 (直接回车=当前目录): " WORKSPACE
WORKSPACE="${WORKSPACE:-$SCRIPT_DIR}"

read -p "花名册序号 (直接回车=12): " ROSTER
ROSTER="${ROSTER:-12}"

echo ""
echo "工作目录: $WORKSPACE"
echo "花名册序号: $ROSTER"
echo ""
read -p "按回车键开始分析..." _

# 执行
$PYTHON "$SCRIPT_DIR/attendance_pipeline.py" all --workspace "$WORKSPACE" --roster-index "$ROSTER"

echo ""
echo "========================================"
echo "  分析完成!"
echo "  报告已保存到工作目录"
echo "========================================"
read -p "按回车键退出..."
