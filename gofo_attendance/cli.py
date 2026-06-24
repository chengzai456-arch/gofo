"""
考勤数据处理 —— CLI 入口
=========================
用法:
    gofo                           # 文件放当前目录，直接运行
    gofo --input ./data --output ./result
    gofo --raw "原始数据.xlsx" --leave "离职.xlsx" ...

输出:
    output/
    ├── 清洗后数据.xlsx
    ├── 指标计算后数据.xlsx    ← 核心产物
    └── 透视分析.xlsx
"""
import sys
import os
import argparse
from pathlib import Path

from .pipeline.steps.clean_data    import run as run_clean
from .pipeline.steps.add_metrics    import run as run_metrics
from .pipeline.steps.pivot_analysis import run as run_pivot


# ============================================================
# 默认文件映射
# ============================================================
DEFAULT_FILES = {
    "raw":           "原始数据.xlsx",
    "leave":         "离职流程.xlsx",
    "roster":        "花名册.xlsx",
    "shift":         "班次.xlsx",
    "resign":        "补签管理.xlsx",
    "gus_whitelist": "GUS白名单.xlsx",
    "sign_this":     "美区签字报表.xlsx",
    "sign_last":     "美区签字报表 (1).xlsx",
    "sign_biweek":   "美区签字报表 (2).xlsx",
}


def build_config(args):
    """根据命令行参数构造 config 字典"""
    work_dir = Path(args.output).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    input_dir = Path(args.input).resolve() if args.input else None

    def resolve(key, cli_arg):
        if cli_arg:
            return cli_arg
        if input_dir:
            return str(input_dir / DEFAULT_FILES[key])
        return str(work_dir / DEFAULT_FILES[key])

    raw_file    = resolve("raw",           args.raw)
    leave_file  = resolve("leave",         args.leave)
    shift_file  = resolve("shift",         args.shift)
    resign_file = resolve("resign",        args.resign)
    gus_file    = resolve("gus_whitelist", args.gus)
    sign_this   = resolve("sign_this",     args.sign_this)
    sign_last   = resolve("sign_last",     args.sign_last)
    sign_biweek = resolve("sign_biweek",   args.sign_biweek)

    roster_pattern = args.roster
    if not roster_pattern:
        base = input_dir if input_dir else work_dir
        roster_pattern = str(base / "花名册 ({n}).xlsx")

    return {
        "raw_file":              raw_file,
        "leave_file":            leave_file,
        "roster_pattern":        roster_pattern,
        "shift_file":            shift_file,
        "resign_file":           resign_file,
        "gus_whitelist_file":    gus_file,
        "sign_report_this_week": sign_this,
        "sign_report_last_week": sign_last,
        "sign_report_biweek":    sign_biweek,
        "cleaned_file":   str(work_dir / "清洗后数据.xlsx"),
        "metrics_file":   str(work_dir / "指标计算后数据.xlsx"),
        "pivot_file":     str(work_dir / "透视分析.xlsx"),
        "workspace":      str(work_dir),
    }


def check_files_exist(config, roster_index=12):
    """检查必需输入文件是否存在"""
    keys = [
        ("原始考勤数据",     "raw_file"),
        ("离职流程",         "leave_file"),
        ("班次",             "shift_file"),
        ("补签管理",         "resign_file"),
        ("美区签字(本周)",    "sign_report_this_week"),
        ("美区签字(上周)",    "sign_report_last_week"),
        ("美区签字(双周)",    "sign_report_biweek"),
    ]
    missing = []
    for label, key in keys:
        path = config.get(key, "")
        if not os.path.exists(path):
            missing.append(f"  - {label}: {path}")

    roster = config["roster_pattern"]
    if "{n}" in roster:
        roster_filled = roster.format(n=roster_index)
        if not os.path.exists(roster_filled):
            missing.append(f"  - 花名册: {roster_filled}")
    elif not os.path.exists(roster):
        missing.append(f"  - 花名册: {roster}")

    gus = config.get("gus_whitelist_file", "")
    if gus and not os.path.exists(gus):
        missing.append(f"  - GUS白名单: {gus} (可选)")

    return missing


