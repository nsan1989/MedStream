FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m django

WORKDIR /app

COPY med_stream/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY med_stream/ /app/

RUN mkdir -p /app/staticfiles /app/media

RUN chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "med_stream.wsgi:application", "--bind", "0.0.0.0:8000"]