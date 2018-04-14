from flask import Flask, request
from api.settings import HOST, PORT, DEBUG
from helpers.resizer import resize_and_upload

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/resize", methods=["GET"])
def resize_api():
    url = request.args.get('url')
    face_id = request.args.get('face_id')
    height = request.args.get('height')
    width = request.args.get('width')
    top = request.args.get('top')
    left = request.args.get('left')

    resize_and_upload(url, face_id, height, width, top, left)
    return 'ok'


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
