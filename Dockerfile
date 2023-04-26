FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir "poetry==1.4.2"

RUN poetry config virtualenvs.create false && \
  poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
