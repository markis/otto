FROM python:3.12 AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_CACHE_DIR="/var/cache/pip/"

WORKDIR /app
COPY pyproject.toml /app/
COPY otto/ /app/otto/

RUN --mount=type=cache,target=/var/cache \
    pip install --upgrade build==0.10.0 && \
    python -m build

FROM python:3.12-slim AS otto

#ENTRYPOINT [ "python3" ]
#CMD [ "-m", "otto.app" ]
#WORKDIR /app

# Wand dependency for image manipulation
ENV MAGICK_HOME=/usr
RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache \
    --mount=type=tmpfs,target=/var/log \
    apt-get update && \
    apt-get install -y imagemagick build-essential cmake gcc ninja-build \
      libharfbuzz-dev \
      libfreetype6 \
      fonts-freefont-ttf \
      libasound2 \
      libxcomposite1 \
      libxdamage1 \
      libxfixes3 \
      libxrandr2 \
      libxtst6 \
      libatk1.0-0 \
      libdbus-glib-1-2 \
      libdbus-1-3 \
      libx11-xcb1 \
      libxcursor1 \
      libxi6 \
      libgtk-3-0

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_CACHE_DIR="/var/cache/pip/"

RUN --mount=type=cache,target=/var/cache \
    --mount=from=base,src=/app/dist/,target=/tmp \
    pip install /tmp/*.whl

RUN playwright install firefox
