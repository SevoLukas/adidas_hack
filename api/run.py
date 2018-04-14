from flask import Flask, request
from flask import jsonify
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


@app.route("/recommend", methods=["POST"])
def recommend_product():
    age = request.args.get('age')
    gender = request.args.get('gender')
    gender_code = 1 if gender == 'male' else 2
    accuracy = 100
    if gender_code == 1:
        product = 'BR6930'
    else:
        if age < 40:
            product = 'BY8745'
        else:
            product = 'CV9889'

    return jsonify({'product': product, 'accuracy': accuracy})


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
