import os
import time


def clear_terminal():
    time.sleep(1)

    if os.system == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    time.sleep(1)
