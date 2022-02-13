import logging

logger = logging.getLogger(__name__)


def logger_share_text(share_text):
    logger = logging.getLogger('share_text')
    logger.info(share_text)
