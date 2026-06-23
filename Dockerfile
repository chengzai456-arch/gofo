FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖（openpyxl 需要 xml 解析，Python slim 已包含）
# pandas 需要一些编译依赖，用预编译 wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py .
COPY run.py .
COPY static/ ./static/
COPY requirements.txt .

# 复制 pipeline 模块（从 skill 目录，构建时需将 skill 目录放在 build context 中）
# 构建命令：docker build --build-arg SKILL_DIR=./attendance-pipeline -t attendance-web .
ARG SKILL_DIR=./attendance-pipeline
COPY ${SKILL_DIR}/pipeline ./pipeline/
COPY ${SKILL_DIR}/config.py .
COPY ${SKILL_DIR}/scripts  ./scripts/

# 暴露端口
EXPOSE 8000

ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/app/pipeline

# 启动
CMD ["python", "run.py"]
