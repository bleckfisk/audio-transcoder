# Audio Transcoder

## About

This Transcoder is a software that lets you transcode audio files between a variety of formats.
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
 
    ```git clone https://github.com/bleckfisk/audio-transcoder```

 ### For Dev and Local Testing
 - If needed, edit AWS related environment variables in ```docker-compose.yml``` file to fit your needs.
    - Note: If you are running the transcoder outside of docker, make sure AWS Environment variables are set on your machine or set them in the ```service/settings.py``` file. 
    - Note 2: When using Localstack, ```AWS_ACCESS_KEY_ID``` and ```AWS_SECRET_ACCESS_KEY``` is not actually validated so these can be set to anything. A good practice is to name them test, for the sake of clarity. 
 
 - Run the setup command. 
    ```make setup```
 
  - This will build the transcoder and localstack, test the transcoder and then run it, leaving it on for use. 
  - When transcoder-container is up it will directly start looking for messages in SQS Queue and is by then ready to be used.
    
 - If you have turned the containers off with ```docker-compose down``` or ```stop```, you can start them again with ```make run```

 #### Additional shorthandss
  - ```make localstack```: Runs the localstack container.
  - ```make transcoder```: Runs the transcoder container. 
  - ```make test```: Runs the localstack container and then runs the tests for transcoder.
  
    - There is currently an issue with running the tests while another transcoder container is up. If your tests fails, try to shut the currently running transcoder container before running this command. 
    
  - ```make coverage```: Runs localstack and all tests for transcoder while additionally reporting code coverage in terminal.  
  - ```make build```: Builds the transcoder but doesn't run it. 
  
  ### For Production Environment
  
These steps can be done in a multiple ways depending on how your production environment is set up. These steps go through the basics that is needed (correct credentials and a running docker container) but please make adjustments based on your needs. If you intend to add or edit code to get the transcoder working on your production environment, feel free to fork the repository and make changes accordingly.  
  
  - Make sure environment has access to the following environment variables set with correct values.
    ```REQUEST_QUEUE_NAME```: Name of the queue the transcoder should start looking for messages in once running. \
    ```RESPONSE_TOPIC_ARN```: ARN of the Topic where the transcoder should publish the status of the executed job. \
    ```AWS_ACCESS_KEY_ID```: Your AWS Access Key ID \
    ```AWS_SECRET_ACCESS_KEY```: Your AWS Secret Access Key \
    ```AWS_DEFAULT_REGION```: The region you want Boto3 to default to as the transcoder doesn't contain any hard coded regions. 

    - Boto3 will default to the actual endpoints of AWS if the endpoint variables are unset which means that endpoints shouldn't be needed in production.  

  - cd into project folder and build Transcoder Image from Dockerfile
    ```docker build .```

  - Create Container from Image
    ```docker create audio-transcoder``` 

  - Run Container
    ```docker run audio-transcoder```

  - When transcoder-container is up it will directly start looking for messages in SQS Queue and is by then ready to be used.
  
## How To Use
  - Make sure SQS Queue Name and SNS Topic Name in environment variables or settings-file are correct.
  - Make sure transcoder container is running.
  - Send message to SQS Queue containing supported data.
  
``` 
  - supported data = {
      "id": "unique session identification string to separate processes, chosen of your liking",
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
    
- After transcoder has processed the message and done the job, it will publish an object-string like below to the given SNS Topic.

```
callback = {
  "id": "unique identification string of your choice accoring to message",
  "status": "a string containing either success or error depending on exceptions during the job",
  "errors": None or {Message]}, allowing you to see your message and control it. 
}
```

## Supported Formats
 - Following formats can be decoded (supported as inputs)
   - WAV, FLAC, MP3, AIFF, AAC, OGG, OPUS, WMA, FLV, OGV, AC3
 - Following formats can be encoded (suppoted as outputs)
   - WAV, FLAC, MP3, AIFF
  
 - This software uses FFMPEG with libavcodec to decode and encode files. Visit their website for full information about the codec and what it supports. If you need support, you can either support a pull request providing it or fork the repository and add it in your repository.
   - https://ffmpeg.org/documentation.html

