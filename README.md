# 20_deep_scheduling

This is a project about using Gaussian Mixture Model (GMM) clustering and Reinforcement Learning (RL) for load balancing.

Please refer to the plan.md document for details.

## Details

The project uses the social networking app of the [DeathStarBench project](https://github.com/delimitrou/DeathStarBench) as the backend.

The load balancer is based on the open source version of the popular [NGINX](https://www.nginx.com/).

The upstream statistics is obtained through the use of the [nginx-module-vts](https://github.com/vozlt/nginx-module-vts) module.

The DeathStarBench project provides three scripts to generate load on the social network app that use the [wrk load generator](https://github.com/wg/wrk). These are contained in the `scripts/social-network` folder.

The app supports three requests:

- Creating a post
- Reading posts on the user's home timeline
- Reading posts on other user's timelines

Example usages are:

```bash
./wrk -D exp -t 2 -c 10 -d 5 -L -s ./scripts/social-network/compose-post.lua http://<nginx-lb>/wrk2-api/post/compose -R 100
./wrk -D exp -t 2 -c 10 -d 5 -L -s ./scripts/social-network/read-home-timeline.lua http://<nginx-lb>/wrk2-api/home-timeline/read -R 100
./wrk -D exp -t 2 -c 10 -d 5 -L -s ./scripts/social-network/read-user-timeline.lua http://<nginx-lb>/wrk2-api/user-timeline/read -R 100
```

Here work is generated using an exponential distribution. There are two threads running the workload with 10 connections and 100 requests per second. The `-L` switch prints out the entire latency percentiles.

## Work done so far

A load generator has been written in C - `gen_load.c`

- There are four threads in the program. Three of them run one request type while the fourth simply reports time remaining on the test.
- The testing threads choose a distribution at random from `exponential`, `normal`, `fixed` and `zipf`.
- Then each thread runs the test for a random amount of time between 30 seconds and 10 minutes.
- The number of requests are randomly chosen to be between 1000 and 2000 requests per second.
- After each testing period is complete, the thread backs off for a random amount of time between 10 and 100 seconds.
- This can be run simply as `./gen_load`

A statistics collector has also been written in Python 3 - `get_stats.py`

- This collector gets its statistics as json from the `nginx-module-vts` module and stores it in a `.json` file.
- This can be run as `python get_stats.py example.json`
- This script detects if the `gen_load` binary is running and exits automatically when the `gen_load` binary exits.
- This script is based on Python 3.

A `Makefile` has also been provided to build and run the above, as well as to test the Python version. This testing is available from the `check_python.py` script.

The easiest way to run these programs and collect the statistics is to simply run the following command in a terminal.

```bash
make ARGS="example.json" run
```

This command does the following:

- Builds the `gen_load` binary
- Checks that the environment supports Python 3 or exits
- Starts the load generation in the background
- Starts collecting statistics from the nginx server and saves it into the provided file name.

## How the statistics look

There are three upstream groups (`service groups`) created:

- `compose_backend`
- `home_read_backend`
- `user_read_backend`

Each of these `service groups` map to a specific request type. As of now they all contain the same set of servers (`server1`, `server2` and `server3`) but they can contain different servers without loss of generality.

The following statistics are collected from say `server1` for the `compose` request type:

1.  `requestCounter` - Number of requests of this type forwarded to this server
2.  `inBytes` and `outBytes` are self explanatory
3.  `Non 2xx/3xx responses` simply encompass all `1xx`, `4xx` and `5xx` responses from the backend.
4.  `requestMsecCounter` number of accumulated request processing time in milliseconds
5.  `maxFails` is the number of fails that must occur during `failTimeout` to mark the server unavailable.
6.  `backup` if the server is being used as a backup
7.  `down` if the server is marked as being unavailable.

We are using `weight` as our control; so it's not part of the `state`.
