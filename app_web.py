from flask import Flask, render_template, url_for, request
from app_db import DB_ENGINE, rawcontents
from sqlalchemy import update
import logging
import zerorpc
import os

app = Flask(__name__)


BLOCK_LIST = [
    ('1179', '区块链星球'),
    ('develop', '经济论坛'),
    ('free', '天涯杂谈'),
    ('funinfo', '娱乐八卦'),
    ('worldlook', '国际观察')
]

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:8989")


@app.before_first_request
def init():
    with DB_ENGINE.connect() as conn:
        res = conn.execute("SELECT COUNT(*) FROM rawcontents")
        app.add_template_global(res.fetchone()[0], 'progress_total')
        res = conn.execute(
            "SELECT COUNT(*) FROM rawcontents WHERE tag IS NOT NULL")
        app.add_template_global(res.fetchone()[0], 'progress_done')


@app.route('/')
def hello_world():
    return block_list()


@app.route('/list')
def block_list():
    return render_template('block.html', block_list=BLOCK_LIST)


@app.route('/list/<string:blockid>')
def post_list(blockid):
    try:
        assert (blockid in [
            '1179',
            'develop',
            'free',
            'funinfo',
            'worldlook'
        ])
        with DB_ENGINE.connect() as conn:
            res = conn.execute('''
            SELECT p.pid, p.title, COUNT(rc.content) replycount, p.posttime, COUNT(rc.tag) tagcount 
            FROM posts p, replys r, rawcontents rc 
            WHERE p.blockid="{}" AND p.pid=r.pid AND rc.rid=r.rid 
            GROUP BY r.pid
            '''.format(blockid))
            return render_template('list.html', post_list=res)
    except AssertionError:
        return "Boom", 400


@app.route('/post/<int:pid>')
def post_detail(pid):
    try:
        pid = int(pid)
        with DB_ENGINE.connect() as conn:
            post = conn.execute('''
            SELECT pid, blockid, title, pageurl, clickcount, replycount, activityuserid 
            FROM posts 
            WHERE pid={}
            '''.format(pid)).fetchone()

            replyres = conn.execute('''
            SELECT r.rid, hostid, posttime, r.content, upCount, shang, totalScore, tag 
            FROM replys r, rawcontents rc WHERE pid={} AND r.rid=rc.rid
            '''.format(pid)).fetchall()
            return render_template('detail.html', post=post, replys=replyres, lastpid=pid-1, nextpid=pid+1)
    except AssertionError:
        return "Pa", 400


@app.route('/reply/<int:pid>', methods=['POST'])
def reply_tag(pid):
    with DB_ENGINE.connect() as conn:
        transcation = conn.begin()
        try:
            for rid, tag in request.form.items():
                conn.execute(
                    update(rawcontents)
                    .where(rawcontents.c.rid == rid)
                    .values(tag=float(tag), assure=True)
                )

            transcation.commit()
        except:
            transcation.rollback()
            return 'failed'
        else:
            return 'success'


@app.route('/semi/detail')
def semi_detail():
    [i, cnt, content, rid, predict] = eval(
        os.popen('zerorpc tcp://127.0.0.1:8989 labelRequest')
        .read()
        .replace('connecting to "tcp://127.0.0.1:8989"', '')
    )

    content = '<br>'.join(content.split('\n'))
    print(rid, 'request')
    return render_template('semi-train.jinja', idx=i, cnt=cnt, content=content, rid=rid, predict=predict)


@app.route('/semi/label/<int:rid>', methods=['POST'])
def semi_label(rid):
    rid, tag = list(request.form.items())[0]
    [_, _, success] = eval(
        os.popen('zerorpc tcp://127.0.0.1:8989 label {} {}'.format(rid, tag))
        .read()
        .replace('connecting to "tcp://127.0.0.1:8989"', '')
    )
    print(rid, success)
    return success


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
