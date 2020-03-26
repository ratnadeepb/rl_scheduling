#
# Created on Thu Feb 20 2020:16:42:22
# Created by Ratnadeep Bhattacharya
#

import nginxparser as ng
# from itertools import combinations_with_replacement
from itertools import permutations
import time
import subprocess
import sys
import signal

# 10 -> high share, 5 -> medium share, 2 -> low share
NUM_CLUS = 3
CONTROL_VALS = [1, 3, 5] * NUM_CLUS
POSSIBLE_WEIGHTS = []
COLS = []

# PARENT_STRUCTURE = [['worker_processes', '1'], [['events'], [['worker_connections', '1024']]], [['http'], [['vhost_traffic_status_zone'], ['vhost_traffic_status_average_method', 'WMA 60s'], ['vhost_traffic_status_histogram_buckets', '0.005 0.01 0.05 0.1 0.5 1 5 10'], ['include', 'mime.types'], ['default_type', 'application/octet-stream'], ['sendfile', 'on'], ['keepalive_timeout', '65'], [['upstream', 'compose_backend'], [['keepalive', '100'], ['server', '192.168.1.137:8080 weight=1'], ['server', '192.168.1.138:8080 weight=1'], ['server', '192.168.1.139:8080 weight=1']]], [['upstream', 'home_read_backend'], [['keepalive', '100'], ['server', '192.168.1.137:8080 weight=1'], ['server', '192.168.1.138:8080 weight=1'], ['server', '192.168.1.139:8080 weight=1']]], [['upstream', 'user_read_backend'], [['keepalive', '100'], ['server', '192.168.1.137:8080 weight=1'], ['server', '192.168.1.138:8080 weight=1'], ['server', '192.168.1.139:8080 weight=1']]], [['server'], [['listen', '80'], ['server_name', 'localhost'], [['location', '/'], [['root', 'html'], ['index', 'index.html index.htm']]], [['location', '/nginx_status'], [['stub_status', 'on'], ['access_log', 'off']]], [['location', '/status'], [['vhost_traffic_status_display'], ['vhost_traffic_status_display_format', 'html']]], [['location', '/wrk2-api/post/compose'], [['proxy_pass', 'http://compose_backend/wrk2-api/post/compose']]], [['location', '/wrk2-api/home-timeline/read'], [['proxy_pass', 'http://home_read_backend/wrk2-api/home-timeline/read']]], [['location', '/wrk2-api/user-timeline/read'], [['proxy_pass', 'http://user_read_backend/wrk2-api/user-timeline/read']]], ['error_page', '500 502 503 504  /50x.html'], [['location', '=', '/50x.html'], [['root', 'html']]]]]]]]


def gen_control_list():
    # comb = combinations_with_replacement(CONTROL_VALS, len(CONTROL_VALS))
    perm = permutations(CONTROL_VALS, NUM_CLUS)
    tmp = []
    for c in list(perm):
        tmp.append(c)
    global POSSIBLE_WEIGHTS
    for elem in tmp:
        if (elem[0] / elem[-1]) % 1 != 0 or (elem[1] / elem[-1]) % 1 != 0 or (elem[2] / elem[-1]) % 1 != 0:
            POSSIBLE_WEIGHTS.append(elem)
        else:
            POSSIBLE_WEIGHTS.append((
                (int)(elem[0] / elem[-1]), (int)(elem[1] / elem[-1]), (int)(elem[2] / elem[-1])))
    s = set(POSSIBLE_WEIGHTS)
    POSSIBLE_WEIGHTS = list(s)


gen_control_list()


def change_weights(wait_time):
    signal.signal(signal.SIGINT, signal_handler)

    # getting the file
    config = ng.load(open("/etc/nginx/nginx.conf"))

    # getting the weights
    http = []
    http.extend(config[-1][1])

    upstreams = {}

    for item in http:
        if len(item) > 1 and isinstance(item[0], list):
            if item[0][0] == "upstream":
                tmp = []
                for i in item[1]:
                    if i[0] == "server":
                        tmp.append(i[1].split())
                upstreams[item[0][1]] = tmp

    # changing the weights
    while (1):
        for w in POSSIBLE_WEIGHTS:
            print("Running with", w)
            time.sleep(wait_time)
            for _, v in upstreams.items():
                for i in range(len(v)):
                    v[i][1] = "weight={}".format(w[i])
            # formatting weights
            NEW_VALS = []
            for _, v in upstreams.items():
                for i in range(len(v)):
                    NEW_VALS.append("{} {}".format(v[i][0], v[i][1]))
            # putting weights into the http list
            j = 0  # track which val from NEW_VALS to get
            for item in http:
                if len(item) > 1 and isinstance(item[0], list):
                    if item[0][0] == "upstream":
                        tmp = []
                        for i in item[1]:
                            if i[0] == "server":
                                i[1] = NEW_VALS[j]
                                j += 1
            # putting weights into config
            config[-1][1] = http

            # write out to the file
            out = open("/etc/nginx/nginx.conf", 'w')
            ng.dump(config, out)

            # restart the nginx process
            subprocess.call(["nginx", "-s", "reload"])


def signal_handler(sig, frame):
    print("Exiting")
    sys.exit(0)


def usage():
    sys.stderr.write("NEEDS python 3\n")
    sys.stderr.write("Usage: sudo python {}\n".format(sys.argv[0]))
    sys.stderr.write(
        "Required packages: nginxparser, itertools, subprocess\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            usage()
            sys.exit(-1)
        else:
            wait = sys.argv[1]
    else:
        wait = 10
    print("CTRL + C to exit")
    print(wait, "seconds between changing weights")
    gen_control_list()
    change_weights(5)
