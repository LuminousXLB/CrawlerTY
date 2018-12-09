from app_handle import handlePost
from settings import RUNTIME_RANGE


if __name__ == "__main__":
    for blockid, start, end in RUNTIME_RANGE:
        for postid in range(start, end+1):
            handlePost(blockid, postid)
