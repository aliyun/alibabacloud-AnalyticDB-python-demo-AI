# Copyright @ 2020 Alibaba. All rights reserved.
#-*- coding:utf8 -*-

'''
Usage example as follows:

import APILogging

APILogging.logger.debug('xxx')
APILogging.logger.info('xxx')
APILogging.logger.warning('xxx')
APILogging.logger.error('xxx')
'''

import logging
import logging.config
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
## end if
LOG_FILE = "api.log"
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][%(filename)s:%(lineno)d:%(funcName)s][%(levelname)s] %(message)s',
        },
    },

    "handlers": {
        "default": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": LOG_DIR + "/" + LOG_FILE,
            'mode': 'a',
            "maxBytes": 1024*1024*20,  # 20 MB per log file
            "backupCount": 1,	   # keep 10 files, remove earlist more than 10 files
            "encoding": "utf-8"
        },
    },

    "root": {
        'handlers': ['default'],
        'level': "INFO",
        'propagate': False
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger()

if __name__ == '__main__':
    logger.info(sys.argv[1])
