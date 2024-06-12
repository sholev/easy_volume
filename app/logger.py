import os
import logging.config

from config import config

PATH = os.path.join(os.path.dirname(__file__), 'app.log')

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
            'filename': PATH,
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app_logger': {  # custom logger
            'handlers': ['console', 'file'],
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
