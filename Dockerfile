FROM python:3.7

ENV PYTHONUNBUFFERED 1

ARG PIPENV_ARGS

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get update \
    && pip3 install --no-cache-dir -U pip pipenv \
    && pipenv install --system --deploy --dev

# Install Pydub
RUN pipenv install pydub

# Install FFMPEG 
RUN apt-get update && apt-get -y install ffmpeg libavcodec-extra

CMD ["python", "-m", "service"]
