FROM python:3.13.9-slim

WORKDIR /docker

COPY ./requirements.txt /docker/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /docker/requirements.txt

COPY ./ /docker/

WORKDIR /docker/backend

CMD ["uvicorn", "main:app", "--ssl-certfile", "../cert.pem", "--ssl-keyfile", "../key.pem"]