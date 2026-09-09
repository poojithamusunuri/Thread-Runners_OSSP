#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    int fd[2];
    pid_t pid1, pid2;

    printf("========================================\n");
    printf("       TASK 15 - PIPE PIPELINE\n");
    printf("========================================\n\n");

    printf("Executing: ls -l | grep \".c\"\n\n");

    // Create a pipe
    if (pipe(fd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    // Create first child process
    pid1 = fork();

    if (pid1 < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid1 == 0) {
        // First child: execute ls -l

        // Close unused read end
        close(fd[0]);

        // Redirect standard output to pipe
        dup2(fd[1], STDOUT_FILENO);

        // Close original write end
        close(fd[1]);

        execlp("ls", "ls", "-l", NULL);

        // If exec fails
        perror("execlp ls");
        exit(EXIT_FAILURE);
    }

    // Create second child process
    pid2 = fork();

    if (pid2 < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid2 == 0) {
        // Second child: execute grep ".c"

        // Close unused write end
        close(fd[1]);

        // Redirect standard input from pipe
        dup2(fd[0], STDIN_FILENO);

        // Close original read end
        close(fd[0]);

        execlp("grep", "grep", ".c", NULL);

        // If exec fails
        perror("execlp grep");
        exit(EXIT_FAILURE);
    }

    // Parent process closes both pipe ends
    close(fd[0]);
    close(fd[1]);

    // Wait for both child processes
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);

    printf("\nPipeline execution completed.\n");

    return 0;
}
