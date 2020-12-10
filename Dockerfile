FROM alpine:3.12

WORKDIR /home/decibelsmeter/

COPY requirements.txt ./
RUN apk update && \
    apk add --no-cache \ 
    g++ \
    linux-headers \
    openssl \
    portaudio \
    portaudio-dev \ 
    alsa-plugins-pulse \
    python3 \
    py3-pip \
    py3-numpy \
    py3-scipy \
    py3-cryptography \
    py3-google-api-python-client && \
    pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir --no-deps -r requirements.txt

COPY app/ ./app
COPY scripts/generate_keys.sh ./scripts/generate_keys.sh

CMD [ "python3", "app" ]