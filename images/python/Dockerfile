FROM python:3.13-%codename%

WORKDIR /lcars

EXPOSE 1235 1234

ENV LCARS_CONTAINER=1
ENV LANG=de_DE.UTF-8
ENV LANGUAGE=de_DE.UTF-8
ENV PYTHONPATH=/lcars/lib:/lcars/lib2

RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    apt update && apt install -y locales locales-all iproute2 && \
    dpkg-reconfigure locales

RUN pip install aiofiles aiohttp docker pyyaml pydantic netaddr aioretry psutil

COPY main.py /lcars/starter/main.py
COPY health_check.py /lcars/starter/health_check.py
COPY update.py /lcars/starter/update.py
COPY run.py /lcars/starter/run.py

HEALTHCHECK --interval=1m --timeout=30s --start-period=2m \
            CMD python3 /lcars/starter/health_check.py

LABEL pro.holler.lcars.python=true
LABEL com.centurylinklabs.watchtower.enable=false

CMD ["python3", "/lcars/starter/main.py"]

