FROM nginx:1.27.1-bookworm

RUN apt-get update && apt-get install -y tree vim python3 python3-pip python3-venv locales-all supervisor
RUN python3 -m venv /opt/browser

COPY browser/ /opt/browser/browser/
COPY com/ /opt/browser/com/
COPY filesystem/ /opt/browser/filesystem/
COPY static/ /opt/browser/static/
COPY templates/ /opt/browser/templates/
COPY manage.py /opt/browser/
COPY requirements.txt /opt/browser/
COPY default.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/

RUN cd /opt/browser/ && . bin/activate && pip install -r requirements.txt && deactivate
RUN mkdir /opt/browser/log/ && touch /opt/browser/log/supervisord.log && touch /opt/browser/log/nginx.log && touch /opt/browser/log/gunicorn.log