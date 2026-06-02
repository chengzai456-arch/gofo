"""
生成交互式考勤排班数据分析 HTML 报告 v10
输入: report_data.json
输出: 考勤分析报告.html + 考勤首页.html + 各大区独立报告

v10 更新:
  - 新增考勤首页: 仅展示核心KPI + 查看全览入口
  - 首页复用 v9 3D地球 + 宇宙星云背景
"""
import sys, os, json
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Lib\site-packages")

WORKSPACE  = r"D:\Documents\Downloads\0521排班\output"
_workspace = os.environ.get('ATTENDANCE_WORKSPACE')
if _workspace and os.path.isdir(_workspace):
    WORKSPACE = _workspace
DATA_FILE  = os.path.join(WORKSPACE, "report_data.json")
OUTPUT_FILE = os.path.join(WORKSPACE, "考勤分析报告.html")

FEISHU_URL = "https://acnjh1thgeif.feishu.cn/base/RgdCbpNrKaLiGmsBs2TcnTOCnYt?table=tblFwl3mZSW6yEOP&view=vewoYY8F16"

# ============================================================
# 读取数据
# ============================================================
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, ensure_ascii=True)

# ============================================================
# 生成 HTML
# ============================================================
html_template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>考勤管理数据分析报告</title>
<style>
/* ========== Font & Reset ========== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff;
  color: #1a1a2e;
  display: flex; min-height: 100vh; overflow-x: hidden;
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
}
a { text-decoration: none; color: inherit; }

/* ========== Canvas Backgrounds (hidden in white theme) ========== */
#bgCanvas, #starCanvas { display: none; }

