# Task 12: Interactive Shell Main Loop

## Objective

To create and test a basic interactive shell loop that displays a prompt, reads user input, handles the `exit` condition, and repeatedly accepts commands from the user.

---

## Problem Statement

The task is to implement a basic interactive command-line loop.

The program should:

1. Display a shell prompt.
2. Read input entered by the user.
3. Remove the newline character from the input.
4. Check whether the user entered `exit`.
5. Terminate the shell when `exit` is entered.
6. Otherwise, display the command entered by the user.
7. Continue displaying the prompt until the user chooses to exit.

---

## Libraries Used

| Header File | Functions Used | Purpose |
|---|---|---|
| `<stdio.h>` | `printf()`, `fgets()`, `fflush()` | Display the prompt and read user input |
| `<string.h>` | `strcmp()`, `strcspn()` | Compare and manipulate the input command |

---

## Functions Used

### `printf()`

The `printf()` function is used to display the shell prompt and output messages.

```c
printf("myshell> ");
```

---

### `fflush()`

The `fflush()` function is used to ensure that the prompt is displayed immediately.

```c
fflush(stdout);
```

---

### `fgets()`

The `fgets()` function reads the command entered by the user.

```c
fgets(command, sizeof(command), stdin);
```

---

### `strcspn()`

The `strcspn()` function is used to locate the newline character and remove it from the input string.

```c
command[strcspn(command, "\n")] = '\0';
```

---

### `strcmp()`

The `strcmp()` function compares the user's input with the string `"exit"`.

```c
if (strcmp(command, "exit") == 0)
```

If the comparison returns `0`, the user has entered `exit`.

---

## Program Logic

The program uses an infinite `while` loop to continuously accept user input.

The basic flow is:

```text
START
  |
  v
Display "myshell> "
  |
  v
Read User Input
  |
  v
Remove Newline
  |
  v
Is Input "exit"?
  |
  +-------- Yes --------> Display "Exiting shell..."
  |                              |
  |                              v
  |                             END
  |
  No
  |
  v
Display "You entered: command"
  |
  v
Return to Prompt
```

---

## Working of the Program

### Step 1: Start the Program

The program starts execution in the `main()` function.

A character array is created to store the command entered by the user.

```c
char command[100];
```

---

### Step 2: Display the Shell Prompt

The program enters an infinite `while` loop and displays:

```text
myshell>
```

The prompt is immediately displayed using:

```c
printf("myshell> ");
fflush(stdout);
```

---

### Step 3: Read User Input

The program waits for the user to enter a command.

```c
fgets(command, sizeof(command), stdin);
```

For example, if the user enters:

```text
hello
```

the input is stored in the `command` array.

---

### Step 4: Remove the Newline

When `fgets()` reads input, it normally stores the newline character produced when the user presses Enter.

The program removes this newline using:

```c
command[strcspn(command, "\n")] = '\0';
```

This makes command comparison easier.

---

### Step 5: Check the Exit Condition

The program checks whether the entered command is:

```text
exit
```

using:

```c
if (strcmp(command, "exit") == 0)
```

If the user enters `exit`, the program displays:

```text
Exiting shell...
```

and terminates the loop using:

```c
break;
```

---

### Step 6: Process Other Input

If the user enters anything other than `exit`, the program displays the entered command.

For example:

```text
myshell> hello
You entered: hello
```

The program then returns to the beginning of the loop and displays the prompt again.

---

## Source Code

The complete source code is stored in:

```text
task12_shell_loop.c
```

The program contains:

- An interactive `while` loop
- Shell prompt display
- User input using `fgets()`
- Newline removal using `strcspn()`
- Exit checking using `strcmp()`
- Command display
- Program termination using `break`

---

## Compilation

The program can be compiled using:

```bash
gcc task12_shell_loop.c -o task12_shell_loop
```

---

## Execution

The compiled program can be executed using:

```bash
./task12_shell_loop
```

---

## Test Cases

### Test Case 1: Normal Input

Input:

```text
hello
```

Expected output:

```text
myshell> hello
You entered: hello
```

---

### Test Case 2: Another Command

Input:

```text
ls
```

Expected output:

```text
myshell> ls
You entered: ls
```

The program only displays the command at this stage. It does not actually execute the operating-system command.

---

### Test Case 3: Exit

Input:

```text
exit
```

Expected output:

```text
myshell> exit
Exiting shell...
```

The program then terminates.

---

## Sample Execution

```text
myshell> hello
You entered: hello
myshell> ls
You entered: ls
myshell> exit
Exiting shell...
```

---

## Important Observation

This task implements the **basic interactive loop** of a shell.

At this stage, commands such as `ls` are not actually executed. They are only read as input and displayed back to the user.

The main purpose is to establish the control flow required for an interactive shell.

---

## Key Learning

This task demonstrates:

- Creating an infinite interactive loop
- Displaying a command prompt
- Reading user input
- Removing unwanted newline characters
- Comparing strings
- Handling an exit condition
- Controlling program flow using `break`

---

## Conclusion

The interactive shell loop was successfully implemented and tested.

The program continuously displays the `myshell>` prompt, accepts user input, displays the entered command, and terminates when the user enters `exit`.

This provides the basic control structure required for developing a more functional command-line shell.
