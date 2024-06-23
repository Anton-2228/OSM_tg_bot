import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Database:

    def __init__(self):
        conn = psycopg2.connect(user='postgres', dbname='osm_roads',
                                password='1234', host='127.0.0.1', port="5432")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = conn.cursor()

    def drop_table_users(self):
        try:
            self.cursor.execute("DROP table users;")
        except:
            pass

    def drop_table_pictures(self):
        try:
            self.cursor.execute("DROP table pictures;")
        except:
            pass

    def create_DB(self):
        try:
            self.cursor.execute("CREATE DATABASE osm_roads;")
        except:
            pass

    def create_table_users(self):
        try:
            self.cursor.execute("CREATE TABLE users (id serial PRIMARY KEY, telegram_id bigint, hash text);")
        except:
            pass

    def create_table_pictures(self):
        try:
            self.cursor.execute("CREATE TABLE pictures (id serial PRIMARY KEY, user_id integer, path_to_osm text, path_to_pic text);")
        except:
            pass

    def get_user_id(self, hash):
        self.cursor.execute(f"SELECT id FROM users WHERE hash={hash};")
        return self.cursor.fetchone()

    def get_telegram_id(self, hash):
        self.cursor.execute(f"SELECT telegram_id FROM users WHERE hash={hash};")
        return self.cursor.fetchone()

    def get_hash(self, telegram_id):
        self.cursor.execute(f"SELECT hash FROM users WHERE telegram_id={telegram_id};")
        return self.cursor.fetchone()

    def add_user(self, telegram_id, hash):
        self.cursor.execute(f"INSERT INTO users"
                            f"(telegram_id, hash)"
                            f"VALUES"
                            f"({telegram_id}, {hash});")

    def get_pictures(self, user_id):
        self.cursor.execute(f"SELECT path FROM pictures WHERE user_id={user_id};")
        return self.cursor.fetchone()

    def add_pictures(self, user_id, path_to_osm, path_to_pic):
        self.cursor.execute(f"INSERT INTO pictures"
                            f"(user_id, path_to_osm, path_to_pic)"
                            f"VALUES"
                            f"({user_id}, {path_to_osm}, {path_to_pic});")
