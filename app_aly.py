from crawler import handlePost, logger
import json
import time
from requests.exceptions import ConnectionError


def wrapper(blockid, postid, times=0):
    try:
        meta = handlePost(blockid, postid)
        if meta != None:
            with open('data/{}_{}.json'.format(blockid, postid), 'w') as f:
                json.dump(meta, f)
    except ConnectionError as err:
        logger.error(err.strerror)
        if times < 3:
            time.sleep(1+3*times)
            return wrapper(blockid, postid, times+1)
        else:
            raise


if __name__ == "__main__":
    # wrapper('1179', 9176)
    # for page in range(8789, 33150):
    # for page in range(20000, 28000):
        # wrapper('1179', page)

    for page in range(29750, 29752):
        wrapper('1179', page)

    # for page in range(20000, 24000):
    #     wrapper('1179', page)

    # for page in range(12000, 20000):
    #     wrapper('1179', page)
