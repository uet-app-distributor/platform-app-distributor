FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service_account.json

RUN pip install -r requirement.txt

CMD ["python", "manage.py", "runserver"]