FROM python:3.9-slim-bullseye

LABEL org.opencontainers.image.source https://github.com/comp-dev-cms-ita/kserve-bond-serve

RUN pip install --no-cache-dir --upgrade pip && python3 -m pip install --no-cache-dir grpcio-tools

COPY ./ bondmodel
RUN pip install --no-cache-dir --upgrade pip \
       && python3 -m pip install --no-cache-dir -e ./bondmodel

RUN useradd kserve -m -u 1000 -d /home/kserve
USER 1000
ENTRYPOINT ["python", "-m", "bondmodel"]