import logging

# 中途半端に設定すると余計なログがたくさん表示されるので一旦パス
# logging.basicConfig(
#     level=logging.ERROR,  # ここで指定したレベル以上のログが出力される
#     # filename='logging_sample/sample01.log',
#     # filemode='w',
#     format='%(asctime)s-%(process)s-%(levelname)s-%(message)s'
# )


logger = logging.getLogger(__name__)


def logger_share_text(share_text):
    logger = logging.getLogger('share_text')
    # logger.debug(share_text)  # 表示されない
    logger.info(share_text)
    # logger.warning(share_text)
    # logger.error(share_text)
    # logger.critical(share_text)
