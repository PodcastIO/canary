FROM python:3.9.13-buster as base
SHELL ["/bin/bash", "-c"]
WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN python -m venv ./venv \
    && source venv/bin/activate \
    && pip install  -r requirements.txt --no-dependencies \
    && pip install paddlepaddle==2.2.2 -i https://mirror.baidu.com/pypi/simple


FROM base as server
WORKDIR /usr/src/app
COPY ./ ./
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh server


FROM base as job
ARG JOB
ENV JOB ${JOB}
SHELL ["/bin/bash", "-c"]
WORKDIR /usr/src/app
COPY ./ ./
RUN set -x; source venv/bin/activate \
    && apt update -y \
    && apt install ffmpeg calibre ttf-wqy-microhei ttf-wqy-zenhei -y \
    && python -m playwright install \
    && chmod +x ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh rq --name=${JOB}



FROM base as scheduler
WORKDIR /usr/src/app
COPY ./ ./
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh scheduler


