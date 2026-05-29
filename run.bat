@echo off
chcp 65001 >nul
title 考勤排班数据分析工具
echo ========================================
echo   考勤排班数据分析工具 v1.0
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查/安装依赖
echo [1/3] 检查依赖...
pip show pandas >nul 2>&1 && pip show openpyxl >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] 安装依赖包 (pandas, numpy, openpyxl)...
    pip install pandas numpy openpyxl -q
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请手动执行: pip install pandas numpy openpyxl
        pause
        exit /b 1
    )
) else (
    echo [2/3] 依赖已就绪
)

:: 运行
echo [3/3] 启动分析...
echo.
echo 用法: 将 Excel 文件放在当前目录下
echo       然后拖入工作目录路径，或直接回车使用当前目录
echo.
set /p WORKSPACE="请输入工作目录 (直接回车=当前目录): "
if "%WORKSPACE%"=="" set WORKSPACE=%cd%

set /p ROSTER="花名册序号 (直接回车=12): "
if "%ROSTER%"=="" set ROSTER=12

echo.
echo 工作目录: %WORKSPACE%
echo 花名册序号: %ROSTER%
echo.
echo 按任意键开始分析...
pause >nul

python "%~dp0attendance_pipeline.py" all --workspace "%WORKSPACE%" --roster-index %ROSTER%

echo.
echo ========================================
echo   分析完成!
echo   报告已保存到工作目录
echo ========================================
pause
