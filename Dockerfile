FROM python:3 as otto
MAINTAINER m@rkis.cc
WORKDIR /app
EXPOSE 8001
ADD ./requirements.txt /app/requirements.txt
ADD ./setup.py /app/setup.py
RUN pip install -r requirements.txt
RUN pip install .
RUN apt-get install libmagickwand-dev
ADD . /app
ENTRYPOINT [ "python3" ]
CMD [ "-m", "otto.app" ]
