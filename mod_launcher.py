from mod_config import SOLDAT_SERVER_ADDRESS
from subprocess import Popen
import os
import time

Popen(f"C:\Soldat\soldat.exe -joinurl soldat://{SOLDAT_SERVER_ADDRESS[0]}:{SOLDAT_SERVER_ADDRESS[1]}")
time.sleep(3)
os.system("python mod_main.py")