import asyncpg
from api.settings import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT


# class DbConnection:
#
#     def __init__(self):
#         self.connection = None
#
#     def __enter__(self):
#         self.connection = asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT)
#
#     def __exit__(self, *args):
#         self.connection.close()
#
# async def create_connection():
#     return asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT)

#
# async def get_connection():
#     conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT)
#     print('connection created')
#     yield conn
#     print('destroying connection')
#     # values = await conn.fetch('''SELECT * FROM mytable''')
#     await conn.close()
