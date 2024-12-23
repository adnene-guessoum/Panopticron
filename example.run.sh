#!/bin/bash

cd /home/{path/to/project}/Panopticron || exit
docker build -t panopticron .
docker run --rm -v "$(pwd)/logs:/app/logs" --env-file ./.env panopticron
