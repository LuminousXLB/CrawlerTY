from crawler import handlePost
from settings import RUNTIME_RANGE, DATA_ROOT


if not DATA_ROOT.is_dir():
    DATA_ROOT.mkdir()


if __name__ == "__main__":
    for blockid, start, end in RUNTIME_RANGE:
        for postid in range(start, end+1):
            handlePost(blockid, postid)
