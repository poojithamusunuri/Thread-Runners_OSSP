#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>

#define BUFFER_SIZE 256

const char *client_to_server[] = {
    "client1_to_server",
    "client2_to_server",
    "client3_to_server"
};

const char *server_to_client[] = {
    "server_to_client1",
    "server_to_client2",
    "server_to_client3"
};

volatile sig_atomic_t client_running = 1;

void handle_sigint(int sig)
{
    (void)sig;

    printf("\nClient received SIGINT.\n");
    printf("Client shutting down...\n");

    client_running = 0;
}

void handle_sigusr1(int sig)
{
    (void)sig;

    printf("\nClient received SIGUSR1 from server.\n");
}

int main(int argc, char *argv[])
{
    if (argc != 2) {
        printf("Usage: %s <client_number>\n", argv[0]);
        printf("Example: %s 1\n", argv[0]);
        return EXIT_FAILURE;
    }

    int client_number = atoi(argv[1]);

    if (client_number < 1 || client_number > 3) {
        printf("Client number must be 1, 2, or 3.\n");
        return EXIT_FAILURE;
    }

    int index = client_number - 1;

    signal(SIGINT, handle_sigint);
    signal(SIGUSR1, handle_sigusr1);

    printf("========================================\n");
    printf("       TASK 16 - FIFO IPC CLIENT\n");
    printf("========================================\n");

    printf("Client %d started.\n", client_number);
    printf("Client PID: %d\n\n", getpid());

    /*
     * Open the two FIFOs.
     */
    int write_fd = open(client_to_server[index], O_RDWR);

    if (write_fd == -1) {
        perror("open client-to-server FIFO");
        return EXIT_FAILURE;
    }

    int read_fd = open(server_to_client[index], O_RDWR);

    if (read_fd == -1) {
        perror("open server-to-client FIFO");
        close(write_fd);
        return EXIT_FAILURE;
    }

    /*
     * Read the handler PID.
     */
    char pid_filename[64];

    snprintf(pid_filename,
             sizeof(pid_filename),
             "handler%d.pid",
             client_number);

    FILE *pid_file = NULL;

    /*
     * Wait until the server creates the PID file.
     */
    while ((pid_file = fopen(pid_filename, "r")) == NULL) {
        sleep(1);
    }

    pid_t handler_pid;

    if (fscanf(pid_file, "%d", &handler_pid) != 1) {
        printf("Unable to read handler PID.\n");
        fclose(pid_file);
        close(write_fd);
        close(read_fd);
        return EXIT_FAILURE;
    }

    fclose(pid_file);

    printf("Connected to Handler %d (PID %d).\n",
           client_number,
           handler_pid);

    printf("Type messages to send to the server.\n");
    printf("Type 'exit' to terminate the client.\n\n");

    while (client_running) {

        char message[BUFFER_SIZE];
        char response[BUFFER_SIZE];

        printf("Client %d > ", client_number);
        fflush(stdout);

        if (fgets(message, sizeof(message), stdin) == NULL) {
            break;
        }

        if (strncmp(message, "exit", 4) == 0) {
            break;
        }

        /*
         * Send message to the server.
         */
        write(write_fd, message, strlen(message));

        /*
         * Notify the corresponding handler using SIGUSR1.
         */
        kill(handler_pid, SIGUSR1);

        /*
         * Read server response.
         */
        memset(response, 0, sizeof(response));

        ssize_t bytes_read =
            read(read_fd, response, sizeof(response) - 1);

        if (bytes_read > 0) {
            response[bytes_read] = '\0';

            printf("Server > %s\n", response);
        }
    }

    close(write_fd);
    close(read_fd);

    printf("\nClient %d terminated.\n", client_number);

    return 0;
}
