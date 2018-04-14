import aiopg
import asyncpg
from flask import Flask, request
from quart import Quart, websocket
from api.settings import HOST, PORT, DEBUG, DB_USER, DB_PASS, DB_NAME, DB_HOST, DB_PORT
from helpers.resizer import resize_and_upload

app = Quart(__name__)


@app.route("/")
async def hello():
    print('in hello')
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    await conn.fetch("SELECT 1")
    print('we have connection')
    conn.close()

    return "Fuck you in the ass!"


@app.route("/resize", methods=["GET"])
async def resize_api():
    url = request.args.get('url')
    face_id = request.args.get('face_id')
    height = request.args.get('height')
    width = request.args.get('width')
    top = request.args.get('top')
    left = request.args.get('left')

    await resize_and_upload(url, face_id, height, width, top, left)
    return 'ok'

dsn = 'dbname=AllYourFaces user=hackmaster password=HackMaster66 host=http://adidashack.chdkvmsgas9w.us-east-1.rds.amazonaws.com/'


@app.route("/go")
async def go():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            ret = []
            async for row in cur:
                ret.append(row)
            assert ret == [(1,)]

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
