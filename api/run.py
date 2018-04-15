from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from flask import make_response, request, current_app
from functools import update_wrapper
from datetime import timedelta
from api.settings import HOST, PORT, DEBUG
from helpers.resizer import resize_and_upload
import psycopg2
import logging


app = Flask(__name__)

conn = psycopg2.connect("dbname='dd5fd1bu74cdkb' user='vonhwrarqlubaj' host='ec2-54-247-81-88.eu-west-1.compute.amazonaws.com' password='cc3766fdc1656b071806c4209eea4273ce16cdf7e5e8050d5fe30a5fbe5e0f7a'")


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/api/latest-records', methods=['GET'])
@crossdomain(origin='*')
def get_latest_records():
    cur = conn.cursor()
    query = """
    SELECT adi_face.*, adi_client.gender FROM adi_face
    JOIN adi_client
      ON adi_face.user_id=adi_client.id
    ORDER BY adi_face.timestamp DESC
    LIMIT 10
    """
    cur.execute(query)
    results = cur.fetchall()
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
    cur = conn.cursor()
    adi_client = request.get_json(silent=True)
    if adi_client['is_new_user']:
        query = """
        INSERT INTO adi_client (gender) VALUES(%s)
        RETURNING id
        """
        cur.execute(query, (adi_client.get('gender', ''),))
        adi_client_id = cur.fetchone()[0]
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
        cur.execute(query, (adi_client['face_id'],
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
        conn.commit()
    else:
        for match in adi_client['matches']:
            query = "SELECT user_id FROM adi_face WHERE id='{}'".format(match)
            cur.execute(query)
            matched_ids = cur.fetchone()
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
                cur.execute(query, (adi_client['face_id'],
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
                conn.commit()
            else:
                continue
    return 'ok'


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
