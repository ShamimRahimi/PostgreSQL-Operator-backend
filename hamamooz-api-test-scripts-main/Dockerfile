FROM hub.hamdocker.ir/python:3.12-slim
WORKDIR /app
COPY requirements.lock .
COPY pyproject.toml .
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED="true"
RUN pip install --no-cache-dir -r requirements.lock
COPY src/ .

ENTRYPOINT ["python", "cli.py"]