from app_handle import handlePost

POST_RANGE = [
    ('1179', 8790, 33149),
    ('develop', 2303713, 2329332),
    ('free', 5935881, 5970215),
    ('funinfo', 7666313, 7690308),
    ('worldlook', 1849540, 1859166)
]

RUNTIME_RANGE = [
    ('worldlook', 1857780, 1859166)
]


if __name__ == "__main__":
    # [2018-12-05 13:04:25] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-1179-14025-2.shtml
    # [2018-12-05 18:37:24] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-1179-17830-1.shtml
    # handlePost('develop', 2314235) # Not Solved
    # handlePost('develop', 2324112) # Not Solved
    # [2018-12-06 13:58:02] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-develop-2314196-1.shtml
    # [2018-12-06 17:37:14] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-develop-2314721-1.shtml
    # [2018-12-06 23:03:23] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-develop-2323208-1.shtml
    # [2018-12-07 00:29:44] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-free-5937375-1.shtml
    # [2018-12-07 00:50:12] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-free-5939757-1.shtml
    # [2018-12-07 04:51:11] CRITICAL| parser: Return 500 from GET http://bbs.tianya.cn/post-free-5966593-1.shtml

    for blockid, start, end in RUNTIME_RANGE:
        for postid in range(start, end+1):
            handlePost(blockid, postid)
