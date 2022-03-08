FROM python:3.10

ARG VERSION

#RUN pip install zyxelprometheus==$VERSION

WORKDIR /opt/zyxelprometheus

COPY requirements.txt /opt/zyxelprometheus
RUN pip install --no-cache-dir -r requirements.txt

COPY bin/zyxelprometheus bin/
COPY zyxelprometheus zyxelprometheus

ENV PYTHONPATH "${PYTHONPATH}:/opt/zyxelprometheus/zyxelprometheus"


ENTRYPOINT ["bin/zyxelprometheus"]
CMD ["-d"]
