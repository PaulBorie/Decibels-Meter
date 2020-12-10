# Decibels-Meter

Program sending location and sound level to google cloud iot core using MQTT protocol.

## Instructions

* Docker installed on your machine. https://docs.docker.com/engine/install/ubuntu/
* Update the configuration file config.env with your device name.
* Build the image: ```docker build --pull --rm -f "Dockerfile" -t decibelsmeter:latest .```
* Run the image: ```docker run --rm -it --device /dev/snd:/dev/snd  --env-file config.env --mount source=dbmetervol,target=/home/decibelsmeter/data decibelsmeter:latest```
