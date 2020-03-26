/*
 * Created on Thu Feb 13 2020:16:54:18
 * Created by Ratnadeep Bhattacharya
 */

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define NUM_ITERS 10
#define UPPER_SLEEP_TIME 100
#define UPPER_EXEC_TIME 600
#define UPPER_REQS 2000
#define LOWER_SLEEP_TIME 10
#define LOWER_EXEC_TIME 30
#define LOWER_REQS 100

#define TEST_TIME                                                              \
        UPPER_EXEC_TIME * 6 *                                                  \
            5 /* make sure TEST_TIME is greater than all UPPER TIMES */
#define WAIT_TM 15

static int stop;

void
death_msg(char *msg)
{
        fprintf(stderr, "%s", msg);
        exit(EXIT_FAILURE);
}

/* protected malloc
 * take a size and a message as arguments
 * if malloc succeeds then returns a non-null pointer
 * else fails and prints the user provided msg to the stderr
 */
void *
pmalloc(size_t n, char *msg)
{
        void *p;
        if (!(p = malloc(n)))
                death_msg(msg);
        return p;
}

void *
compose_post(__attribute__((unused)) void *argv)
{
        int ret;
        char *cmd;
        int exec_tm;
        int reqs;
        char *dist;
        int cur_tm = 0;
        int old_tm = 0;
#if 0
        char *cmd1 = "./wrk -D exp -t 1 -c 100 -s ./scripts/social-network/compose-post.lua http://192.168.1.134/wrk2-api/post/compose -R 2000 -d 500";
        dist = fixed/exp/norm/zipf;
#endif // 0

        cmd = pmalloc(sizeof(char) * 200,
                      "Failed to create memory for command\n");
        dist =
            pmalloc(sizeof(char) * 6, "Failed to create memory for command\n");

        while (!stop) {
                srand(time(0));
                cur_tm = (rand() % (UPPER_SLEEP_TIME - LOWER_SLEEP_TIME + 1)) +
                         LOWER_SLEEP_TIME;
                exec_tm = (rand() % (UPPER_EXEC_TIME - LOWER_EXEC_TIME + 1)) +
                          LOWER_EXEC_TIME;
                reqs = (rand() % (UPPER_REQS - LOWER_REQS + 1)) + LOWER_REQS;

                int tmp = (rand() % 4);
                switch (tmp) {
                case 0:
                        memcpy((void *)dist, "fixed", strlen("fixed"));
                        break;
                case 1:
                        memcpy((void *)dist, "exp", strlen("exp"));
                        break;
                case 2:
                        memcpy((void *)dist, "norm", strlen("norm"));
                        break;
                default:
                        memcpy((void *)dist, "zipf", strlen("zipf"));
                        break;
                }

                if (!cur_tm)
                        break;

                if (cur_tm != old_tm) {
                        sprintf(cmd,
                                "./wrk -D %s -t 1 -c 100 -s "
                                "./scripts/social-network/compose-post.lua "
                                "http://192.168.1.134/wrk2-api/post/compose -R "
                                "%d -d %d >> /dev/null",
                                dist, reqs, exec_tm);
                        if ((ret = system(cmd)) != 0) {
                                fprintf(
                                    stderr,
                                    "Failed to run compose post.\nTrying again "
                                    "in 5 ms\n");
                                usleep(5000);
                                continue;
                        }
                        sleep(cur_tm);
                        // printf("Command is:\n\n%s\n", cmd);
                        old_tm = cur_tm;
                }
                memset((void *)dist, 0, 6); /* dist needs to be cleaned whether
                                               or not the if loop runs */
        }

        pthread_exit(NULL);
}

void *
read_home_timeline(__attribute__((unused)) void *argv)
{
        int ret;
        char *cmd;
        int exec_tm;
        int reqs;
        char *dist;
        int cur_tm = 0;
        int old_tm = 0;
#if 0
        char *cmd1 = "./wrk -D exp -t 1 -c 100 -s ./scripts/social-network/compose-post.lua http://192.168.1.134/wrk2-api/post/compose -R 2000 -d 500";
        dist = fixed/exp/norm/zipf;
#endif // 0

        cmd = pmalloc(sizeof(char) * 200,
                      "Failed to create memory for command\n");
        dist =
            pmalloc(sizeof(char) * 6, "Failed to create memory for command\n");

        while (!stop) {
                srand(time(0));
                cur_tm = (rand() % (UPPER_SLEEP_TIME - LOWER_SLEEP_TIME + 1)) +
                         LOWER_SLEEP_TIME;
                exec_tm = (rand() % (UPPER_EXEC_TIME - LOWER_EXEC_TIME + 1)) +
                          LOWER_EXEC_TIME;
                reqs = (rand() % (UPPER_REQS - LOWER_REQS + 1)) + LOWER_REQS;

                int tmp = (rand() % 4);
                switch (tmp) {
                case 0:
                        memcpy((void *)dist, "fixed", strlen("fixed"));
                        break;
                case 1:
                        memcpy((void *)dist, "exp", strlen("exp"));
                        break;
                case 2:
                        memcpy((void *)dist, "norm", strlen("norm"));
                        break;
                default:
                        memcpy((void *)dist, "zipf", strlen("zipf"));
                        break;
                }

                if (!cur_tm)
                        break;

                if (cur_tm != old_tm) {
                        sprintf(
                            cmd,
                            "./wrk -D exp -t 1 -c 100 -s "
                            "./scripts/social-network/read-home-timeline.lua "
                            "http://192.168.1.134/wrk2-api/home-timeline/read "
                            "-R "
                            "%d -d %d >> /dev/null",
                            reqs, exec_tm);
                        if ((ret = system(cmd)) != 0) {
                                fprintf(stderr, "Failed to run home timeline "
                                                "read.\nTrying again "
                                                "in 5 ms\n");
                                usleep(5000);
                                continue;
                        }
                        sleep(cur_tm);
                        // printf("Command is:\n\n%s\n", cmd);
                        old_tm = cur_tm;
                }
                memset((void *)dist, 0, 6); /* dist needs to be cleaned whether
                                               or not the if loop runs */
        }

        pthread_exit(NULL);
}

