from crawler import handlePost, logger
import json
import time
from requests.exceptions import ConnectionError, ChunkedEncodingError


def wrapper(blockid, postid, times=0):
    try:
        meta = handlePost(blockid, postid)
        if meta != None:
            with open('data/{}_{}.json'.format(blockid, postid), 'w') as f:
                json.dump(meta, f)
    except (ConnectionError, ChunkedEncodingError) as err:
        logger.error(err.strerror)
        if times < 3:
            time.sleep(1+3*times)
            return wrapper(blockid, postid, times+1)
        else:
            raise


if __name__ == "__main__":
    # wrapper('worldlook', 1849538)
    for page in range(1849538, 1859167):
        wrapper('worldlook', page)