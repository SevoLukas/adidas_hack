from flask import Flask, request
from flask import jsonify
from api.settings import HOST, PORT, DEBUG
from helpers.resizer import resize_and_upload
import psycopg2
import logging


app = Flask(__name__)
conn = psycopg2.connect("dbname='dd5fd1bu74cdkb' user='vonhwrarqlubaj' host='ec2-54-247-81-88.eu-west-1.compute.amazonaws.com' password='cc3766fdc1656b071806c4209eea4273ce16cdf7e5e8050d5fe30a5fbe5e0f7a'")


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


@app.route("/get-record", methods=['GET', 'POST'])
def get_record():
    cur = conn.cursor()
    adi_client = request.get_json(silent=True)
    if adi_client['is_new_user']:
        query = """
        INSERT INTO adi_client (gender) VALUES(%s)
        RETURNING id
        """
        cur.execute(query, ('Female',))
        adi_client_id = cur.fetchone()[0]
        query = """
        INSERT INTO adi_face (user_id,
                              camera_id,
                              min_age,
                              max_age,
                              happy,
                              sad,
                              angry,
                              confused,
                              disgusted,
                              surprised,
                              smile,
                              calm,
                              image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (adi_client_id,
                            adi_client['camera_id'],
                            adi_client['age']['min'],
                            adi_client['age']['max'],
                            adi_client['emotions']['happy'],
                            adi_client['emotions']['sad'],
                            adi_client['emotions']['angry'],
                            adi_client['emotions']['confused'],
                            adi_client['emotions']['disgusted'],
                            adi_client['emotions']['surprised'],
                            adi_client['emotions']['smile'],
                            adi_client['emotions']['calm'],
                            adi_client['image_url']))
        conn.commit()
        # cur.execute("INSERT INTO product(store_id, url, price, charecteristics, color, dimensions) VALUES (%s, %s, %s, %s, %s, %s)", (1,  'http://www.google.com', '$20', json.dumps(thedictionary), 'red', '8.5x11'))


        # """

    # {
    #     'is_new_user': len(matches) == 0,
    #     'matches': matches,
    #     'face_id': face_id,
    #     'camera_id': get_camera_id(key),
    #     'age': get_age_info(face_detail),
    #     'gender': get_gender(face_detail),
    #     'emotions': get_emotions(face_detail),
    #     'image_url': FACES_PREFIX + face_id + '.jpg',
    # }

    # cur.execute("""SELECT * from adi_client""")
    # rows = cur.fetchall()
    # for row in rows:
    #     logging.warning(row)
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