void *
read_user_timeline(__attribute__((unused)) void *argv)
{
        int ret;
        char *cmd;
        char *dist;
        int exec_tm;
        int reqs;
        int cur_tm = 0;
        int old_tm = 0;
#if 0
        char *cmd1 = "./wrk -D exp -t 1 -c 100 -s ./scripts/social-network/compose-post.lua http://192.168.1.134/wrk2-api/post/compose -R 2000 -d 500";
        dist = fixed/exp/norm/zipf;
#endif // 0

        cmd = pmalloc(sizeof(char) * 200,
                      "Failed to create memory for command\n");
        dist =
            pmalloc(sizeof(char) * 6, "Failed to create memory for command\n");

        while (!stop) {
                srand(time(0));
                cur_tm = (rand() % (UPPER_SLEEP_TIME - LOWER_SLEEP_TIME + 1)) +
                         LOWER_SLEEP_TIME;
                exec_tm = (rand() % (UPPER_EXEC_TIME - LOWER_EXEC_TIME + 1)) +
                          LOWER_EXEC_TIME;
                reqs = (rand() % (UPPER_REQS - LOWER_REQS + 1)) + LOWER_REQS;

                int tmp = (rand() % 4);
                switch (tmp) {
                case 0:
                        memcpy((void *)dist, "fixed", strlen("fixed"));
                        break;
                case 1:
                        memcpy((void *)dist, "exp", strlen("exp"));
                        break;
                case 2:
                        memcpy((void *)dist, "norm", strlen("norm"));
                        break;
                default:
                        memcpy((void *)dist, "zipf", strlen("zipf"));
                        break;
                }

                if (!cur_tm)
                        break;

                if (cur_tm != old_tm) {
                        sprintf(
                            cmd,
                            "./wrk -D exp -t 1 -c 100 -s "
                            "./scripts/social-network/read-user-timeline.lua "
                            "http://192.168.1.134/wrk2-api/user-timeline/read "
                            "-R "
                            "%d -d %d >> /dev/null",
                            reqs, exec_tm);
                        if ((ret = system(cmd)) != 0) {
                                fprintf(stderr, "Failed to run home timeline "
                                                "read.\nTrying again "
                                                "in 5 ms\n");
                                usleep(5000);
                                continue;
                        }
                        sleep(cur_tm);
                        // printf("Command is:\n\n%s\n", cmd);
                        old_tm = cur_tm;
                }
                memset((void *)dist, 0, 6); /* dist needs to be cleaned whether
                                               or not the if loop runs */
        }

        pthread_exit(NULL);
}

void *
print_status(__attribute__((unused)) void *argv)
{
        int rem, hrs, mins, secs, tmp;
        int elapsed_time = 0;
        while (!stop) {
                if (WAIT_TM > TEST_TIME)
                        break;

                sleep(WAIT_TM);
                elapsed_time += WAIT_TM;
                printf("Status: Running load ... ");
                rem = (TEST_TIME - elapsed_time);
                tmp = rem % 3600;
                hrs = (rem - tmp) / 3600;
                if (hrs) {
                        printf("here\n");
                        secs = (rem - hrs * 3600) % 60;
                        mins = (rem - hrs * 3600 - secs) / 60;
                } else {
                        secs = rem % 60;
                        mins = (rem - secs) / 60;
                }

                if (!hrs)
                        if (!mins)
                                printf(
                                    "Approximate time remaining: %d seconds\n",
                                    secs);
                        else if (!secs)
                                printf("Approximate time remaining: %d "
                                       "minutes\n",
                                       mins);
                        else
                                printf("Approximate time "
                                       "remaining: %d minutes, %d seconds\n",
                                       mins, secs);
                else if (!mins)
                        if (!secs)
                                printf("Approximate time remaining: %d "
                                       "hours\n",
                                       hrs);
                        else
                                printf(
                                    "Approximate time remaining: %d hours, %d "
                                    "seconds\n",
                                    hrs, secs);
                else if (!secs)
                        printf("Approximate time "
                               "remaining: %d hours, %d minutes\n",
                               hrs, mins);
                else
                        printf("Approximate time "
                               "remaining: %d hours, %d minutes, %d seconds\n",
                               hrs, mins, secs);
        }
        printf("Ending Load Run\n");
        pthread_exit(NULL);
}

int
main(int argc, char **argv)
{
        pthread_t status_update, cmpose_post, read_homeline, read_userline;

        pthread_create(&status_update, NULL, print_status, NULL);
        pthread_create(&cmpose_post, NULL, compose_post, NULL);
        pthread_create(&read_homeline, NULL, read_home_timeline, NULL);
        pthread_create(&read_userline, NULL, read_user_timeline, NULL);
        sleep(TEST_TIME); /* running load */
        stop = 1;
        pthread_join(status_update, NULL);
        pthread_join(cmpose_post, NULL);
        pthread_join(read_homeline, NULL);
        pthread_join(read_userline, NULL);

        return EXIT_SUCCESS;
}
