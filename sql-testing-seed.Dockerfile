# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

FROM python:3.14-trixie@sha256:7453da3728d84ba6db8446a597ca40bc088a2034c19f2f0ec3d1b41e7dfb0519 AS builder

WORKDIR /build

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN uv export --frozen --no-hashes --no-dev --output-file requirements.lock

RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.lock
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels --no-deps .

RUN curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xEE4D7792F748182B" \
        | gpg --dearmor -o /build/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
        https://packages.microsoft.com/debian/13/prod trixie main" \
        > /build/mssql-release.list


FROM python:3.14-slim-trixie@sha256:af8a5aa14780025dbfbcfbc81bd8a91ebd87711dd5b0f48ed71090949dd7cb1d

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Applies bundled SQL seeds to a target SQL Server for MEx integration tests."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-testing"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV MEX_TESTING_SQL_SEED_DIRECTORY=/app/seeds

WORKDIR /app

COPY --from=builder /build/wheels /wheels

RUN pip install --no-cache-dir \
    --no-index \
    --find-links=/wheels \
    /wheels/*.whl \
    && rm -rf /wheels

COPY --from=builder /build/microsoft-prod.gpg /usr/share/keyrings/microsoft-prod.gpg
COPY --from=builder /build/mssql-release.list /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

COPY seeds/ /app/seeds/

USER 10001

ENTRYPOINT [ "seed" ]
