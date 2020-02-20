#! /usr/bin/env bash

sudo apt-get update && apt-get -y install ffmpeg libavcodec-extra
sudo pip install --upgrade pip && sudo pip install pipenv awscli boto3
sudo pipenv install --system --deploy --dev