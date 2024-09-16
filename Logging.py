import sys

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s #%(levelname)-8s %(filename)s:'
                   '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_0': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(message)s'
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
            },
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'WARNING',
            'stream': sys.stdout
            }
        },
    'loggers': {
        'Functions': {
            'level': 'DEBUG',
            'handlers': ['stdout']
        },
        'Classes': {
            'level': 'DEBUG',
            'handlers': ['stdout']
            }
    },
    'root': {
        'formatter': 'default',
        'handlers': ['default']
    }
}
