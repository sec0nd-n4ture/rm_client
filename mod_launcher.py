from mod_config import SOLDAT_SERVER_ADDRESS, SOLDAT_EXECUTABLE_DIR, SOLDAT_SERVER_PASSWORD
from subprocess import Popen
import os
import time

Popen(f"{SOLDAT_EXECUTABLE_DIR} -joinurl soldat://{SOLDAT_SERVER_ADDRESS[0]}:{SOLDAT_SERVER_ADDRESS[1]}/{SOLDAT_SERVER_PASSWORD}")
time.sleep(3)
os.system("python mod_main.py")