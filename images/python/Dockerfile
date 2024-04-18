FROM python:3.12-bookworm

WORKDIR /lcars

EXPOSE 1235 1234

ENV LCARS_CONTAINER=1
ENV LANG=de_DE.UTF-8
ENV LANGUAGE=de_DE.UTF-8

RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    apt update && apt install -y locales locales-all && \
    dpkg-reconfigure locales

COPY main.py /lcars/starter/main.py

CMD ["python3", "/lcars/starter/main.py"]

