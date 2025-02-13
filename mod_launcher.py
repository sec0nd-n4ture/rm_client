from subprocess import Popen
import os
import time

Popen("C:\Soldat\soldat.exe -joinurl soldat://127.0.0.1:23074")
time.sleep(3)
os.system("python mod_main.py")