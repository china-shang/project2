#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logger import get_logger
logger = get_logger(__name__)


class BaseSpider(object):
    """
    execute crawl url
    """

    async def fetch(self, url):
        """
        fetch specific url'data
        """
        logger.info("start fetch")
    
    def close(self):
        pass
    
    def closed(self):
        pass

