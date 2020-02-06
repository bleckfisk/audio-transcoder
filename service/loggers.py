import logging
from os import getcwd
file_directory = getcwd() + '/errorlogs/logs.log'


AWS_Logger = logging.getLogger('AWS_Logger')
Transcoder_Logger = logging.getLogger('Transcoder_Logger')

f_handler = logging.FileHandler(file_directory)
f_handler.setLevel(logging.WARNING)

f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
f_handler.setFormatter(f_format)

AWS_Logger.addHandler(f_handler)
Transcoder_Logger.addHandler(f_handler)
