# 考勤排班数据分析工具

一键分析考勤 Excel 数据，自动生成交互式 HTML 报告。

## 快速开始

### Windows

1. 下载全部文件到同一个文件夹
2. 将考勤 Excel 文件放入该文件夹
3. 双击 `run.bat` → 输入工作目录 → 回车

### macOS

1. 下载全部文件到同一个文件夹
2. 打开终端，给脚本执行权限：
   ```bash
   cd ~/Downloads/考勤工具/
   chmod +x run.command
   ```
3. 将考勤 Excel 文件放入该文件夹
4. 双击 `run.command` → 输入工作目录 → 回车

## 需要的文件

放到同一个文件夹中：

| 文件 | 说明 |
|------|------|
| `attendance_pipeline.py` | 主程序 |
| `run.bat` | Windows 启动脚本 |
| `run.command` | macOS 启动脚本 |
| `requirements.txt` | Python 依赖 |

## 需要的 Excel 文件

| 文件名 | 是否必填 | 说明 |
|--------|:---:|------|
| 原始数据.xlsx | ✅ | 考勤主数据 |
| 离职流程.xlsx | ❌ | 离职审批数据 |
| 花名册 (N).xlsx | ❌ | 员工花名册 |
| 班次.xlsx | ❌ | 班次字典 |
| 补签管理.xlsx | ❌ | 补签记录 |
| 美区签字报表 (2).xlsx | ❌ | 本周签字报表 |
| 美区签字报表 (1).xlsx | ❌ | 上周签字报表 |
| 美区签字报表.xlsx | ❌ | 双周签字报表 |

## 命令行高级用法

```bash
# 完整流程
python attendance_pipeline.py all --workspace ./data --roster-index 15

# 含同比对比
python attendance_pipeline.py all-with-compare --workspace ./data --prev-workspace ./data_yesterday

# 单独步骤
python attendance_pipeline.py clean --workspace ./data --roster-index 15
python attendance_pipeline.py metrics --workspace ./data
python attendance_pipeline.py render --workspace ./data

# 快速报告 (已有指标数据时)
python attendance_pipeline.py quick-report --workspace ./data
```

## 在线版

如果不想安装 Python，可以使用浏览器版：
https://chengzai456-arch.github.io/gofo/
