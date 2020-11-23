FROM python:3 as otto
MAINTAINER m@rkis.cc
WORKDIR /otto
EXPOSE 8001
ADD ./requirements.txt /otto/requirements.txt
ADD ./setup.py /otto/setup.py
RUN pip install -r requirements.txt
RUN pip install .
RUN apt-get install libmagickwand-dev
ADD . /otto
ENTRYPOINT [ "python3" ]
CMD [ "-m", "otto.app" ]
