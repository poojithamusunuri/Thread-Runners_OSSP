#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

#define NUM_CLIENTS 3
#define BUFFER_SIZE 256

const char *client_to_server[NUM_CLIENTS] = {
    "client1_to_server",
    "client2_to_server",
    "client3_to_server"
};

const char *server_to_client[NUM_CLIENTS] = {
    "server_to_client1",
    "server_to_client2",
    "server_to_client3"
};

pid_t handler_pids[NUM_CLIENTS];

volatile sig_atomic_t server_running = 1;

void handle_sigint(int sig)
{
    (void)sig;

    printf("\nServer received SIGINT.\n");
    printf("Shutting down server...\n");

    server_running = 0;
}

void handle_sigchld(int sig)
{
    (void)sig;

    while (waitpid(-1, NULL, WNOHANG) > 0) {
        printf("Handler child terminated.\n");
    }
}

void handle_sigusr1(int sig)
{
    (void)sig;
}

/*
 * Handler process for one client.
 */
void client_handler(int client_number)
{
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE];

    const char *read_fifo = client_to_server[client_number];
    const char *write_fifo = server_to_client[client_number];

    signal(SIGUSR1, handle_sigusr1);
    signal(SIGINT, SIG_DFL);

    printf("Handler %d started. PID = %d\n",
           client_number + 1, getpid());

    /*
     * Open both FIFOs in read/write mode.
     * This avoids blocking while establishing the FIFO connection.
     */
    int read_fd = open(read_fifo, O_RDWR);

    if (read_fd == -1) {
        perror("open client-to-server FIFO");
        exit(EXIT_FAILURE);
    }

    int write_fd = open(write_fifo, O_RDWR);

    if (write_fd == -1) {
        perror("open server-to-client FIFO");
        close(read_fd);
        exit(EXIT_FAILURE);
    }

    /*
     * Store handler PID so the client knows
     * which process to notify using SIGUSR1.
     */
    char pid_filename[64];

    snprintf(pid_filename,
             sizeof(pid_filename),
             "handler%d.pid",
             client_number + 1);

    FILE *pid_file = fopen(pid_filename, "w");

    if (pid_file != NULL) {
        fprintf(pid_file, "%d\n", getpid());
        fclose(pid_file);
    }

    while (server_running) {

        memset(buffer, 0, sizeof(buffer));

        ssize_t bytes_read = read(read_fd, buffer, sizeof(buffer) - 1);

        if (bytes_read > 0) {

            buffer[bytes_read] = '\0';

            printf("\n[Handler %d] Message received: %s",
                   client_number + 1, buffer);

            snprintf(response,
                     sizeof(response),
                     "Server response to Client %d: Message received successfully.",
                     client_number + 1);

            write(write_fd, response, strlen(response) + 1);

            printf("[Handler %d] Response sent to Client %d.\n",
                   client_number + 1,
                   client_number + 1);
        }
    }

    close(read_fd);
    close(write_fd);

    unlink(pid_filename);

    printf("Handler %d exiting.\n", client_number + 1);

    exit(EXIT_SUCCESS);
}

int main(void)
{
    printf("========================================\n");
    printf("       TASK 16 - FIFO IPC SERVER\n");
    printf("========================================\n\n");

    /*
     * Install signal handlers.
     */
    signal(SIGINT, handle_sigint);
    signal(SIGCHLD, handle_sigchld);
    signal(SIGUSR1, handle_sigusr1);

    /*
     * Create the six named pipes.
     */
    for (int i = 0; i < NUM_CLIENTS; i++) {

        unlink(client_to_server[i]);
        unlink(server_to_client[i]);

        if (mkfifo(client_to_server[i], 0666) == -1) {
            if (errno != EEXIST) {
                perror("mkfifo client-to-server");
                return EXIT_FAILURE;
            }
        }

        if (mkfifo(server_to_client[i], 0666) == -1) {
            if (errno != EEXIST) {
                perror("mkfifo server-to-client");
                return EXIT_FAILURE;
            }
        }
    }

    printf("Six FIFOs created successfully.\n\n");

    /*
     * Create three handler child processes.
     */
    for (int i = 0; i < NUM_CLIENTS; i++) {

        pid_t pid = fork();

        if (pid == -1) {
            perror("fork");
            return EXIT_FAILURE;
        }

        if (pid == 0) {
            client_handler(i);
        }

        handler_pids[i] = pid;

        printf("Handler %d created with PID %d.\n",
               i + 1, pid);
    }

    printf("\nServer is ready for three clients.\n");
    printf("Press Ctrl+C to stop the server.\n");

    /*
     * Keep the main server process alive.
     */
    while (server_running) {
        pause();
    }

    /*
     * Terminate handler processes.
     */
    printf("\nTerminating handler processes...\n");

    for (int i = 0; i < NUM_CLIENTS; i++) {
        if (handler_pids[i] > 0) {
            kill(handler_pids[i], SIGTERM);
        }
    }

    /*
     * Wait for children.
     */
    for (int i = 0; i < NUM_CLIENTS; i++) {
        waitpid(handler_pids[i], NULL, 0);
    }

    /*
     * Remove FIFOs.
     */
    for (int i = 0; i < NUM_CLIENTS; i++) {
        unlink(client_to_server[i]);
        unlink(server_to_client[i]);
    }

    printf("All FIFOs removed.\n");
    printf("Server terminated successfully.\n");

    return 0;
}