def main():
    parser = argparse.ArgumentParser(
        description="考勤数据处理 · 离线工具 (gofo-attendance)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 方式一：文件放在 input/ 目录
  gofo --input ./input --output ./output

  # 方式二：指定每个文件路径
  gofo --raw "原始数据.xlsx" --leave "离职.xlsx" --shift "班次.xlsx" ...

  # 最简：文件放在当前目录
  gofo

默认输出目录: ./output    花名册序号: 12
        """
    )
    parser.add_argument("--input", "-i",    default=".",       help="输入文件目录（默认当前目录）")
    parser.add_argument("--output", "-o",   default="./output", help="输出目录（默认 ./output）")
    parser.add_argument("--roster-index",   type=int, default=12, help="花名册序号（默认 12）")
    parser.add_argument("--raw",             help="原始考勤数据 .xlsx")
    parser.add_argument("--leave",           help="离职流程 .xlsx")
    parser.add_argument("--roster",          help="花名册 .xlsx（模板: 花名册 ({n}).xlsx）")
    parser.add_argument("--shift",           help="班次 .xlsx")
    parser.add_argument("--resign",          help="补签管理 .xlsx")
    parser.add_argument("--gus",             help="GUS白名单 .xlsx（可选）")
    parser.add_argument("--sign-this",       help="美区签字(本周) .xlsx")
    parser.add_argument("--sign-last",       help="美区签字(上周) .xlsx")
    parser.add_argument("--sign-biweek",     help="美区签字(双周) .xlsx")
    parser.add_argument("--skip-check",      action="store_true", help="跳过文件检查（调试用）")

    args = parser.parse_args()

    # 构建 config
    config = build_config(args)

    # 文件检查
    if not args.skip_check:
        missing = check_files_exist(config, roster_index=args.roster_index)
        if missing:
            print("❌ 以下文件未找到：")
            for m in missing:
                print(m)
            print("\n请将文件放到指定位置，或使用命令行参数指定路径。")
            print("运行 gofo --help 查看帮助。")
            sys.exit(1)

    print(f"📂 输出目录: {config['workspace']}")
    print(f"📋 花名册序号: {args.roster_index}\n")

    # ---- 步骤1：数据清洗 ----
    print("=" * 50)
    print("[1/3] 数据清洗中…")
    print("=" * 50)
    try:
        run_clean(config, roster_index=args.roster_index)
        print("✅ 步骤1 完成 → 清洗后数据.xlsx")
    except Exception as e:
        print(f"❌ 步骤1 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ---- 步骤2：指标计算 ----
    print("\n" + "=" * 50)
    print("[2/3] 指标计算中…")
    print("=" * 50)
    try:
        run_metrics(config)
        print("✅ 步骤2 完成 → 指标计算后数据.xlsx")
    except Exception as e:
        print(f"❌ 步骤2 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ---- 步骤3：透视分析 ----
    print("\n" + "=" * 50)
    print("[3/3] 透视分析中…")
    print("=" * 50)
    try:
        run_pivot(config)
        print("✅ 步骤3 完成 → 透视分析.xlsx")
    except Exception as e:
        print(f"❌ 步骤3 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ---- 输出结果 ----
    print("\n" + "=" * 50)
    print("🎉 全部处理完成！")
    print("=" * 50)
    output_files = ["清洗后数据.xlsx", "指标计算后数据.xlsx", "透视分析.xlsx"]
    out_dir = Path(config["workspace"])
    for fname in output_files:
        fpath = out_dir / fname
        if fpath.exists():
            size_mb = fpath.stat().st_size / (1024 * 1024)
            print(f"  📄 {fname}  ({size_mb:.1f} MB)")
        else:
            print(f"  ⚠ {fname}  未生成")

    print(f"\n📂 所有文件已输出到: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
