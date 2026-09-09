#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>

#define MAX_HISTORY 100
#define MAX_COMMAND 1024

char history[MAX_HISTORY][MAX_COMMAND];
int history_count = 0;
int history_position = -1;

struct termios original_terminal;

/*
 * Restore the original terminal settings.
 */
void disable_raw_mode(void) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &original_terminal);
}

/*
 * Enable non-canonical (raw) mode.
 */
void enable_raw_mode(void) {
    struct termios raw;

    if (tcgetattr(STDIN_FILENO, &original_terminal) == -1) {
        perror("tcgetattr");
        exit(1);
    }

    atexit(disable_raw_mode);

    raw = original_terminal;

    /*
     * Disable canonical mode and echo.
     */
    raw.c_lflag &= ~(ICANON | ECHO);

    /*
     * Read one character at a time.
     */
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr");
        exit(1);
    }
}

/*
 * Clear the current command from the terminal.
 */
void clear_current_line(int length) {
    printf("\r");

    printf("myshell> ");

    for (int i = 0; i < length; i++) {
        printf(" ");
    }

    printf("\rmyshell> ");
    fflush(stdout);
}

/*
 * Display a command on the current input line.
 */
void display_command(const char *command, int old_length) {
    printf("\r");

    printf("myshell> ");

    for (int i = 0; i < old_length; i++) {
        printf(" ");
    }

    printf("\rmyshell> %s", command);

    fflush(stdout);
}

/*
 * Store a command in history.
 */
void add_to_history(const char *command) {
    if (strlen(command) == 0) {
        return;
    }

    if (history_count < MAX_HISTORY) {
        strcpy(history[history_count], command);
        history_count++;
    } else {
        for (int i = 1; i < MAX_HISTORY; i++) {
            strcpy(history[i - 1], history[i]);
        }

        strcpy(history[MAX_HISTORY - 1], command);
    }
}

/*
 * Display all stored commands.
 */
void show_history(void) {
    printf("\n\nCommand History:\n");

    for (int i = 0; i < history_count; i++) {
        printf("%d  %s\n", i + 1, history[i]);
    }
}

/*
 * Read a command using non-canonical mode.
 */
int read_command(char *command) {
    int length = 0;
    int old_length = 0;

    history_position = history_count;

    memset(command, 0, MAX_COMMAND);

    while (1) {
        char c;

        if (read(STDIN_FILENO, &c, 1) != 1) {
            return 0;
        }

        /*
         * Enter key
         */
        if (c == '\n' || c == '\r') {
            command[length] = '\0';
            printf("\n");
            return 1;
        }

        /*
         * Backspace
         */
        if (c == 127 || c == 8) {
            if (length > 0) {
                length--;
                command[length] = '\0';

                printf("\b \b");
                fflush(stdout);
            }

            continue;
        }

        /*
         * Escape sequence handling.
         *
         * Up Arrow    = ESC [ A
         * Down Arrow  = ESC [ B
         */
        if (c == 27) {
            char sequence[2];

            if (read(STDIN_FILENO, &sequence[0], 1) != 1) {
                continue;
            }

            if (sequence[0] != '[') {
                continue;
            }

            if (read(STDIN_FILENO, &sequence[1], 1) != 1) {
                continue;
            }

            /*
             * Up Arrow
             */
            if (sequence[1] == 'A') {
                if (history_count == 0) {
                    continue;
                }

                if (history_position > 0) {
                    history_position--;
                }

                old_length = length;

                strcpy(command, history[history_position]);
                length = strlen(command);

                display_command(command, old_length);
            }

            /*
             * Down Arrow
             */
            else if (sequence[1] == 'B') {
                if (history_count == 0) {
                    continue;
                }

                if (history_position < history_count - 1) {
                    history_position++;

                    old_length = length;

                    strcpy(command, history[history_position]);
                    length = strlen(command);

                    display_command(command, old_length);
                } else {
                    history_position = history_count;

                    old_length = length;

                    command[0] = '\0';
                    length = 0;

                    clear_current_line(old_length);
                }
            }

            continue;
        }

        /*
         * Regular printable character
         */
        if (c >= 32 && c <= 126) {
            if (length < MAX_COMMAND - 1) {
                command[length++] = c;
                command[length] = '\0';

                putchar(c);
                fflush(stdout);
            }
        }
    }
}

/*
 * Main function.
 */
int main(void) {
    char command[MAX_COMMAND];

    enable_raw_mode();

    printf("========================================\n");
    printf("      TASK 14 - COMMAND HISTORY\n");
    printf("========================================\n");
    printf("Use Up/Down arrows to navigate history.\n");
    printf("Type 'history' to display commands.\n");
    printf("Type 'exit' to quit.\n\n");

    while (1) {
        printf("myshell> ");
        fflush(stdout);

        if (!read_command(command)) {
            break;
        }

        /*
         * Exit condition
         */
        if (strcmp(command, "exit") == 0) {
            printf("Exiting shell...\n");
            break;
        }

        /*
         * Display command history
         */
        if (strcmp(command, "history") == 0) {
            show_history();
            continue;
        }

        /*
         * Store the command in history.
         */
        if (strlen(command) > 0) {
            add_to_history(command);
        }
    }

    return 0;
}
