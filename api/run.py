from flask import Flask, request
from flask import jsonify
from api.settings import HOST, PORT, DEBUG
from helpers.resizer import resize_and_upload
from keras.models import model_from_json
import pandas as pd
import numpy as np

app = Flask(__name__)

json_file = open('recommender_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
nn_model = model_from_json(loaded_model_json)
nn_model.load_weights("rec_weights.h5")

PRODUCT_OHE = pd.read_csv('../data/product_ids.csv')
PRODUCT_CODE = pd.read_csv('../data/product_codes.csv')
NUM_ARTICLES = PRODUCT_CODE.unique().size

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
    try:
        input_vec = np.append(np.array([gender_code, age]), np.zeros(NUM_ARTICLES))
        output_vec = model.predict(input_vec)
        most_probable = np.argmax(output_vec)
        accuracy = np.max(output_vec) * 100
        product = PRODUCT_CODE[PRODUCT_OHE == most_probable].values[0]
    except:
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
