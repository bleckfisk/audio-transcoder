import logging
from os import getcwd

"""
File for creating 1 logger per type of error / message
that is created through the process.

AWS_Logger logs exceptions from Boto3 (ClientError).

Service_Logger logs exceptions from
Pydub (CouldntDecodeError, IndexError & KeyError)
as well as eventual unexpected exceptions.

FFMPEG_logger logs all the processes done by FFMPEG.
These are not exceptions, but can give insight if the
transcoding doesn't work or doesn't do as intended.
"""

exception_logfile = getcwd() + '/service/logging/exceptions.log'

AWS_Logger = logging.getLogger('AWS_Logger')
Service_Logger = logging.getLogger('Service_Logger')

f_handler = logging.FileHandler(exception_logfile)
f_handler.setLevel(logging.WARNING)

f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
f_handler.setFormatter(f_format)

AWS_Logger.addHandler(f_handler)
Service_Logger.addHandler(f_handler)


FFMPEG_logfile = getcwd() + '/service/logging/ffmpeg.log'
FFMPEG_logger = logging.getLogger("pydub.converter")

FFMPEG_logger.setLevel(logging.DEBUG)
FFMPEG_logger.addHandler(logging.FileHandler(FFMPEG_logfile))
