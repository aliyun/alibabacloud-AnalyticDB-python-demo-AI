# Copyright @ 2020 Alibaba. All rights reserved.
import yaml
import os
from StringIO import StringIO
import traceback
from logger import logger

CONFIG = None
app_config_str = os.environ.get('APP_CONFIG')
if app_config_str:
    try:
        print "Load config from environment"
        CONFIG = yaml.safe_load(StringIO(app_config_str))
    except Exception as e:
        logger.error(traceback.format_exc())

if not CONFIG:
    CONFIG = yaml.safe_load(open(os.path.dirname(__file__) + '/config/config.yml'))