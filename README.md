# Bleck Audio Transcoder (Under Development)

## About

Bleck Audio Transcoder is a software that lets you transcode audio files between wide variety of formats.
It is built with Amazon Web Services Infrastructure in mind and listens to SQS Queue for jobs to 
be done and reports back to SNS Topic with information of whether or not the job succeeded or not.

### Requirements

 - Docker
 - Docker-Compose
 - Amazon Web Services Account with use of SQS, SNS and S3. 

### Dependencies
#### Handled by Pipenv (Pipfile)

  - Pydub (https://github.com/jiaaro/pydub)
  - Localstack (https://github.com/localstack/localstack)
  - Boto3 (https://github.com/boto/boto3)
  - Pytest (https://github.com/pytest-dev/pytest)
  - Pytest-cov (https://github.com/pytest-dev/pytest-cov)
  - Coverage (https://github.com/nedbat/coveragepy)

#### Handled by Docker (Dockerfile)
  - FFMPEG + libavcodec (https://github.com/FFmpeg/FFmpeg)


## Installation & Setup
 - Clone Repository to machine that should run the docker container
 
    ```git clone https://github.com/brorssonoskar/bleck-audio-transcoder```

 ### For Dev and Local Testing
 - Edit AWS related environment variables in ```docker-compose.yml``` file to fit your needs.
    - Note: If you are running the transcoder outside of container, make sure AWS Environment variables are set or set them in the ```service/settings.py``` file. 
 
 - Build Transcoder Image and Container
 
    ```make build```

 - Run Localstack

    ```docker-compose up localstack```  
        - If you want it detached, add ```-d``` before localstack.
 

 - Run Tests for Bleck Audio Transcoder

    ```make test```

 - Run Bleck Audio Transcode Container

    ```docker-compose up -d transcoder```
    
  - When transcoder-container is up it will directly start looking for messages in SQS and is by then ready to be used.
    
  - If you after entering AWS Environment Variable want to do the docker-compose process in one command, you can enter ```make setup```. 

  ### For Production Environment
  - Make sure environment has access to the following environment variables set with correct values. This can be done in a multiple ways depending on how your production environment is set up.
    ```AWS_SQS_QUEUE_NAME```
    ```AWS_SNS_TOPIC_ARN```
    ```AWS_ACCESS_KEY_ID```
    ```AWS_SECRET_ACCESS_KEY```
    ```AWS_DEFAULT_REGION```

    - Boto3 will in the files try to reach AWS Service Endpoints (for reference: https://github.com/brorssonoskar/bleck-audio-transcoder/blob/e8cac9deb74f3ef0bb2d3ad5483440d6dc113871/service/aws_boto3.py#L18). When these are unset, it will instead target real AWS, and therefore the variables are not needed in production. 

  - Build Transcoder Image from Dockerfile
    ```docker build .```

  - Create Container from Image
    ```docker create bleckfisk/audiotranscoder``` 

  - Run Container
    ```docker run bleckfisk/audiotranscoder```

## How To Use
  - Make sure SQS Queue Name and SNS Topic Name in environment variables or settings-file are correct.
  - Make sure transcoder container is running.
  - Send message to SQS Queue containing supported data.
  
``` 
  - supported data = {
      "input": {
        "key": "s3 bucket key to download",
        "bucket": "bucket name where s3 key exists" 
      },
      "outputs": [
        {
        "key": "what uploaded key should be called when placed on s3 bucket",
        "format": "what format the file should be transcoded into",
        "bucket": "bucket name where result should be placed"
        },
        {
          # Any number of output objects can be placed in the outputs-list
        }
      ]
    }
```
    
- Please observe that SQS Messages Body can only contain strings, transcoder will parse the string to json and handle it accordingly. 
    
- After transcoder has processed the message and done the job, it will publish an object like below to the given SNS Topic.

```
callback = {
  "from": {the input data that was sent to the transcoder},
  "to": {the output data that was sent to the transcoder},
  "status": "a string containing either success or error depending on exceptions during the job",
  "errors": None or {[errormessage]}, dending on exceptions during the job. 
}
```
