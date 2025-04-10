FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["/venv/bin/daphne", "-b", "0.0.0.0", "-p", "8000", "bu_search.asgi:application"]
