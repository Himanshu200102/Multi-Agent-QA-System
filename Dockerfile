# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
ENV PYTHONPATH=/app/src
CMD ["python","-m","qa_agents.run_test","--goal","Toggle Wi‑Fi off and on","--env","mock","--logs_dir","/app/logs"]
