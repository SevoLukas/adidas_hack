import psycopg2
import os
import boto3
rekognition = boto3.client('rekognition',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                           aws_secret_access_key=os.getenv('AWS_SECRET'),
                           region_name='eu-west-1')

rekognition.delete_collection(
    CollectionId='adifaces-test'
)
rekognition.create_collection(
    CollectionId='adifaces-test'
)


conn = psycopg2.connect("dbname='dd5fd1bu74cdkb' user='vonhwrarqlubaj' host='ec2-54-247-81-88.eu-west-1.compute.amazonaws.com' password='cc3766fdc1656b071806c4209eea4273ce16cdf7e5e8050d5fe30a5fbe5e0f7a'")
cur = conn.cursor()

query = """
    DELETE FROM adi_face
"""
cur.execute(query)

query = """
    DELETE FROM adi_client
"""
cur.execute(query)

query = """
    ALTER SEQUENCE user_id_seq RESTART WITH 1
"""
cur.execute(query)

query = """
    ALTER SEQUENCE face_id_seq RESTART WITH 1
"""
cur.execute(query)

conn.commit()
conn.close()
