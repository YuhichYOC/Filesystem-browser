FROM nginx:1.27.1-bookworm

RUN apt-get update && apt-get install -y tree vim python3 python3-pip python3-venv locales-all supervisor

COPY default.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/

RUN python3 -m venv /opt/venv
COPY requirements.txt /opt/venv/
RUN cd /opt/venv/ && . bin/activate && pip install -r requirements.txt && deactivate