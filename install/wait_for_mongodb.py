import sys
import os
from pymongo import MongoClient, errors
sys.path.append(os.getcwd())
from helpers.config import get_config

config = get_config('mongo')

mongoClient = MongoClient(host=config['host'], port=config['port'], serverSelectionTimeoutMS=2000)
while(True):
    try:
        mongoClient.server_info()
        print("MongoDB started ... continue", flush=True)
        sys.exit(0)
    except errors.ServerSelectionTimeoutError:
        print("MongoDB pending ... waiting", flush=True)
    except Exception:
        print("MongoDB unknown error ... aborting", flush=True)
        sys.exit(1)
