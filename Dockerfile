FROM python:3.8

ARG VERSION

RUN pip install zyxelprometheus==$VERSION

ENTRYPOINT ["zyxelprometheus"]
CMD []
