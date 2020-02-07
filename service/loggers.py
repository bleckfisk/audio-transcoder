import logging
from os import getcwd

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


ffmpeg_logfile = getcwd() + '/service/errorlogs/pydub_logs.log'
ffmpeg_logger = logging.getLogger("pydub.converter")

ffmpeg_logger.setLevel(logging.DEBUG)
ffmpeg_logger.addHandler(logging.FileHandler(ffmpeg_logfile))
