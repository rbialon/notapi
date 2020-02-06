FROM python:3.8-slim

WORKDIR /app
EXPOSE 8000

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv gunicorn && pipenv install --deploy --system --ignore-pipfile

COPY app.py ./
COPY notapi ./notapi

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
