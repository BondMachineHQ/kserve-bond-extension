FROM python:3.9-slim-bullseye

LABEL org.opencontainers.image.source https://github.com/comp-dev-cms-ita/kserve-bond-serve

RUN pip install --no-cache-dir --upgrade pip && python3 -m pip install --no-cache-dir grpcio-tools   protobuf  kserve==0.9.0  ray[serve]==1.10.0

RUN apt update && apt-get install -y wget

COPY ./ bondmodel
RUN cd ./bondmodel && python3 -m pip install --no-cache-dir -e ./

#https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal
RUN wget https://raw.githubusercontent.com/protocolbuffers/protobuf/main/python/google/protobuf/internal/builder.py -O /usr/local/lib/python3.9/site-packages/google/protobuf/internal/builder.py


RUN useradd kserve -m -u 1000 -d /home/kserve
USER 1000
ENTRYPOINT ["python", "-m", "bondmodel"]