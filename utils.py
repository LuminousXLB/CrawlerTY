import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)-8s| %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='myapp.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)-8s| %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

logging.getLogger('').addHandler(console)


def getLogger(name, level=logging.NOTSET):
    logger = logging.getLogger('req')
    if level:
        logger.setLevel(level)
    return logger


if __name__ == "__main__":
    logger = getLogger('utils')
    logger.info("Hello world")
