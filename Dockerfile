FROM nginx:latest

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv locales-all supervisor

COPY default.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/

RUN mkdir /opt/filesystem/ && python3 -m venv /opt/filesystem/venv
COPY requirements.txt /opt/filesystem/venv/
RUN cd /opt/filesystem/venv/ && . bin/activate && pip install -r requirements.txt && deactivate