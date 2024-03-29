from os import environ as env

AWS_SQS_ENDPOINT_URL = env.get("AWS_SQS_ENDPOINT_URL")
REQUEST_QUEUE_NAME = env.get("REQUEST_QUEUE_NAME")
AWS_S3_ENDPOINT_URL = env.get("AWS_S3_ENDPOINT_URL")
AWS_SNS_ENDPOINT_URL = env.get("AWS_SNS_ENDPOINT_URL")
RESPONSE_TOPIC_ARN = env.get("RESPONSE_TOPIC_ARN")
AWS_DEFAULT_REGION = env.get("AWS_DEFAULT_REGION")
AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")


"""
This ffmpeg_logging variable is a switch
to turn the encode/decode logging on and off.

True = ON
False = OFF

Default = OFFs
"""
ffmpeg_logging = False
