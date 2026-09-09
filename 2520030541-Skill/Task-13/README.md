# Task 13: Command Processor

## Objective

To implement a simple command processor that accepts commands from the user and performs different actions based on the command entered.

The program demonstrates how a basic shell can recognize predefined commands, execute the corresponding functionality, handle unknown commands, and terminate when the `exit` command is entered.

---

## Problem Statement

A command processor is a basic component of a shell that reads a command entered by the user and determines what action should be performed.

In this program, a simple shell-like command processor is implemented with the following commands:

- `hello` - Displays a greeting message.
- `help` - Displays the list of available commands.
- `exit` - Terminates the command processor.

If the user enters a command that is not recognized, the program displays an appropriate message.

Empty input is also handled without executing any command.

---

## Concepts Used

### 1. Command Processing

The program continuously reads input from the user and compares the entered command with a set of predefined commands.

Based on the command, the appropriate operation is performed.

---

### 2. String Comparison

String comparison is used to determine which command the user entered.

The entered command is compared with predefined command names such as:

```c
hello
help
exit
```

---

### 3. Looping

The command processor runs continuously inside a loop.

The loop allows the user to enter multiple commands one after another until the `exit` command is entered.

---

### 4. Conditional Statements

Conditional statements are used to identify the command entered by the user.

For example:

```text
hello → Display greeting
help  → Display available commands
exit  → Terminate the program
```

If none of the predefined commands match, the program reports the command as unknown.

---

## Available Commands

| Command | Description |
|---------|-------------|
| `hello` | Displays a greeting message |
| `help` | Displays the available commands |
| `exit` | Exits the command processor |

---

## Program Workflow

```text
                    START
                      |
                      v
              Display shell prompt
                      |
                      v
                Read command
                      |
                      v
                Is input empty?
                  /       \
                Yes        No
                 |          |
                 v          v
             Do nothing   Compare command
                              |
                +-------------+-------------+
                |             |             |
                v             v             v
             "hello"        "help"        "exit"
                |             |             |
                v             v             v
          Display greeting  Show help    Exit program
                |             |             
                +-------------+
                      |
                      v
                Unknown command
                      |
                      v
              Display error message
                      |
                      v
              Return to shell prompt
```

---

## Working of the Program

### Step 1: Start the Command Processor

The program starts and displays a shell-like prompt:

```text
myshell>
```

The user can enter a command after the prompt.

---

### Step 2: Enter `hello`

When the user enters:

```text
hello
```

the program recognizes the command and displays:

```text
Hello! Welcome to my shell.
```

---

### Step 3: Enter `help`

When the user enters:

```text
help
```

the program displays the list of supported commands:

```text
Available commands:
  hello - Display greeting
  help  - Display available commands
  exit  - Exit the shell
```

---

### Step 4: Enter an Unknown Command

If a command that is not supported is entered, for example:

```text
abc
```

the program displays:

```text
Unknown command: abc
```

The command processor then returns to the prompt and waits for another command.

---

### Step 5: Enter `exit`

When the user enters:

```text
exit
```

the program terminates and displays:

```text
Exiting shell...
```

---

### Step 6: Empty Input

If the user presses Enter without entering a command, the program handles the empty input without executing a command.

The program displays:

```text
Do nothing for empty input.
```

and returns to the shell prompt.

---

## Expected Output

A sample execution of the program is:

```text
myshell> hello!
Unknown command: hello!

myshell> hello
Hello! Welcome to my shell.

myshell> abc
Unknown command: abc

myshell> help
Available commands:
  hello - Display greeting
  help  - Display available commands
  exit  - Exit the shell

myshell> 
Do nothing for empty input.

myshell> exit
Exiting shell...
```

The output may vary depending on the commands entered by the user.

---

## Source Code

The source code for this task is:

```text
task13_command_processor.c
```

The compiled executable is:

```text
task13_command_processor
```

---

## Compilation

The program can be compiled using:

```bash
gcc task13_command_processor.c -o task13_command_processor
```

---

## Execution

After compilation, the program can be executed using:

```bash
./task13_command_processor
```

The shell prompt appears as:

```text
myshell>
```

Commands can then be entered interactively.

---

## Testing

The program was tested using different types of input.

### Test 1: Valid Command

Input:

```text
hello
```

Output:

```text
Hello! Welcome to my shell.
```

---

### Test 2: Help Command

Input:

```text
help
```

Output:

```text
Available commands:
  hello - Display greeting
  help  - Display available commands
  exit  - Exit the shell
```

---

### Test 3: Unknown Command

Input:

```text
abc
```

Output:

```text
Unknown command: abc
```

---

### Test 4: Empty Input

Input:

```text

```

Output:

```text
Do nothing for empty input.
```

---

### Test 5: Exit Command

Input:

```text
exit
```

Output:

```text
Exiting shell...
```

---

## Key Learning

This task demonstrates the basic working of a command processor.

The important concepts learned are:

1. Reading user input.
2. Processing commands.
3. Comparing strings.
4. Using conditional statements to select actions.
5. Using loops to repeatedly accept commands.
6. Handling unknown commands.
7. Handling empty input.
8. Terminating the program using an exit command.

---

## Conclusion

The command processor was successfully implemented as a simple shell-like program.

The program accepts commands from the user, recognizes predefined commands such as `hello`, `help`, and `exit`, handles unknown commands appropriately, and continues accepting input until the `exit` command is entered.

This provides a basic understanding of how command processing works inside a simple shell.
