FROM python:3.6.1
ENV APP /SignageData
ENV FLASK_ENV production


RUN mkdir $APP
WORKDIR $APP


EXPOSE 5000


COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install uwsgi

COPY . .


CMD ["uwsgi","--ini","app.ini"]

