from flask import Flask, request
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
