import logging.config

from config import config
from utils import get_path


# Check if the script is compiled with Nuitka
is_compiled = '__compiled__' in globals()
handlers = ['file'] if is_compiled else ['console', 'file']

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s '
                      '[%(filename)s:%(lineno)d]: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'detailed',
            'level': 'INFO',
            'filename': get_path('app.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': handlers,
            'level': 'DEBUG',
            'propagate': True,
        },
        'app_logger': {  # custom logger
            'handlers': handlers,
            'level': config.get('log_level', 'ERROR'),
            'propagate': False,
        },
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger('app_logger')

# Log messages at various severity levels
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
