FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY . .

RUN pip install -r requirement.txt

CMD ["python", "manage.py", "runserver"]