/* ========== Sidebar ========== */
.sidebar {
  width: 260px; min-width: 260px;
  background: #f8f9fc;
  border-right: 1px solid #e5e7eb;
  color: #1a1a2e;
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; bottom: 0;
  overflow-y: auto; z-index: 100;
  box-shadow: 2px 0 12px rgba(0,0,0,0.06);
}
.sidebar-header {
  padding: 20px 20px; font-size: 15px; font-weight: 700; letter-spacing: -0.2px;
  border-bottom: 1px solid #e5e7eb;
  display: flex; align-items: center; gap: 10px;
  position: sticky; top: 0;
  background: inherit; z-index: 1; color: #1a1a2e;
}
.sidebar-header .logo {
  width: 34px; height: 34px; border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.sidebar-action {
  padding: 10px 14px; display: flex; justify-content: center;
  border-bottom: 1px solid #e5e7eb;
}
.back-home-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: 100%; padding: 8px 0; border-radius: 10px;
  font-size: 12.5px; font-weight: 600; color: #3b82f6;
  background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.18);
  cursor: pointer; transition: all 0.25s ease; text-decoration: none; white-space: nowrap;
  letter-spacing: 0.5px;
}
.back-home-btn:hover {
  background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.35);
  color: #2563eb; transform: translateY(-1px);
}
.sidebar-nav { flex: 1; padding: 10px 0; }
.nav-item {
  display: flex; align-items: center; padding: 10px 18px; cursor: pointer;
  transition: all 0.2s; font-size: 13.5px; font-weight: 500; user-select: none;
  margin: 1px 8px; border-radius: 8px; color: #4b5563;
}
.nav-item:hover { background: #eef2ff; color: #1a1a2e; }
.nav-item.active { background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); color: #ffffff; font-weight: 600; box-shadow: 0 2px 8px rgba(59,130,246,0.25); }
.nav-item .icon { margin-right: 10px; font-size: 15px; width: 20px; text-align: center; }
.nav-item .badge { margin-left: auto; background: #e5e7eb; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; color: #6b7280; }
.nav-item.active .badge { background: rgba(255,255,255,0.25); color: #fff; }
.nav-item .arrow { margin-left: 6px; font-size: 10px; transition: transform 0.2s; opacity: 0.5; }
.nav-item.expanded .arrow { transform: rotate(90deg); opacity: 0.8; }

/* Status dot for sub-department tabs */
.status-dot { width: 7px; height: 7px; border-radius: 50%; margin-left: 6px; flex-shrink: 0; }
.dot-green { background: #22c55e; }
.dot-yellow { background: #eab308; }
.dot-red { background: #ef4444; }

.sub-nav { display: none; }
.sub-nav.show { display: block; }
.sub-nav .nav-item { padding-left: 42px; font-size: 13px; }

/* ========== Main Content ========== */
.main {
  margin-left: 260px; flex: 1; padding: 28px 32px;
  max-width: calc(100vw - 260px); overflow-x: hidden;
  position: relative; z-index: 1;
}

/* ========== Floating Button ========== */
.floating-btn {
  position: fixed; top: 22px; right: 28px; z-index: 300;
  display: flex; align-items: center; gap: 8px;
  padding: 9px 20px; border-radius: 50px;
  border: 1px solid #d1d5db; cursor: grab;
  font-size: 13px; font-weight: 600; color: #374151; letter-spacing: 0.1px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  user-select: none; touch-action: none;
}
.floating-btn.dragging { cursor: grabbing; opacity: 0.85; transition: none; }
.floating-btn:hover {
  background: #f9fafb; color: #1a1a2e;
  border-color: #9ca3af;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  transform: translateY(-1px);
}
.floating-btn .btn-icon { font-size: 15px; }
.floating-btn .btn-arrow { margin-left: 4px; transition: transform 0.3s; }
.floating-btn:hover .btn-arrow { transform: translateX(3px); }

/* ========== Page Header ========== */
.page-header {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 22px 28px; margin-bottom: 22px;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.page-header h1 { font-size: 21px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.3px; }
.page-header .meta { font-size: 13px; color: #6b7280; font-weight: 500; }

/* ========== Cards Grid ========== */
.cards-grid { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; }
.cards-grid .card { flex: 0 0 calc(50% - 8px); min-width: 220px; }
.card {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
  padding: 20px 22px;
  transition: all 0.25s; position: relative; overflow: hidden;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.card:hover {
  transform: translateY(-2px);
  border-color: #d1d5db;
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
}
.card.clickable { cursor: pointer; }
.card-title {
  font-size: 11.5px; color: #6b7280;
  margin-bottom: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.card-value {
  font-size: 28px; font-weight: 800; margin-bottom: 6px;
  line-height: 1.1; color: #1a1a2e;
}
.card-desc { font-size: 12px; color: #374151; font-weight: 600; }

/* Employee drill-down cards */
.caliber-card {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 10px;
  background: #ffffff; border: 1px solid #e5e7eb;
  cursor: pointer; transition: all 0.25s; text-decoration: none;
}
.caliber-card:hover { background: #eff6ff; border-color: #93c5fd; transform: translateY(-1px); }
.caliber-icon { font-size: 18px; flex-shrink: 0; }
.caliber-title { flex: 1; font-size: 13px; color: #1a1a2e; font-weight: 500; }
.caliber-count { font-size: 12px; color: #3b82f6; font-weight: 600; }

/* Data caliber info card */
.data-caliber {
  background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 16px;
  padding: 16px 24px; margin-bottom: 24px;
}
.data-caliber h4 { font-size: 13px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
.data-caliber .caliber-item { font-size: 12px; color: #6b7280; margin-bottom: 4px; }
.data-caliber .caliber-item strong { color: #1a1a2e; }

/* Card Status Accents (colored left border + light bg) */
.card.status-ok    { border-left: 3px solid #22c55e; background: #f0fdf4; }
.card.status-warn  { border-left: 3px solid #eab308; background: #fefce8; }
.card.status-bad   { border-left: 3px solid #ef4444; background: #fef2f2; }
.card.neutral       { }

/* Status: cards show via border, tables show via background */
.text-ok, .text-warn, .text-bad { color: #1a1a2e !important; }
td.text-ok    { background: #dcfce7; }
td.text-warn  { background: #fef9c3; }
td.text-bad   { background: #fee2e2; }

/* ========== Filter Bar ========== */
.filter-bar {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  padding: 14px 18px; margin-bottom: 16px;
  background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
}
.filter-bar input {
  flex: 1; min-width: 200px; padding: 8px 14px;
  background: #f9fafb; border: 1px solid #d1d5db;
  border-radius: 8px; color: #1a1a2e; font-size: 13px; outline: none;
  transition: border-color 0.2s;
}
.filter-bar input:focus { border-color: #3b82f6; }
.filter-bar input::placeholder { color: #9ca3af; }
.filter-toggle {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
  background: #f9fafb; border: 1px solid #e5e7eb;
  color: #6b7280;
}
.filter-toggle:hover { border-color: #9ca3af; color: #1a1a2e; }
.filter-toggle.active { background: #eff6ff; border-color: #93c5fd; color: #1d4ed8; font-weight: 600; }
.filter-toggle .dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.filter-clear {
  padding: 6px 14px; border-radius: 8px; font-size: 12px; cursor: pointer;
  background: #fef2f2; border: 1px solid #fecaca;
  color: #dc2626; transition: all 0.2s;
}
.filter-clear:hover { background: #fee2e2; }

/* Caliber section (employee drill cards) */
.caliber-section { margin-bottom: 24px; }
.caliber-section h3 { font-size: 13px; font-weight: 600; color: #6b7280; margin-bottom: 12px; }
.caliber-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }

/* ========== Chart Container ========== */
.chart-wrap {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px 28px; margin-bottom: 22px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.chart-wrap h3 { font-size: 15px; font-weight: 700; margin-bottom: 18px; color: #1a1a2e; letter-spacing: -0.2px; }
.chart-wrap canvas { max-height: 380px; }

/* ========== Table ========== */
.table-wrap {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px 28px; margin-bottom: 22px; overflow-x: auto;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.table-wrap h3 { font-size: 15px; font-weight: 700; margin-bottom: 16px; color: #1a1a2e; letter-spacing: -0.2px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th {
  background: #f9fafb; padding: 11px 12px; text-align: center;
  font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.4px;
  color: #6b7280; border-bottom: 1px solid #e5e7eb; white-space: nowrap;
}
td {
  padding: 9px 12px; text-align: center;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
}
tr:hover td { background: #f9fafb; }
tr.summary td {
  background: #f3f4f6;
  font-weight: 700; color: #1a1a2e;
  border-top: 1px solid #d1d5db;
}
.drill-link { color: #3b82f6; cursor: pointer; font-weight: 600; transition: color 0.2s; }
.drill-link:hover { color: #2563eb; text-decoration: underline; }
.drill-data { cursor: pointer; font-weight: 600; border-bottom: 1px dashed #93c5fd; transition: transform 0.2s; display: inline-block; }
.drill-data:hover { transform: scale(1.12); }
.expand-row { cursor: pointer; color: #3b82f6; font-weight: 600; transition: color 0.2s; }
.expand-row:hover { color: #2563eb; text-decoration: underline; }

/* ========== Modal ========== */
.modal-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.40); z-index: 200;
  justify-content: center; align-items: center;
}
.modal-overlay.show { display: flex; }
.modal {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  width: 92%; max-width: 1000px; max-height: 84vh;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: modalIn 0.22s ease-out;
}
@keyframes modalIn { from { transform: scale(0.95) translateY(8px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 26px; border-bottom: 1px solid #e5e7eb;
}
.modal-header h3 { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.modal-close {
  background: #f3f4f6; border: none; width: 30px; height: 30px;
  border-radius: 50%; font-size: 15px; cursor: pointer; color: #6b7280;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.modal-close:hover { background: #e5e7eb; color: #1a1a2e; }
.modal-body { padding: 18px 26px; overflow-y: auto; flex: 1; }
.modal-body .summary-line { font-size: 13px; color: #6b7280; margin-bottom: 14px; }
.modal-body table { font-size: 12px; }
.modal-body th {
  position: sticky; top: 0;
  background: #f9fafb;
  z-index: 1; color: #6b7280;
}
.modal-body td { color: #374151; }

/* Empty / Loading */
.empty { text-align: center; padding: 60px 20px; color: #9ca3af; font-size: 15px; }
.loading { text-align: center; padding: 100px 20px; color: #9ca3af; font-size: 16px; }
.loading-spinner {
  display: inline-block; width: 40px; height: 40px;
  border: 3px solid #e5e7eb; border-top-color: #3b82f6;
  border-radius: 50%; animation: spin 0.7s linear infinite; margin-bottom: 18px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* ========== Floating Action Buttons ========== */
.fab-container {
  position: fixed; bottom: 24px; right: 24px; z-index: 350;
  display: flex; flex-direction: column; gap: 10px;
  pointer-events: auto;
}
.fab-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 18px; border-radius: 50px;
  border: 1px solid #d1d5db;
  cursor: pointer; font-size: 12.5px; font-weight: 600;
  color: #374151; letter-spacing: 0.1px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  user-select: none; white-space: nowrap;
}
.fab-btn:hover {
  background: #f9fafb; color: #1a1a2e;
  border-color: #9ca3af;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  transform: translateY(-2px) scale(1.02);
}
.fab-btn:active { transform: translateY(0) scale(0.98); }
.fab-btn .fab-icon { font-size: 14px; line-height: 1; }
.fab-btn .fab-toast {
  position: absolute; top: -36px; left: 50%; transform: translateX(-50%);
  background: #22c55e; color: #fff; font-size: 11px;
  padding: 4px 12px; border-radius: 6px; white-space: nowrap;
  opacity: 0; pointer-events: none; transition: opacity 0.2s;
}
.fab-btn .fab-toast.show { opacity: 1; }

/* Responsive */
@media (max-width: 900px) {
  .sidebar { width: 220px; min-width: 220px; }
  .main { margin-left: 220px; padding: 20px; }
  .cards-grid .card { flex: 0 0 calc(50% - 6px); min-width: 170px; }
  .floating-btn { top: 14px; right: 14px; padding: 8px 14px; font-size: 12px; }
  .fab-container { bottom: 16px; right: 16px; gap: 8px; }
  .fab-btn { padding: 8px 14px; font-size: 11.5px; }
}
</style>
<script src="https://cdn.bootcdn.net/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
</head>
<body>

<!-- 纯白底主题 - 无背景渲染 -->

<!-- Floating Button (双击打开飞书，单击拖动) -->
<a class="floating-btn" title="双击查看原始数据明细（可拖动）">
  <span class="btn-icon">&#x1F50D;</span>查看具体明细<span class="btn-arrow">&#x2192;</span>
</a>

<!-- ========== Sidebar (深色调) ========== -->
<div class="sidebar">
  <div class="sidebar-header">
    <div class="logo">&#x1F4CA;</div> 考勤分析
  </div>
  <div class="sidebar-action">
    <a href="index.html" class="back-home-btn">&#x1F3E0; 返回数据面板</a>
  </div>
  <div class="sidebar-nav" id="sidebarNav">
    <div class="nav-item active"><span class="icon">&#x1F3E0;</span>加载中...</div>
  </div>
</div>

<!-- ========== Main Content ========== -->
<div class="main" id="mainContent">
  <div class="loading">
    <div class="loading-spinner"></div>
    <p>正在加载考勤数据...</p>
  </div>
</div>

<!-- ========== Drill-down Modal ========== -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modalTitle">穿透明细</h3>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<!-- ========== FAB Buttons (右下角) ========== -->
<div class="fab-container">
  <div class="fab-btn" id="fabDownload" onclick="downloadImage()">
    <span class="fab-icon">&#x1F4CE;</span>下载图片
    <span class="fab-toast" id="downloadToast">已保存</span>
  </div>
  <div class="fab-btn" id="fabShare" onclick="shareUrl()">
    <span class="fab-icon">&#x1F517;</span>分享网址
    <span class="fab-toast" id="shareToast">已复制</span>
  </div>
</div>

<script>
// ========== FAB Actions: 下载图片 & 分享网址 ==========
function downloadImage() {
  var toast = document.getElementById('downloadToast');
  // 使用 html2canvas 或原生方案: 将当前页面转为图片
  // 方案: 引入 html2canvas CDN 后截图
  if (typeof html2canvas === 'undefined') {
    // 动态加载 html2canvas
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
    s.onload = function() {
      doCapture();
    };
    s.onerror = function() {
      toast.textContent = '加载失败';
      toast.classList.add('show');
      setTimeout(function() { toast.classList.remove('show'); }, 2000);
    };
    document.head.appendChild(s);
  } else {
    doCapture();
  }

  function doCapture() {
    var mainEl = document.getElementById('mainContent');
    if (!mainEl) mainEl = document.body;
    html2canvas(mainEl, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      logging: false,
      ignoreElements: function(el) {
        return el.classList && el.classList.contains('fab-container');
      },
    }).then(function(canvas) {
      var link = document.createElement('a');
      link.download = '考勤报告_' + new Date().toISOString().slice(0,10) + '.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.textContent = '已保存';
      toast.classList.add('show');
      setTimeout(function() { toast.classList.remove('show'); }, 2000);
    }).catch(function(err) {
      console.error('截图失败:', err);
      toast.textContent = '保存失败';
      toast.classList.add('show');
      setTimeout(function() { toast.classList.remove('show'); }, 2000);
    });
  }
}

function shareUrl() {
  var toast = document.getElementById('shareToast');
  var url = window.location.href || document.URL || '';
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(function() {
      toast.textContent = '已复制';
      toast.classList.add('show');
      setTimeout(function() { toast.classList.remove('show'); }, 2000);
    }).catch(function() {
      fallbackCopy(url);
    });
  } else {
    fallbackCopy(url);
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); toast.textContent = '已复制'; }
    catch(e) { toast.textContent = '复制失败'; }
    document.body.removeChild(ta);
    toast.classList.add('show');
    setTimeout(function() { toast.classList.remove('show'); }, 2000);
  }
}

// ========== Draggable Floating Button (双击打开, 单击拖动) ==========
(function() {
  var btn = document.querySelector('.floating-btn');
  if (!btn) return;
  var isDragging = false;
  var didDrag = false;
  var startX, startY, origLeft, origTop;

  function onStart(e) {
    if (e.type === 'touchstart') e.preventDefault();
    isDragging = true;
    didDrag = false;
    var clientX = e.touches ? e.touches[0].clientX : e.clientX;
    var clientY = e.touches ? e.touches[0].clientY : e.clientY;
    startX = clientX;
    startY = clientY;
    var rect = btn.getBoundingClientRect();
    origLeft = rect.left;
    origTop = rect.top;
    btn.classList.add('dragging');
  }

  function onMove(e) {
    if (!isDragging) return;
    var clientX = e.touches ? e.touches[0].clientX : e.clientX;
    var clientY = e.touches ? e.touches[0].clientY : e.clientY;
    var dx = clientX - startX;
    var dy = clientY - startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
    btn.style.left = (origLeft + dx) + 'px';
    btn.style.top = (origTop + dy) + 'px';
    btn.style.right = 'auto';
  }

  function onEnd(e) {
    if (!isDragging) return;
    isDragging = false;
    btn.classList.remove('dragging');
  }

  btn.addEventListener('mousedown', onStart);
  btn.addEventListener('touchstart', onStart, { passive: false });
  document.addEventListener('mousemove', onMove);
  document.addEventListener('touchmove', onMove, { passive: false });
  document.addEventListener('mouseup', onEnd);
  document.addEventListener('touchend', onEnd);

  // 双击打开飞书
  btn.addEventListener('dblclick', function(e) {
    if (didDrag) return;
    e.preventDefault();
    window.open('__FEISHU_URL__', '_blank');
  });

  // 单击不跳转(拖拽后单击也忽略)
  btn.addEventListener('click', function(e) {
    e.preventDefault();
  });
})();

// ========== Data ==========
var DATA = __DATA_JSON__;

// ========== Helpers ==========
function p2n(pctStr) { return parseFloat(pctStr) / 100; }
function fmtH(v) { v = parseFloat(v); return v > 0 ? v + 'h' : '-'; }

function statusClass(val, type) {
  var v = typeof val === 'number' ? val : p2n(val);
  if (type === 'miss') {
    if (v < 0.5) return 'text-ok';
    if (v < 0.9) return 'text-warn';
    return 'text-bad';
  }
  if (type === 'hub') {
    if (v >= 0.9) return 'text-ok';
    if (v >= 0.5) return 'text-warn';
    return 'text-bad';
  }
  if (type === 'schedule' || type === 'punch') {
    if (v >= 1.0) return 'text-ok';
    if (v >= 0.9) return 'text-warn';
    return 'text-bad';
  }
  if (type === 'correct') {
    if (v >= 0.9) return 'text-ok';
    if (v >= 0.5) return 'text-warn';
    return 'text-bad';
  }
  if (v >= 0.9) return 'text-ok';
  if (v >= 0.5) return 'text-warn';
  return 'text-bad';
}

function cardStatusClass(val, type) {
  var v = typeof val === 'number' ? val : p2n(val);
  if (type === 'miss') {
    if (v < 0.5) return 'status-ok';
    if (v < 0.9) return 'status-warn';
    return 'status-bad';
  }
  if (type === 'hub') {
    if (v >= 0.9) return 'status-ok';
    if (v >= 0.5) return 'status-warn';
    return 'status-bad';
  }
  if (type === 'schedule' || type === 'punch') {
    if (v >= 1.0) return 'status-ok';
    if (v >= 0.9) return 'status-warn';
    return 'status-bad';
  }
  if (type === 'correct') {
    if (v >= 0.9) return 'status-ok';
    if (v >= 0.5) return 'status-warn';
    return 'status-bad';
  }
  if (v >= 0.9) return 'status-ok';
  if (v >= 0.5) return 'status-warn';
  return 'status-bad';
}

function getDotClass(s) {
  var schedRate = p2n(s['排班']['排班率']);
  var correctRate = p2n(s['排班正确']['正确率']);
  var worst = 'ok';
  if (schedRate < 0.9 || correctRate < 0.5) worst = 'red';
  else if (schedRate < 1.0 || correctRate < 0.9) worst = 'yellow';
  return 'dot-' + worst;
}

// ========== Drill-down Data Store ==========
var drillStore = new Map();
var drillIdCounter = 0;

function registerDrill(title, employees) {
  var id = ++drillIdCounter;
  drillStore.set(id, { title: title, employees: employees });
  return id;
}

function drillBtn(label, employees, showCount) {
  if (!employees || employees.length === 0) return '';
  var id = registerDrill(label, employees);
  var cnt = showCount ? employees.length : '';
  return '<span class="drill-link" onclick="openDrill(' + id + ')" title="点击查看明细">' + cnt + '</span>';
}

function drillData(val, label, employees) {
  if (!employees || employees.length === 0) return String(val);
  var id = registerDrill(label, employees);
  return '<span class="drill-data" onclick="openDrill(' + id + ')" title="点击穿透查看明细">' + val + '</span>';
}

function infoBtn(label, employees) {
  if (!employees || employees.length === 0) return '';
  return ' <span class="drill-data" onclick="openDrill(' + registerDrill(label, employees) + ')" style="font-size:11px;cursor:pointer" title="点击穿透">&#x1F4CB;</span>';
}

// ========== Card Component ==========
function metricCard(title, valStr, desc, statusCls, cardCls, employees) {
  var cardC = cardCls ? ' ' + cardCls : '';
  var valC = statusCls ? ' ' + statusCls : '';
  var drillVal = employees ? drillData(valStr, '', employees) : valStr;
  var drillIcon = employees ? ' <span style="font-size:10px;color:#9ca3af;font-weight:400">(可查看明细)</span>' : '';
  return '<div class="card' + cardC + '">' +
    '<div class="card-title">' + title + drillIcon + '</div>' +
    '<div class="card-value' + valC + '">' + drillVal + '</div>' +
    (desc ? '<div class="card-desc">' + desc + '</div>' : '') +
  '</div>';
}

function caliberCard(title, employees, icon) {
  if (!employees || employees.length === 0) return '';
  var id = registerDrill(title, employees);
  return '<a class="caliber-card" onclick="openDrill(' + id + ')" title="点击穿透查看明细">' +
    '<span class="caliber-icon">' + (icon || '\u{1F50D}') + '</span>' +
    '<span class="caliber-title">' + title + '</span>' +
    '<span class="caliber-count">' + employees.length + '人</span>' +
  '</a>';
}

// ========== Chart Helpers ==========
var chartColors = {
  green: '#22c55e',
  yellow: '#eab308',
  red: '#ef4444',
  blue: '#3b82f6',
  purple: '#8b5cf6',
  cyan: '#06b6d4',
  orange: '#f97316',
};
var chartInstances = {};

function destroyAllCharts() {
  Object.keys(chartInstances).forEach(function(k) {
    if (chartInstances[k]) { chartInstances[k].destroy(); delete chartInstances[k]; }
  });
}

function drawBarChart(canvasId, config) {
  if (typeof Chart === 'undefined') return;
  var ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  var isLine = config.type === 'line';
  var dataLabelPlugin = {
    id: 'dataLabels',
    afterDatasetsDraw: function(chart) {
      var ctx2 = chart.ctx;
      chart.data.datasets.forEach(function(ds, i) {
        var meta = chart.getDatasetMeta(i);
        if (!meta.hidden) {
          meta.data.forEach(function(point, j) {
            var v = ds.data[j];
            if (v == null) return;
            var label = String(v);
            ctx2.font = 'bold 10px sans-serif';
            ctx2.fillStyle = ds.borderColor || '#333';
            ctx2.textAlign = 'center';
            ctx2.textBaseline = 'bottom';
            ctx2.fillText(label, point.x, point.y - 8);
          });
        }
      });
    }
  };

  chartInstances[canvasId] = new Chart(ctx, {
    type: config.type || 'bar',
    data: config.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: config.legend !== false, position: 'top',
          labels: { usePointStyle: true, padding: 20, font: { size: 12 }, color: '#6b7280' }
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 }, color: '#6b7280' }
        },
        y: {
          beginAtZero: true, max: config.yMax || 100,
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { font: { size: 11 }, color: '#6b7280', callback: function(v) { return v + '%'; } }
        }
      }
    },
    plugins: [dataLabelPlugin]
  });
}

// ========== Filter Logic ==========
var activeMetricFilters = { schedule: true, correct: true, hub: true, punch: true };

function renderSearchBar(prefix) {
  return '<div class="filter-bar">' +
    '<input type="text" placeholder="搜索部门名称..." oninput="applyFilters(\'' + prefix + '\')" id="' + prefix + '_search">' +
  '</div>';
}

function renderChartFilter(prefix) {
  return '<div class="filter-bar">' +
    '<span class="filter-toggle active" data-metric="schedule" onclick="toggleMetric(\'' + prefix + '\',\'schedule\',this)"><span class="dot" style="background:#22c55e"></span>排班率</span>' +
    '<span class="filter-toggle active" data-metric="correct" onclick="toggleMetric(\'' + prefix + '\',\'correct\',this)"><span class="dot" style="background:#3b82f6"></span>排班正确率</span>' +
    '<span class="filter-toggle active" data-metric="hub" onclick="toggleMetric(\'' + prefix + '\',\'hub\',this)"><span class="dot" style="background:#8b5cf6"></span>HUB排班正确率</span>' +
    '<span class="filter-toggle active" data-metric="punch" onclick="toggleMetric(\'' + prefix + '\',\'punch\',this)"><span class="dot" style="background:#f97316"></span>打卡率</span>' +
    '<span class="filter-clear" onclick="clearFilters(\'' + prefix + '\')">重置</span>' +
  '</div>';
}

function toggleMetric(prefix, metric, el) {
  activeMetricFilters[metric] = !activeMetricFilters[metric];
  el.classList.toggle('active', activeMetricFilters[metric]);
  updateChartVisibility(prefix);
}

function updateChartVisibility(prefix) {
  var names = [prefix + 'Chart', prefix + 'LineChart'];
  names.forEach(function(name) {
    var inst = chartInstances[name];
    if (!inst) return;
    var ds = inst.data.datasets;
    for (var i = 0; i < ds.length; i++) {
      var d = ds[i].label;
      if (d.indexOf('排班率') !== -1) inst.setDatasetVisibility(i, activeMetricFilters.schedule);
      else if (d.indexOf('HUB') !== -1) inst.setDatasetVisibility(i, activeMetricFilters.hub);
      else if (d.indexOf('打卡率') !== -1) inst.setDatasetVisibility(i, activeMetricFilters.punch);
      else if (d.indexOf('正确率') !== -1) inst.setDatasetVisibility(i, activeMetricFilters.correct);
    }
    inst.update();
  });
}

function applyFilters(prefix) {
  var q = (document.getElementById(prefix + '_search') || {value:''}).value.toLowerCase();
  var tbody = document.querySelector('#' + prefix + '_table tbody');
  if (!tbody) return;
  tbody.querySelectorAll('tr').forEach(function(tr) {
    tr.style.display = q === '' || tr.textContent.toLowerCase().indexOf(q) !== -1 ? '' : 'none';
  });
}

function clearFilters(prefix) {
  var inp = document.getElementById(prefix + '_search');
  if (inp) inp.value = '';
  activeMetricFilters = { schedule: true, correct: true, hub: true, punch: true };
  document.querySelectorAll('.filter-toggle').forEach(function(el) {
    var m = el.getAttribute('data-metric');
    el.classList.toggle('active', activeMetricFilters[m] === true);
  });
  applyFilters(prefix);
  updateChartVisibility(prefix);
}

var sortAscending = false;
function sortTable(tableId, colIdx) {
  sortAscending = !sortAscending;
  var tbody = document.querySelector('#' + tableId + ' tbody');
  if (!tbody) return;
  var rows = Array.from(tbody.querySelectorAll('tr'));
  rows.sort(function(a, b) {
    var va = parseFloat(a.getAttribute('data-punch')) || 0;
    var vb = parseFloat(b.getAttribute('data-punch')) || 0;
    return sortAscending ? va - vb : vb - va;
  });
  rows.forEach(function(r) { tbody.appendChild(r); });
}

// ========== Render Sidebar ==========
function renderSidebar() {
  var nav = document.getElementById('sidebarNav');
  var html = '<div class="nav-item active" data-view="overview" onclick="showView(\'overview\')">' +
    '<span class="icon">&#x1F3E0;</span>全览<span class="badge">' + DATA.meta.total_employees + '人</span></div>';

  DATA.departments.forEach(function(dept, i) {
    var dId = 'dept-' + i;
    html += '<div class="nav-item" data-view="' + dId + '" onclick="toggleDept(\'' + dId + '\', event)">' +
      '<span class="icon">&#x1F5C2;</span>' + dept.name + '<span class="badge">' + dept.summary.total + '人</span>' +
      '<span class="arrow">&#x25B6;</span></div>';
    html += '<div class="sub-nav" id="sub-' + dId + '">';
    dept.sub_depts.forEach(function(sub, j) {
      var sId = dId + '-sub-' + j;
      var dotCls = getDotClass(sub.summary);
      html += '<div class="nav-item" data-view="' + sId + '" onclick="showView(\'' + sId + '\')">' +
        '<span class="icon">&#x1F4C3;</span>' + sub.name +
        '<span class="status-dot ' + dotCls + '"></span>' +
        '<span class="badge">' + sub.summary.total + '人</span></div>';
    });
    html += '</div>';
  });

  nav.innerHTML = html;
}

function toggleDept(dId, event) {
  event.stopPropagation();
  var item = event.currentTarget;
  var sub = document.getElementById('sub-' + dId);
  var isOpen = sub.classList.contains('show');
  if (isOpen) {
    sub.classList.remove('show');
    item.classList.remove('expanded');
  } else {
    sub.classList.add('show');
    item.classList.add('expanded');
  }
  showView(dId);
}

// ========== View Switching ==========
function showView(viewId) {
  destroyAllCharts();
  document.querySelectorAll('.nav-item').forEach(function(el) { el.classList.remove('active'); });
  var target = document.querySelector('[data-view="' + viewId + '"]');
  if (target) target.classList.add('active');

  if (viewId === 'overview') {
    renderOverview();
  } else if (viewId.startsWith('dept-') && viewId.indexOf('-sub-') === -1) {
    var idx = parseInt(viewId.split('-')[1]);
    renderDepartment(DATA.departments[idx]);
  } else if (viewId.indexOf('-sub-') !== -1) {
    var parts = viewId.split('-');
    var dIdx = parseInt(parts[1]);
    var sIdx = parseInt(parts[3]);
    renderSubDepartment(DATA.departments[dIdx], DATA.departments[dIdx].sub_depts[sIdx]);
  }
}

// ========== Render Overview ==========
function renderOverview() {
  var o = DATA.overview;
  var main = document.getElementById('mainContent');

  var schedRate = p2n(o['排班']['排班率']);
  var correctRate = p2n(o['排班正确']['正确率']);
  var hubRate = p2n(o['HUB']['正确率']);
  var punchRate = p2n(o['打卡率']['打卡率']);
  var punchD = o['打卡率'];
  var resignRate = p2n(punchD['补签率']);

  var cards = '<div class="page-header">' +
    '<h1>&#x1F4CA; 考勤管理数据分析报告</h1>' +
    '<div class="meta">日期: ' + DATA.meta.date_range + ' &nbsp;|&nbsp; 部门: ' + DATA.meta.department_count + '个 &nbsp;|&nbsp; 总人数: ' + o.total + '人</div>' +
  '</div>' +
  '<div class="cards-grid">' +
    metricCard('\uD83D\uDC65 总人数', o.total, '', '', null, o.all_employees) +
    metricCard('\u23F0 日超8H合计', Math.round(o['日超8H'].total_hours) + 'h', '\u8D85\u6807\u7387 ' + o['日超8H'].rate,
      o['日超8H'].total_hours > 0 ? 'text-warn' : 'text-ok',
      o['日超8H'].total_hours > 0 ? 'status-warn' : 'status-ok',
      o['日超8H'].employees.length > 0 ? o['日超8H'].employees : null) +
    metricCard('\uD83D\uDCCB 排班率', o['排班']['排班率'],
      '已排班 ' + o['排班']['已排班'] + ' / 未排班 ' + o['排班']['未排班'],
      statusClass(schedRate, 'schedule'),
      cardStatusClass(schedRate, 'schedule')) +
    metricCard('\u2705 排班正确率', o['排班正确']['正确率'],
      '正确 ' + o['排班正确']['正确'] + ' / 不正确 ' + o['排班正确']['不正确'],
      statusClass(correctRate, 'correct'),
      cardStatusClass(correctRate, 'correct'),
      o['排班正确']['employees_不正确'].length > 0 ? o['排班正确']['employees_不正确'] : null) +
    metricCard('\u2705 \u6253\u5361\u7387', punchD['打卡率'] + '',
      '\u8865\u7B7E\u7387 ' + punchD['补签率'],
      statusClass(punchRate, 'punch'),
      cardStatusClass(punchRate, 'punch'),
      punchD.employees.length > 0 ? punchD.employees : null) +
    metricCard('\uD83D\uDD37 HUB排班正确率', o['HUB']['正确率'],
      'HUB总 ' + o['HUB'].total + '人 | 目标90% | ' + (hubRate >= 0.9 ? '\u2705达标' : '\u26A0未达标'),
      statusClass(hubRate, 'hub'),
      cardStatusClass(hubRate, 'hub'),
      o['HUB']['employees_不正确'].length > 0 ? o['HUB']['employees_不正确'] : null) +
    metricCard('\uD83D\uDCC5 \u672C\u5468\u52A0\u73ED\u5DE5\u65F6', fmtH(o['本周加班工时']), DATA.meta.date_range,
      o['本周加班工时'] > 0 ? 'text-warn' : 'text-ok',
      o['本周加班工时'] > 0 ? 'status-warn' : 'status-ok') +
    metricCard('\uD83D\uDCC5 \u4E0A\u5468\u52A0\u73ED\u5DE5\u65F6', fmtH(o['上周加班工时']), DATA.meta.date_range.replace(/\/.*/, '') + ' 上周', '', '') +
  '</div>' +

  // ---- 数据口径说明 ----
  '<div class="data-caliber"><h4>\u{1F4CA} 数据口径说明</h4>' +
    '<div class="caliber-item"><strong>排班率</strong> = 已排班人数 / 总人数</div>' +
    '<div class="caliber-item"><strong>打卡率</strong> = 当天员工打卡次数总和 / 当天应出勤人员标准打卡总和</div>' +
    '<div class="caliber-item"><strong>HUB排班正确率</strong> = HUB首打卡跟班次卡点差1h以内人数 / HUB总人数</div>' +
  '</div>';

  // Department table (明细先于柱状图)
  var tableRows = DATA.departments.map(function(dept, i) {
    var s = dept.summary;
    var dId = 'dept-' + i;
    var pD = s['打卡率'];
    var o8D = s['日超8H'];
    var pdRate = p2n(pD['打卡率']);
    return '<tr data-punch="' + pdRate + '">' +
      '<td><span class="expand-row" onclick="showView(\'' + dId + '\')">' + dept.name + '</span></td>' +
      '<td>' + drillData(s.total, '全员', s.all_employees) + '</td>' +
      '<td>' + drillData(Math.round(o8D.total_hours) + 'h', '日超8H', o8D.employees) + '</td>' +
      '<td class="' + statusClass(pdRate, 'punch') + '">' + pD['打卡率'] + '</td>' +
      '<td class="' + statusClass(p2n(pD['补签率']), 'resign') + '">' + pD['补签率'] + '</td>' +
      '<td>' + fmtH(s['本周加班工时']) + '</td>' +
      '<td>' + fmtH(s['上周加班工时']) + '</td>' +
      '<td>' + drillData(s['排班']['未排班'], '未排班', s['排班']['employees_未排班']) + '</td>' +
      '<td class="' + statusClass(p2n(s['排班']['排班率']), 'schedule') + '">' + s['排班']['排班率'] + '</td>' +
      '<td class="' + statusClass(p2n(s['排班正确']['正确率']), 'correct') + '">' + s['排班正确']['正确率'] + '</td>' +
      '<td class="' + statusClass(p2n(s['HUB']['正确率']), 'hub') + '">' + s['HUB']['正确率'] + (p2n(s['HUB']['正确率']) < 0.9 ? ' \u26A0' : '') + '</td>' +
    '</tr>';
  }).join('');

  var table = renderSearchBar('overview') +
    '<div class="table-wrap">' +
    '<h3>&#x1F4CA; 部门总览（点击部门名查看四级明细）</h3>' +
    '<table id="overview_table"><thead><tr>' +
    '<th>部门</th><th>人数 (可查看明细)</th><th>日超8H合计 (可查看明细)</th><th onclick="sortTable(\'overview_table\',3)" style="cursor:pointer" title="点击排序">打卡率 ⇅</th><th>补签率</th><th>本周加班(h)</th><th>上周加班(h)</th><th>未排班数 (可查看明细)</th><th>排班率</th><th>排班正确率</th><th>HUB正确率</th>' +
    '</tr></thead><tbody>' + tableRows + '</tbody></table></div>';

  // ---- Bar Chart (放在明细表格下面) ----
  var topDepts = DATA.departments.slice(0, 12);
  var barLabels = topDepts.map(function(d) { return d.name.length > 8 ? d.name.substring(0,8)+'...' : d.name; });
  var scheduleData = topDepts.map(function(d) { return parseFloat(d.summary['排班']['排班率']); });
  var correctData = topDepts.map(function(d) { return parseFloat(d.summary['排班正确']['正确率']); });
  var hubData = topDepts.map(function(d) { return parseFloat(d.summary['HUB']['正确率']); });
  var punchData = topDepts.map(function(d) { return parseFloat(d.summary['打卡率']['打卡率']); });

  var chartHtml = renderChartFilter('overview') +
    '<div class="chart-wrap"><h3>&#x1F4C8; 部门指标趋势（前12部门）</h3>' +
    '<div style="position:relative; height:380px;"><canvas id="overviewLineChart"></canvas></div></div>';

  // 顺序: cards → table → charts
  main.innerHTML = cards + table + chartHtml;

  var lineDs = [
    { label: '排班率', data: scheduleData, borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#22c55e' },
    { label: '排班正确率', data: correctData, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#3b82f6' },
    { label: 'HUB正确率', data: hubData, borderColor: '#8b5cf6', backgroundColor: 'rgba(139,92,246,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#8b5cf6' },
    { label: '打卡率', data: punchData, borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#f97316' },
  ];

  setTimeout(function() {
    drawBarChart('overviewLineChart', {
      type: 'line',
      data: { labels: barLabels, datasets: lineDs },
      legend: true,
      yMax: 105
    });
  }, 100);
}

// ========== Render Department (三级) ==========
function renderDepartment(dept) {
  var s = dept.summary;
  var main = document.getElementById('mainContent');

  var schedRate = p2n(s['排班']['排班率']);
  var correctRate = p2n(s['排班正确']['正确率']);
  var hubRate = p2n(s['HUB']['正确率']);
  var punchRate = p2n(s['打卡率']['打卡率']);
  var punchD = s['打卡率'];

  var html = '<div class="page-header">' +
    '<h1>&#x1F3E2; ' + dept.name + '</h1>' +
    '<div class="meta">总人数: ' + s.total + '人 | 日期: ' + DATA.meta.date_range + '</div></div>' +
  '<div class="cards-grid">' +
    metricCard('\uD83D\uDC65 总人数', s.total, '', '', null, s.all_employees) +
    metricCard('\u23F0 日超8H合计', Math.round(s['日超8H'].total_hours) + 'h', '\u8D85\u6807\u7387 ' + s['日超8H'].rate,
      s['日超8H'].total_hours > 0 ? 'text-warn' : 'text-ok',
      s['日超8H'].total_hours > 0 ? 'status-warn' : 'status-ok',
      s['日超8H'].employees.length > 0 ? s['日超8H'].employees : null) +
    metricCard('\uD83D\uDCCB 排班率', s['排班']['排班率'], '已排班 ' + s['排班']['已排班'] + ' / 未排班 ' + s['排班']['未排班'],
      statusClass(schedRate, 'schedule'),
      cardStatusClass(schedRate, 'schedule'),
      s['排班']['employees_未排班'].length > 0 ? s['排班']['employees_未排班'] : null) +
    metricCard('\u2705 排班正确率', s['排班正确']['正确率'], '正确 ' + s['排班正确']['正确'] + ' / 不正确 ' + s['排班正确']['不正确'],
      statusClass(correctRate, 'correct'),
      cardStatusClass(correctRate, 'correct'),
      s['排班正确']['employees_不正确'].length > 0 ? s['排班正确']['employees_不正确'] : null) +
    metricCard('\u2705 \u6253\u5361\u7387', punchD['打卡率'] + '',
      '\u8865\u7B7E\u7387 ' + punchD['补签率'],
      statusClass(punchRate, 'punch'),
      cardStatusClass(punchRate, 'punch'),
      punchD.employees.length > 0 ? punchD.employees : null) +
    metricCard('\uD83D\uDD37 HUB正确率', s['HUB']['正确率'], 'HUB ' + s['HUB'].total + '人 | ' + (hubRate >= 0.9 ? '\u2705达标' : '\u26A0未达标'),
      statusClass(hubRate, 'hub'),
      cardStatusClass(hubRate, 'hub'),
      s['HUB']['employees_不正确'].length > 0 ? s['HUB']['employees_不正确'] : null) +
    metricCard('\uD83D\uDCC5 本周加班工时', fmtH(s['本周加班工时']), DATA.meta.date_range,
      s['本周加班工时'] > 0 ? 'text-warn' : 'text-ok',
      s['本周加班工时'] > 0 ? 'status-warn' : 'status-ok') +
    metricCard('\uD83D\uDCC5 上周加班工时', fmtH(s['上周加班工时']), DATA.meta.date_range.replace(/\/.*/, '') + ' 上周', '', '') +
  '</div>' +

  '<div class="data-caliber"><h4>\u{1F4CA} 数据口径说明</h4>' +
    '<div class="caliber-item"><strong>排班率</strong> = 已排班人数 / 总人数</div>' +
    '<div class="caliber-item"><strong>打卡率</strong> = 当天员工打卡次数总和 / 当天应出勤人员标准打卡总和</div>' +
    '<div class="caliber-item"><strong>HUB排班正确率</strong> = HUB首打卡跟班次卡点差1h以内人数 / HUB总人数</div>' +
  '</div>';

  // 四级部门明细表 (放在柱状图前面)
  var subRows = dept.sub_depts.map(function(sub, j) {
    var ss = sub.summary;
    var mD = ss['打卡率'];
    var o8D = ss['日超8H'];
    var pdRate = p2n(mD['打卡率']);
    return '<tr data-punch="' + pdRate + '">' +
      '<td>' + sub.name + '</td>' +
      '<td>' + drillData(ss.total, dept.name + '-' + sub.name + ' 全员', ss.all_employees) + '</td>' +
      '<td>' + drillData(o8D.total_hours + 'h', dept.name + '-' + sub.name + ' 日超8H', o8D.employees) + '</td>' +
      '<td class="' + statusClass(pdRate, 'punch') + '">' + mD['打卡率'] + '</td>' +
      '<td class="' + statusClass(p2n(mD['补签率']), 'resign') + '">' + mD['补签率'] + '</td>' +
      '<td>' + fmtH(ss['本周加班工时']) + '</td>' +
      '<td>' + fmtH(ss['上周加班工时']) + '</td>' +
      '<td>' + drillData(ss['排班']['未排班'], dept.name + '-' + sub.name + ' 未排班', ss['排班']['employees_未排班']) + '</td>' +
      '<td class="' + statusClass(p2n(ss['排班']['排班率']), 'schedule') + '">' + ss['排班']['排班率'] + '</td>' +
      '<td class="' + statusClass(p2n(ss['排班正确']['正确率']), 'correct') + '">' + ss['排班正确']['正确率'] + '</td>' +
      '<td class="' + statusClass(p2n(ss['HUB']['正确率']), 'hub') + '">' + ss['HUB']['正确率'] + '</td>' +
    '</tr>';
  }).join('');

  subRows += '<tr class="summary"><td>&#x1F4CA; ' + dept.name + ' 汇总</td>' +
    '<td>' + s.total + '</td>' +
    '<td>' + Math.round(s['日超8H'].total_hours) + 'h (' + s['日超8H'].rate + ')</td>' +
    '<td>' + punchD['打卡率'] + '</td>' +
    '<td>' + punchD['补签率'] + '</td>' +
    '<td>' + fmtH(s['本周加班工时']) + '</td>' +
    '<td>' + fmtH(s['上周加班工时']) + '</td>' +
    '<td>' + s['排班']['未排班'] + '</td>' +
    '<td>' + s['排班']['排班率'] + '</td>' +
    '<td>' + s['排班正确']['正确率'] + '</td>' +
    '<td>' + s['HUB']['正确率'] + '</td></tr>';

  html += renderSearchBar('dept') +
    '<div class="table-wrap"><h3>&#x1F4CA; 四级部门明细</h3>' +
    '<table id="dept_table"><thead><tr>' +
    '<th>四级部门</th><th>人数 (可查看明细)</th><th>日超8H合计 (可查看明细)</th><th onclick="sortTable(\'dept_table\',3)" style="cursor:pointer" title="点击排序">打卡率 ⇅</th><th>补签率</th><th>本周加班(h)</th><th>上周加班(h)</th><th>未排班数 (可查看明细)</th><th>排班率</th><th>排班正确率</th><th>HUB正确率</th>' +
    '</tr></thead><tbody>' + subRows + '</tbody></table></div>';

  // 柱状图 (放在明细表格下面)
  if (dept.sub_depts.length > 0) {
    var subLabels = dept.sub_depts.map(function(sd) { return sd.name.length > 10 ? sd.name.substring(0,10)+'..' : sd.name; });
    var subSched = dept.sub_depts.map(function(sd) { return parseFloat(sd.summary['排班']['排班率']); });
    var subCorrect = dept.sub_depts.map(function(sd) { return parseFloat(sd.summary['排班正确']['正确率']); });
    var subHub = dept.sub_depts.map(function(sd) { return parseFloat(sd.summary['HUB']['正确率']); });
    var subPunch = dept.sub_depts.map(function(sd) { return parseFloat(sd.summary['打卡率']['打卡率']); });

    html += renderChartFilter('dept') +
    '<div class="chart-wrap"><h3>&#x1F4C8; 四级部门指标趋势</h3>' +
      '<div style="position:relative; height:350px;"><canvas id="deptLineChart"></canvas></div></div>';

    html += '<script class="chart-config" data-id="deptLineChart">' +
      JSON.stringify({
        labels: subLabels,
        schedule: subSched,
        correct: subCorrect,
        hub: subHub,
        punch: subPunch
      }) + '</' + 'script>';
  }

  // 顺序: cards → table → chart
  main.innerHTML = html;

  setTimeout(function() {
    var configEl = document.querySelector('.chart-config[data-id="deptLineChart"]');
    if (!configEl) return;
    var cfg = JSON.parse(configEl.textContent);
    drawBarChart('deptLineChart', {
      type: 'line',
      data: {
        labels: cfg.labels,
        datasets: [
          { label: '排班率', data: cfg.schedule, borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#22c55e' },
          { label: '排班正确率', data: cfg.correct, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#3b82f6' },
          { label: 'HUB正确率', data: cfg.hub, borderColor: '#8b5cf6', backgroundColor: 'rgba(139,92,246,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#8b5cf6' },
          { label: '打卡率', data: cfg.punch, borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,0.10)', borderWidth: 2, tension: 0.3, pointRadius: 4, pointBackgroundColor: '#f97316' },
        ]
      },
      legend: true,
      yMax: 105
    });
  }, 100);
}

// ========== Render Sub-Department (四级) ==========
function renderSubDepartment(dept, sub) {
  var s = sub.summary;
  var main = document.getElementById('mainContent');
  var schedRate = p2n(s['排班']['排班率']);
  var correctRate = p2n(s['排班正确']['正确率']);
  var hubRate = p2n(s['HUB']['正确率']);
  var punchRate = p2n(s['打卡率']['打卡率']);
  var punchD = s['打卡率'];

  var html = '<div class="page-header">' +
    '<h1>&#x1F4C3; ' + dept.name + ' / ' + sub.name + '</h1>' +
    '<div class="meta">总人数: ' + s.total + '人 | 日期: ' + DATA.meta.date_range + '</div></div>' +
  '<div class="cards-grid">' +
    metricCard('\uD83D\uDC65 总人数', s.total, '', '', null, s.all_employees) +
    metricCard('\u23F0 日超8H合计', Math.round(s['日超8H'].total_hours) + 'h', '\u8D85\u6807\u7387 ' + s['日超8H'].rate,
      s['日超8H'].total_hours > 0 ? 'text-warn' : 'text-ok',
      s['日超8H'].total_hours > 0 ? 'status-warn' : 'status-ok',
      s['日超8H'].employees.length > 0 ? s['日超8H'].employees : null) +
    metricCard('\uD83D\uDCCB 排班率', s['排班']['排班率'], '已排班 ' + s['排班']['已排班'] + ' / 未排班 ' + s['排班']['未排班'],
      statusClass(schedRate, 'schedule'),
      cardStatusClass(schedRate, 'schedule'),
      s['排班']['employees_未排班'].length > 0 ? s['排班']['employees_未排班'] : null) +
    metricCard('\u2705 排班正确率', s['排班正确']['正确率'], '正确 ' + s['排班正确']['正确'] + ' / 不正确 ' + s['排班正确']['不正确'],
      statusClass(correctRate, 'correct'),
      cardStatusClass(correctRate, 'correct'),
      s['排班正确']['employees_不正确'].length > 0 ? s['排班正确']['employees_不正确'] : null) +
    metricCard('\u2705 \u6253\u5361\u7387', punchD['打卡率'] + '',
      '\u8865\u7B7E\u7387 ' + punchD['补签率'],
      statusClass(punchRate, 'punch'),
      cardStatusClass(punchRate, 'punch'),
      punchD.employees.length > 0 ? punchD.employees : null) +
    metricCard('\uD83D\uDD37 HUB正确率', s['HUB']['正确率'], 'HUB ' + s['HUB'].total + '人 | ' + (hubRate >= 0.9 ? '\u2705达标' : '\u26A0未达标'),
      statusClass(hubRate, 'hub'),
      cardStatusClass(hubRate, 'hub'),
      s['HUB']['employees_不正确'].length > 0 ? s['HUB']['employees_不正确'] : null) +
    metricCard('\uD83D\uDCC5 本周加班工时', fmtH(s['本周加班工时']), DATA.meta.date_range,
      s['本周加班工时'] > 0 ? 'text-warn' : 'text-ok',
      s['本周加班工时'] > 0 ? 'status-warn' : 'status-ok') +
    metricCard('\uD83D\uDCC5 上周加班工时', fmtH(s['上周加班工时']), DATA.meta.date_range.replace(/\/.*/, '') + ' 上周', '', '') +
  '</div>' +

  '<div class="data-caliber"><h4>\u{1F4CA} 数据口径说明</h4>' +
    '<div class="caliber-item"><strong>排班率</strong> = 已排班人数 / 总人数</div>' +
    '<div class="caliber-item"><strong>打卡率</strong> = 当天员工打卡次数总和 / 当天应出勤人员标准打卡总和</div>' +
    '<div class="caliber-item"><strong>HUB排班正确率</strong> = HUB首打卡跟班次卡点差1h以内人数 / HUB总人数</div>' +
  '</div>';

  // 完整指标表 (放在柱状图前面)
  html += '<div class="table-wrap"><h3>&#x1F4CA; ' + sub.name + ' - 完整指标</h3>' +
    '<table><thead><tr><th>指标</th><th>数值</th><th>说明</th></tr></thead><tbody>' +
    '<tr><td>总人数</td><td>' + s.total + '</td><td>去重工号数</td></tr>' +
    '<tr><td>日超8H合计</td><td>' + s['日超8H'].total_hours + 'h (' + s['日超8H'].rate + ')</td>' +
      '<td>' + (s['日超8H'].employees.length > 0 ? infoBtn('日超8H', s['日超8H'].employees) + '查看明细' : '无') + '</td></tr>' +
    '<tr><td>排班率</td><td class="' + statusClass(schedRate, 'schedule') + '">' + s['排班']['排班率'] + '</td>' +
      '<td>已排班' + s['排班']['已排班'] + ' / 未排班' + s['排班']['未排班'] + ' ' + (s['排班']['未排班'] > 0 ? infoBtn('未排班', s['排班']['employees_未排班']) + '查看' : '') + '</td></tr>' +
    '<tr><td>排班正确率</td><td class="' + statusClass(correctRate, 'correct') + '">' + s['排班正确']['正确率'] + '</td>' +
      '<td>正确' + s['排班正确']['正确'] + ' / 不正确' + s['排班正确']['不正确'] + ' ' + (s['排班正确']['不正确'] > 0 ? infoBtn('不正确', s['排班正确']['employees_不正确']) + '查看' : '') + '</td></tr>' +
    '<tr><td>打卡率</td><td class="' + statusClass(punchRate, 'punch') + '">' + punchD['打卡率'] + '</td>' +
      '<td>打卡数' + punchD['打卡数'] + ' / 标准打卡数' + punchD['标准打卡数'] + '</td></tr>' +
    '<tr><td>补签率</td><td class="' + statusClass(p2n(punchD['补签率']), 'resign') + '">' + punchD['补签率'] + '</td>' +
      '<td>补签数' + punchD['补签数_emp'] + '</td></tr>' +
    '<tr><td>HUB正确率</td><td class="' + statusClass(hubRate, 'hub') + '">' + s['HUB']['正确率'] + '</td>' +
      '<td>HUB' + s['HUB'].total + '人, 目标90% ' + (hubRate >= 0.9 ? '\u2705' : '\u26A0') + ' ' + (s['HUB']['不正确'] > 0 ? infoBtn('HUB不正确', s['HUB']['employees_不正确']) + '查看' : '') + '</td></tr>' +
    '<tr><td>本周加班工时</td><td>' + fmtH(s['本周加班工时']) + '</td><td>累计加班工时（签字报表本周）</td></tr>' +
    '<tr><td>上周加班工时</td><td>' + fmtH(s['上周加班工时']) + '</td><td>累计加班工时（签字报表上周）</td></tr>' +
    '</tbody></table></div>';

  // 柱状图 (放在明细表格下面)
  html += '<div class="chart-wrap"><h3>&#x1F4CA; ' + sub.name + ' - 指标总览</h3>' +
    '<div style="position:relative; height:280px;"><canvas id="subDeptChart"></canvas></div></div>';

  // 顺序: cards → table → chart
  main.innerHTML = html;

  setTimeout(function() {
    var schedVal = parseFloat(s['排班']['排班率']);
    var correctVal = parseFloat(s['排班正确']['正确率']);
    var hubVal = parseFloat(s['HUB']['正确率']);
    var punchVal = parseFloat(s['打卡率']['打卡率']);

    drawBarChart('subDeptChart', {
      data: {
        labels: ['排班率', '排班正确率', 'HUB正确率', '打卡率'],
        datasets: [{
          label: sub.name,
          data: [schedVal, correctVal, hubVal, punchVal],
          backgroundColor: [
            schedVal >= 100 ? chartColors.green : schedVal >= 90 ? chartColors.yellow : chartColors.red,
            correctVal >= 90 ? chartColors.green : correctVal >= 50 ? chartColors.yellow : chartColors.red,
            hubVal >= 90 ? chartColors.green : hubVal >= 50 ? chartColors.yellow : chartColors.red,
            punchVal >= 90 ? chartColors.green : punchVal >= 50 ? chartColors.yellow : chartColors.red,
          ],
          borderRadius: 6,
          borderColor: 'rgba(0,0,0,0.08)',
          borderWidth: 1,
        }]
      },
      legend: false,
      yMax: 105
    });
  }, 100);
}

// ========== Drill-down Modal ==========
function openDrill(id) {
  var entry = drillStore.get(id);
  if (!entry) return;
  showDrilldown(entry.title, entry.employees);
}

function showDrilldown(title, employees) {
  document.getElementById('modalTitle').textContent = '\uD83D\uDCCA ' + title;
  var body = document.getElementById('modalBody');

  if (!employees || employees.length === 0) {
    body.innerHTML = '<div class="empty">暂无数据</div>';
  } else {
    var baseKeys = ['工号', '姓名', '三级部门', '四级部门', '五级部门'];
    var preferredOrder = ['班次名称', '班次上班时间', '班次下班时间', '首打卡时间', '末打卡时间', '超8H小时', '缺卡数', '班次内打卡次数', '标准打卡数', '是否排班正确', '是否排班'];
    var sample = employees[0];
    var extraKeys = [];
    for (var k in sample) {
      if (baseKeys.indexOf(k) === -1) extraKeys.push(k);
    }
    extraKeys.sort(function(a, b) {
      var idxA = preferredOrder.indexOf(a);
      var idxB = preferredOrder.indexOf(b);
      if (idxA === -1 && idxB === -1) return a.localeCompare(b);
      if (idxA === -1) return 1;
      if (idxB === -1) return -1;
      return idxA - idxB;
    });
    var allKeys = baseKeys.concat(extraKeys);

    var html = '<div class="summary-line">共 <strong>' + employees.length + '</strong> 人</div>';
    html += '<table><thead><tr>';
    allKeys.forEach(function(k) { html += '<th>' + k + '</th>'; });
    html += '</tr></thead><tbody>';

    employees.forEach(function(emp) {
      html += '<tr>';
      allKeys.forEach(function(k) {
        html += '<td>' + (emp[k] !== undefined ? emp[k] : '') + '</td>';
      });
      html += '</tr>';
    });

    html += '</tbody></table>';
    body.innerHTML = html;
  }

  document.getElementById('modalOverlay').classList.add('show');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('show');
}

document.getElementById('modalOverlay').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeModal();
});

// ========== Initialize ==========
renderSidebar();
showView('overview');
</script>
</body>
</html>"""

HOMEPAGE_FILE = os.path.join(WORKSPACE, "考勤首页.html")

# ============================================================
# 替换占位符 & 输出
# ============================================================
html = html_template.replace('__DATA_JSON__', data_json)
html = html.replace('__FEISHU_URL__', FEISHU_URL)

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML报告已生成: " + OUTPUT_FILE)
print("文件大小: " + str(round(os.path.getsize(OUTPUT_FILE) / 1024, 1)) + " KB")

# 生成大区独立报告
regions = ['FL 佛州大区', 'TX 德州大区', 'GL 大湖大区', 'WE 美西大区', 'MS 中南大区', 'NE 东北大区', 'Ground项目部']
for dept in data['departments']:
    if dept['name'] in regions:
        region_data = {
            'meta': {
                'total_employees': dept['summary']['total'],
                'date_range': data['meta']['date_range'],
                'department_count': 1,
            },
            'overview': dept['summary'],
            'departments': [dept],
        }
        region_json = json.dumps(region_data, ensure_ascii=True)
        region_html = html_template.replace('__DATA_JSON__', region_json)
        region_html = region_html.replace('__FEISHU_URL__', FEISHU_URL)
        region_html = region_html.replace('<title>考勤管理数据分析报告</title>', '<title>考勤分析 - ' + dept["name"] + '</title>')
        region_filename = os.path.join(WORKSPACE, '考勤分析_' + dept["name"] + '.html')
        with open(region_filename, 'w', encoding='utf-8') as f:
            f.write(region_html)
        print("大区报告生成: " + region_filename)

# ============================================================
# 首页改为直接使用全览报告
# ============================================================
import shutil
idx_file = os.path.join(WORKSPACE, "index.html")
report_html = os.path.join(WORKSPACE, "考勤分析报告.html")
shutil.copy(report_html, idx_file)
print("index.html 已同步为全览报告")

print("完成!")
