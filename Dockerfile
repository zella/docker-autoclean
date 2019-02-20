FROM python:3.7

MAINTAINER zella <drumirage@gmail.com>

COPY autoclean.py requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "autoclean.py" ]