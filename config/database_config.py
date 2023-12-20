import sys

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from config.logger_config import LoggerConfig
import logging
terminalLogFlag = True
logger = LoggerConfig("database_config", level=logging.INFO, log_path='../logs/config', enable_console=terminalLogFlag).get_logger()


# Includes database operations
class DB:
    DEFAULT_USERNAME = "thirdpartydevtool"
    DEFAULT_PASSWORD = "mohd"
    DEFAULT_CLUSTER = "cluster0.6dtz6l1.mongodb.net"
    DEFAULT_DATABASE = "p2p-chat"

    def __init__(self, username=None, password=None, connection_string=None):
        self.username = username or self.DEFAULT_USERNAME
        self.password = password or self.DEFAULT_PASSWORD
        self.cluster = self.DEFAULT_CLUSTER
        self.database = self.DEFAULT_DATABASE

        if connection_string is None:
            connection_string = f"mongodb+srv://{self.username}:{self.password}@{self.cluster}/{self.database}?retryWrites=true&w=majority"

        self.client = MongoClient(connection_string)
        self.db = self.client[self.database]
        self.is_connection_working()


    def is_account_exist(self, username):
        return len(list(self.db.accounts.find({'username': username}))) > 0

    def register(self, username, password):
        account = {"username": username, "password": password}
        self.db.accounts.insert_one(account)

    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]

    def is_account_online(self, username):
        return len(list(self.db.online_peers.find({"username": username}))) > 0

    def user_login(self, username, ip, port):
        online_peer = {"username": username, "ip": ip, "port": port}
        self.db.online_peers.insert_one(online_peer)

    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return res["ip"], res["port"]

    def register_room(self, room_id, peers=[]):
        if self.db.rooms.find_one({"room_id": room_id}):
            logger.error(f"Room with id {room_id} already exists.")
            raise ValueError(f"Room with id {room_id} already exists.")

        room = {"room_id": room_id, "peers": peers}
        self.db.rooms.insert_one(room)

    def is_room_exist(self, room_id):
        return len(list(self.db.rooms.find({'room_id': room_id}))) > 0

    def get_room_peers(self, room_id):
        res = self.db.rooms.find_one({"room_id": room_id})
        return res["_id"], res["peers"]

    def update_room(self, id, peers):
        filter_criteria = {"_id": id}
        update_data = {"$set": {"peers": peers}}
        self.db.rooms.update_one(filter_criteria, update_data)

    def remove_peer(self, id, peer):
        filter_criteria = {"room_id": id}
        room = self.db.rooms.find_one(filter_criteria)
        new_peers = room["peers"].remove(peer)
        update_data = {"$set": {"peers": new_peers}}
        self.db.rooms.update_one(filter_criteria, update_data)

    def get_all_online_users(self):
        online_users = list(self.db.online_peers.find({}, {"_id": 0, "username": 1, "ip": 1, "port": 1}))
        return online_users

    def is_connection_working(self):
        try:
            logger.info("Connecting to the database")
            self.client.server_info()
            logger.info("Connection to the database is working")

        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            sys.exit("Terminating the program due to a database connection error")

# Example usage
db_instance = DB()