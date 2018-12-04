SELECT date(posttime), blockid, COUNT(postid), AVG(length) FROM posts GROUP BY date(posttime), blockid;
SELECT date(resttime), blockid, COUNT(replyid), AVG(length) FROM replys GROUP BY date(resttime), blockid;

SELECT posts.postid, posts.blockid, posttime, strftime('%s', resttime) - strftime('%s', posttime)
    FROM posts, replys
    WHERE posts.postid = replys.postid;
