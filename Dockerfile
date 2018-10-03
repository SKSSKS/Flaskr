FROM python:3.6-alpine

RUN adduser -D blog

WORKDIR /home/microblog

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip3 install -r requirements.txt

COPY flaskr flaskr
COPY run.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP run.py

RUN chown -R blog:blog ./
USER blog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
