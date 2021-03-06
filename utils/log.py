import logging

from settings import LOG_FILE

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)-8s| %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=str(LOG_FILE),
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)-8s| %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

logging.getLogger('').addHandler(console)


def getLogger(name, level=logging.NOTSET):
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(level)
    return logger


if __name__ == "__main__":
    logger = getLogger('utils')
    logger.info("Hello world")
