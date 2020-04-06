#
# Created on Wed Mar 25 2020:19:15:31
# Created by Ratnadeep Bhattacharya
#

import json
import sys
import pandas as pd
from sklearn.mixture import GaussianMixture
import numpy as np

'''
There are 3 request types
and 25 control inputs
The number of states has been, arbitrarily, determined to be 3^3 = 27
The logic is that every request type can be in three distinct states:
 - HIGH
 - MEDIUM
 - LOW
A further assumption is that every control change affects a state change
'''
NUM_CLUS = 27

ZONES = ['compose_backend', 'user_read_backend', 'home_read_backend']
SERVERS = ['192.168.1.137:8080', '192.168.1.138:8080', '192.168.1.139:8080']
METRICS = ['outBytes', 'inBytes', 'down', 'Non 2xx/3xx responses']
CONNECTION_STATUS = ["active"]
CONTROL = ['weight']
'''
5 - high share
3 - medium share
1 - low share
'''
# CONTROL_VALS = [1, 3, 5]
COLS = []
ACTIONS = []


def gen_cols():
    for z in ZONES:
        for srv in SERVERS:
            for metric in METRICS + CONTROL:
                COLS.append("{}_{}_{}".format(z, srv, metric))
    for name in CONNECTION_STATUS:
        COLS.append("connections_{}".format(name))


def get_data(filename):
    """load data for analysis"""
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
        return data


def arrange_data(data):
    tmp = {k: [] for k in COLS}
    for entry in data:
        for z in ZONES:
            for srv in SERVERS:
                for metric in METRICS + CONTROL:
                    tmp["{}_{}_{}".format(z, srv, metric)
                        ].append(entry[z][srv][metric])
        for c in CONNECTION_STATUS:
            tmp["connections_{}".format(c)].append(
                entry["connections"][c])
    return pd.DataFrame.from_dict(tmp)


NON_STATE_COLS = []


def non_state_cols():
    for z in ZONES:
        for srv in SERVERS:
            NON_STATE_COLS.append("{}_{}_weight".format(z, srv))


def create_cluster(X):
    gmm = GaussianMixture(n_components=NUM_CLUS, reg_covar=1e-3).fit(X)
    return gmm.predict(X)


def create_actions():
    for w in POSSIBLE_WEIGHTS:
        ACTIONS.append(w * 3)


def actions_index(x):
    for i, elem in enumerate(ACTIONS):
        if (elem == x).all():
            return i


def transition_probs(transition_map):
    """
    Calculate the probability of transitioning from one state to another
    """

    # Dictionary of dictionaries
    probs = np.zeros((NUM_CLUS, NUM_CLUS, len(ACTIONS)))
    index = transition_map.index.to_list()
    for i in range(1, index[-1] + 1):
        idx = actions_index(transition_map.iloc[i].values[:-1])
        probs[transition_map.iloc[i - 1].values[-1]
              ][transition_map.iloc[i].values[-1]][idx] += 1
    for i in range(probs.shape[0]):
        for j in range(probs.shape[1]):
            probs[i][j] /= probs[i][j].sum()
    return probs


def main(datafile, probfile):
    data = get_data(datafile)
    gen_cols()
    non_state_cols()
    dataframe = arrange_data(data)
    df_normed = (dataframe - dataframe.mean()) / \
        (dataframe.max() - dataframe.min())
    states = create_cluster(df_normed.drop(NON_STATE_COLS, axis=1))
    transition_map = dataframe[NON_STATE_COLS]
    transition_map["state"] = states
    dataframe["state"] = states
    trans_probs = transition_probs(transition_map)
    trans_probs.to_csv(probfile)


def usage():
    print("python", sys.argv[0], "<datafile> <probfile>")
    print("datafile contains the data")
    print("probfile is where the state transition probabilities will be written to")


if __name__ == "__main__":
    try:
        datafile = sys.argv[1]
        probfile = sys.argv[2]
    except IndexError:
        sys.stderr.write("usage")
        usage()
        sys.exit(1)
    try:
        main(datafile, probfile)
    except ImportError as e:
        sys.stderr.write(e)
        sys.exit(1)
