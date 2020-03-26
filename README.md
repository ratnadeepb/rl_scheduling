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
- The number of requests are randomly chosen to be between 100 and 2000 requests per second.
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

A separate script `change_nginx_weight.py` needs to run on the nginx/proxy node. This script changes the weights of the different servers after a while.

### Manually running things on separate windows or tmux panes (for better control)

On the client node

```bash
./gen_load
python get_states.py nginx_state_for_clustering.json
```

On the nginx node

```bash
sudo /home/ratnadeepb/miniconda3/envs/py3_env/bin/python change_nginx_weights.py 2
```

## How the statistics look

There are three upstream groups (`service groups`) created:

- `compose_backend`
- `home_read_backend`
- `user_read_backend`

Each of these `service groups` map to a specific request type. As of now they all contain the same set of servers (`server1`, `server2` and `server3`) but they can contain different servers without loss of generality.

The following statistics are collected from say `server1` for the `compose` request type:

1. `inBytes` and `outBytes` are self explanatory
2. `Non 2xx/3xx responses` simply encompass all `1xx`, `4xx` and `5xx` responses from the backend.
3. `weight` of this particular server
4. `requestMsec` is average response time


We are using `weight` as our control; so it's not part of the `state`.

## Building NGINX for this project

Mostly, this [guide](https://www.vultr.com/docs/how-to-compile-nginx-from-source-on-ubuntu-16-04) can be followed.

### Prerequisites

```bash
sudo apt install build-essential -y

# PCRE version 4.4 - 8.40
wget https://ftp.pcre.org/pub/pcre/pcre-8.40.tar.gz && tar xzvf pcre-8.40.tar.gz

# zlib version 1.1.3 - 1.2.11
wget http://www.zlib.net/zlib-1.2.11.tar.gz && tar xzvf zlib-1.2.11.tar.gz

# OpenSSL version 1.0.2 - 1.1.0
wget https://www.openssl.org/source/openssl-1.1.0f.tar.gz && tar xzvf openssl-1.1.0f.tar.gz

```

### Get NGINX (latest, as of this document, 1.17.8)

```bash
wget https://nginx.org/download/nginx-1.17.8.tar.gz

tar zxvf nginx-1.17.8.tar.gz

rm -rf *.tar.gz

cd ~/nginx-1.17.8
```

### Configure and install NGINX

```bash
./configure --prefix=/usr/share/nginx \
            --sbin-path=/usr/sbin/nginx \
            --modules-path=/usr/lib/nginx/modules \
            --conf-path=/etc/nginx/nginx.conf \
            --error-log-path=/var/log/nginx/error.log \
            --http-log-path=/var/log/nginx/access.log \
            --add-module=/path/to/nginx-module-vts \
            --pid-path=/run/nginx.pid \
            --lock-path=/var/lock/nginx.lock \
            --build=Ubuntu \
            --http-client-body-temp-path=/var/lib/nginx/body \
            --http-fastcgi-temp-path=/var/lib/nginx/fastcgi \
            --http-proxy-temp-path=/var/lib/nginx/proxy \
            --http-scgi-temp-path=/var/lib/nginx/scgi \
            --http-uwsgi-temp-path=/var/lib/nginx/uwsgi \
            --with-openssl=../openssl-1.1.0f \
            --with-openssl-opt=enable-ec_nistp_64_gcc_128 \
            --with-openssl-opt=no-nextprotoneg \
            --with-openssl-opt=no-weak-ssl-ciphers \
            --with-openssl-opt=no-ssl3 \
            --with-pcre=../pcre-8.40 \
            --with-pcre-jit \
            --with-zlib=../zlib-1.2.11 \
            --with-compat \
            --with-file-aio \
            --with-threads \
            --with-http_addition_module \
            --with-http_auth_request_module \
            --with-http_dav_module \
            --with-http_flv_module \
            --with-http_gunzip_module \
            --with-http_gzip_static_module \
            --with-http_mp4_module \
            --with-http_random_index_module \
            --with-http_realip_module \
            --with-http_slice_module \
            --with-http_ssl_module \
            --with-http_sub_module \
            --with-http_stub_status_module \
            --with-http_v2_module \
            --with-http_secure_link_module \
            --with-mail \
            --with-mail_ssl_module \
            --with-stream \
            --with-stream_realip_module \
            --with-stream_ssl_module \
            --with-stream_ssl_preread_module \
            --with-debug \
            --with-cc-opt='-g -O2 -fPIE -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2' \
            --with-ld-opt='-Wl,-Bsymbolic-functions -fPIE -pie -Wl,-z,relro -Wl,-z,now'
make
sudo make install
```

### Clean directory and test

```bash
cd ~
rm -r nginx-1.17.8/ openssl-1.1.0f/ pcre-8.40/ zlib-1.2.11/

# NGINX version
sudo nginx -v && sudo nginx -V

# Testing config file
sudo nginx -t
```

### NGINX operations

```bash
# Run nginx
sudo nginx

# Reload after changing conf
sudo nginx -s reload

# Stop gracefully
sudo nginx -s stop

# Quit
sudo nginx -s quit
```

### NGINX file locations

```none
/usr/share/nginx
/usr/sbin/nginx
/etc/nginx
/var/log/nginx

# Config file and logs
/etc/nginx/nginx.conf
/var/lib/nginx
```
