from contextlib import contextmanager

from flask import Flask, request, json, jsonify
from psycopg2 import pool

from api.settings import HOST, PORT, DEBUG
from helpers.resizer import resize_and_upload
import logging

app = Flask(__name__)
db = pool.SimpleConnectionPool(
    1, 10, host='ec2-54-247-81-88.eu-west-1.compute.amazonaws.com', database='dd5fd1bu74cdkb', user='vonhwrarqlubaj',
    password='cc3766fdc1656b071806c4209eea4273ce16cdf7e5e8050d5fe30a5fbe5e0f7a', port=5432)


@contextmanager
def get_cursor():
    con = db.getconn()
    try:
        yield con
    finally:
        con.commit()
        db.putconn(con)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/latest-records', methods=['GET'])
def get_latest_records():
    query = """
    SELECT adi_face.*, adi_client.gender FROM adi_face
    JOIN adi_client
      ON adi_face.user_id=adi_client.id
    ORDER BY adi_face.timestamp DESC
    LIMIT 10
    """
    with get_cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    data = [{
        'face_id': result[0],
        'user_id': result[1],
        'camera_id': result[2],
        'gender': result[15],
        'age': {
            'min': result[3],
            'max': result[4],
        },
        'emotions': {
            'happy': result[5],
            'sad': result[6],
            'angry': result[7],
            'confused': result[8],
            'disgusted': result[9],
            'surprised': result[10],
            'smile': result[11],
            'calm': result[12],
        },
        'image_url': result[13],
        'timestamp': result[14],

    } for result in results]
    logging.error(data)
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Content-Length, X-Requested-With'
    return response


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


@app.route("/get-record", methods=['POST'])
def get_record():
    adi_client = request.get_json(silent=True)
    if adi_client['is_new_user']:
        query = """
        INSERT INTO adi_client (gender) VALUES(%s)
        RETURNING id
        """
        with get_cursor() as cursor:

            cursor.execute(query, (adi_client.get('gender', ''),))
            adi_client_id = cursor.fetchone()[0]
            query = """
            INSERT INTO adi_face (id,
                                  user_id,
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (adi_client['face_id'],
                                   adi_client_id,
                                   adi_client['camera_id'],
                                   adi_client['age']['low'],
                                   adi_client['age']['high'],
                                   adi_client['emotions']['happy'],
                                   adi_client['emotions']['sad'],
                                   adi_client['emotions']['angry'],
                                   adi_client['emotions']['confused'],
                                   adi_client['emotions']['disgusted'],
                                   adi_client['emotions']['surprised'],
                                   adi_client['emotions']['smile'],
                                   adi_client['emotions']['calm'],
                                   adi_client['image_url']))
    else:
        for match in adi_client['matches']:
            query = "SELECT user_id FROM adi_face WHERE id='{}'".format(match)
            with get_cursor() as cursor:

                cursor.execute(query)
                matched_ids = cursor.fetchone()
                if matched_ids is not None:
                    user_id = matched_ids[0]
                    query = """
                            INSERT INTO adi_face (id,
                                                  user_id,
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
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                    cursor.execute(query, (adi_client['face_id'],
                                           user_id,
                                           adi_client['camera_id'],
                                           adi_client['age']['low'],
                                           adi_client['age']['high'],
                                           adi_client['emotions']['happy'],
                                           adi_client['emotions']['sad'],
                                           adi_client['emotions']['angry'],
                                           adi_client['emotions']['confused'],
                                           adi_client['emotions']['disgusted'],
                                           adi_client['emotions']['surprised'],
                                           adi_client['emotions']['smile'],
                                           adi_client['emotions']['calm'],
                                           adi_client['image_url']))
                else:
                    continue
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
