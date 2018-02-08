#! /usr/bin/env python

import logging

logger = logging.getLogger('moss')
logger.setLevel(logging.INFO)

try:
    handler = logging.FileHandler('output/messages.log')
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except IOError:
    pass


def log(message):
    logger.info(message)
