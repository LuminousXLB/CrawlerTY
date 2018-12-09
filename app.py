from app_handle import handlePost

POST_RANGE = [
    ('1179', 8790, 33149),
    ('develop', 2303713, 2329332),
    ('free', 5935881, 5970215),
    ('funinfo', 7666313, 7690308),
    ('worldlook', 1849540, 1859166)
]

RUNTIME_RANGE = [
    # ('1179', 8790, 33149),
    ('develop', 2303713, 2329332),
    ('free', 5935881, 5970215),
    ('funinfo', 7666313, 7690308),
    ('worldlook', 1849540, 1859166)
]


if __name__ == "__main__":
    for blockid, start, end in RUNTIME_RANGE:
        for postid in range(start, end+1):
            handlePost(blockid, postid)
