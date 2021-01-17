FROM python:3-alpine as otto
MAINTAINER m@rkis.cc
ENTRYPOINT [ "python3" ]
CMD [ "-m", "otto.app" ]
WORKDIR /app
EXPOSE 8001

# Wand dependency for image manipulation
RUN apk add imagemagick

# Install pip dependencies and avoid
# docker layer caching invalidation
ADD ./requirements.txt /app/
RUN apk add build-base && \
    pip install --no-cache --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    apk del build-base

ADD . /app
