FROM python:3 as base

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

FROM python:3-slim as otto

#ENTRYPOINT [ "python3" ]
#CMD [ "-m", "otto.app" ]
#WORKDIR /app

ENV MAGICK_HOME=/usr \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_CACHE_DIR="/var/cache/pip/"

# Wand dependency for image manipulation
RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache \
    --mount=type=tmpfs,target=/var/log \
    apt-get update && \
    apt-get install -y imagemagick

RUN --mount=type=cache,target=/var/cache \
    --mount=from=base,src=/app/dist/,target=/tmp \
    pip install /tmp/*.whl
