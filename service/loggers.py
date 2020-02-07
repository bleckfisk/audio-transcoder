import logging
from os import getcwd

"""
File for creating 1 logger per type of error / message that is created through the process.

AWS_Logger logs exceptions from Boto3 (ClientError).

Transcoder_Logger logs exceptions from Pydub (CouldntDecodeError, IndexError) 
as well as eventual unexpected exceptions. 

FFMPEG_logger logs all the processes done by FFMPEG
"""

exception_logfile = getcwd() + '/service/logging/exceptions.log'

AWS_Logger = logging.getLogger('AWS_Logger')
Transcoder_Logger = logging.getLogger('Transcoder_Logger')

f_handler = logging.FileHandler(exception_logfile)
f_handler.setLevel(logging.WARNING)

f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
f_handler.setFormatter(f_format)

AWS_Logger.addHandler(f_handler)
Transcoder_Logger.addHandler(f_handler)


FFMPEG_logfile = getcwd() + '/service/errorlogs/FFMPEG.log'
FFMPEG_logger = logging.getLogger("pydub.converter")

FFMPEG_logger.setLevel(logging.DEBUG)
FFMPEG_logger.addHandler(logging.FileHandler(FFMPEG_logfile))
