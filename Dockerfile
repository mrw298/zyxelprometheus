FROM python:3.10

ARG VERSION

RUN pip install zyxelprometheus==$VERSION

ENTRYPOINT ["zyxelprometheus"]
CMD ["-d"]
