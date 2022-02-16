import time
from helpers.mongodb import start_mongodb_connection
from helpers.tmnf import start_processes as start_tmnf_connection

start_mongodb_connection()
start_tmnf_connection()

while True:
    time.sleep(10000)
