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


conn = psycopg2.connect("dbname='' user='' host='' password=''")
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

