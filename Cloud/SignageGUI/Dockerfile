FROM python:3.6.1
ENV APP /SignageGUI

RUN mkdir $APP
WORKDIR $APP


EXPOSE 8050


COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .



CMD ["uwsgi","--ini","app.ini"]

