#!/home/ratnadeepb/miniconda3/envs/py3_env/bin/python
# '''
#  Created on Fri Feb 14 2020:22:05:25
#  Created by Ratnadeep Bhattacharya
# '''

import subprocess


def check_version():
    text = subprocess.check_output(["python", "--version"])

    if str(text).find('3') < 0:
        return False
    else:
        return True


if __name__ == "__main__":
    import sys

    if check_version() == False:
        sys.stderr.write("Need Python 3\n")
        sys.exit(-1)

    print("Correct Python version found")
