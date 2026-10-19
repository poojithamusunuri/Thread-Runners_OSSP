#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static void pause_seconds(unsigned seconds) {
    struct timespec req = {.tv_sec = (time_t)seconds, .tv_nsec = 0};
    while (nanosleep(&req, &req) == -1 && errno == EINTR) {}
}

static int write_all(int fd, const char *buffer, size_t length) {
    size_t offset = 0;
    while (offset < length) {
        ssize_t written = write(fd, buffer + offset, length - offset);
        if (written < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (written == 0) return -1;
        offset += (size_t)written;
    }
    return 0;
}

static int zombie_demo(void) {
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0) _exit(0);
    printf("LAB_PARENT_PID=%ld\nLAB_CHILD_PID=%ld\n", (long)getpid(), (long)child);
    fflush(stdout);
    /* Intentionally do not wait: the child remains a zombie until cleanup. */
    pause_seconds(25);
    (void)waitpid(child, NULL, 0);
    return 0;
}

static int orphan_demo(void) {
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child > 0) {
        printf("LAB_PARENT_PID=%ld\nLAB_CHILD_PID=%ld\n", (long)getpid(), (long)child);
        fflush(stdout);
        return 0;
    }
    printf("LAB_ORPHAN_PID=%ld\nLAB_INITIAL_PPID=%ld\n", (long)getpid(), (long)getppid());
    fflush(stdout);
    pause_seconds(25);
    return 0;
}

static int pipeline_demo(void) {
    int fds[2];
    if (pipe(fds) == -1) { perror("pipe"); return 1; }
    pid_t writer = fork();
    if (writer < 0) { perror("fork writer"); close(fds[0]); close(fds[1]); return 1; }
    if (writer == 0) {
        close(fds[0]);
        const char msg[] = "ProcScope controlled pipeline message\n";
        if (write_all(fds[1], msg, sizeof(msg) - 1) < 0) {
            perror("write pipeline message");
            close(fds[1]);
            _exit(1);
        }
        close(fds[1]); pause_seconds(20); _exit(0);
    }
    pid_t reader = fork();
    if (reader < 0) { perror("fork reader"); kill(writer, SIGTERM); close(fds[0]); close(fds[1]); (void)waitpid(writer, NULL, 0); return 1; }
    if (reader == 0) {
        close(fds[1]); char buf[128]; while (read(fds[0], buf, sizeof(buf)) > 0) {} close(fds[0]); pause_seconds(20); _exit(0);
    }
    close(fds[0]); close(fds[1]);
    printf("LAB_PARENT_PID=%ld\nLAB_WRITER_PID=%ld\nLAB_READER_PID=%ld\n", (long)getpid(), (long)writer, (long)reader);
    fflush(stdout);
    pause_seconds(20);
    (void)waitpid(writer, NULL, 0); (void)waitpid(reader, NULL, 0);
    return 0;
}

static void *thread_worker(void *arg) {
    long number = (long)arg;
    printf("LAB_THREAD_STARTED=%ld\n", number); fflush(stdout);
    pause_seconds(20);
    return NULL;
}
static int threads_demo(void) {
    pthread_t threads[3];
    printf("LAB_PARENT_PID=%ld\n", (long)getpid()); fflush(stdout);
    for (long i = 0; i < 3; i++) {
        int rc = pthread_create(&threads[i], NULL, thread_worker, (void *)i);
        if (rc != 0) { fprintf(stderr, "pthread_create: %s\n", strerror(rc)); return 1; }
    }
    pause_seconds(20);
    for (int i = 0; i < 3; i++) (void)pthread_join(threads[i], NULL);
    return 0;
}

static int fork_exec_demo(void) {
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0) { execlp("sleep", "sleep", "20", (char *)NULL); perror("execlp sleep"); _exit(127); }
    printf("LAB_PARENT_PID=%ld\nLAB_EXEC_CHILD_PID=%ld\n", (long)getpid(), (long)child); fflush(stdout);
    pause_seconds(20);
    (void)waitpid(child, NULL, 0);
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "Usage: %s <zombie|orphan|pipeline|threads|fork-exec>\n", argv[0]); return 2; }
    if (strcmp(argv[1], "zombie") == 0) return zombie_demo();
    if (strcmp(argv[1], "orphan") == 0) return orphan_demo();
    if (strcmp(argv[1], "pipeline") == 0) return pipeline_demo();
    if (strcmp(argv[1], "threads") == 0) return threads_demo();
    if (strcmp(argv[1], "fork-exec") == 0) return fork_exec_demo();
    fprintf(stderr, "Unknown experiment.\n"); return 2;
}
