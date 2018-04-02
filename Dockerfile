FROM python:2

WORKDIR /usr/src/app

RUN pip install supervisor; mkdir /var/log/supervisord

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8080
CMD [ "supervisord", "-n", "-c", "supervisord.conf" ]
