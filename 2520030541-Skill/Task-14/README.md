# Task 14: Command History and Arrow-Key Navigation

## Objective

To apply escape sequences, store command history, navigate through previous and next commands, update the input buffer, and test command recall functionality using the `termios` library and non-canonical terminal mode.

---

## Problem Statement

The objective of this task is to enhance a simple shell so that it can handle individual keyboard inputs and provide command-history functionality.

The shell should support:

- Storing previously entered commands.
- Navigating to previous commands using the **Up Arrow** key.
- Navigating to next commands using the **Down Arrow** key.
- Updating the current input buffer using the **Backspace** key.
- Displaying all stored commands using the `history` command.
- Exiting the shell using the `exit` command.

The task requires the use of `<termios.h>`, the `struct termios` data type, termios functions, escape sequences, and non-canonical terminal mode.

---

## Requirements

The implementation uses the following concepts and requirements:

1. Header file `<termios.h>`
2. `struct termios` structure
3. Key functions provided by the `termios` interface
4. Canonical and non-canonical (raw) terminal modes
5. Escape sequences for detecting arrow keys
6. Command-history storage
7. Input-buffer modification

---

## Concepts Used

### 1. `<termios.h>`

The `<termios.h>` header provides functions and structures for controlling terminal input and output behavior.

It is used in this program to change the terminal from normal canonical input mode to non-canonical mode.

```c
#include <termios.h>
```

---

### 2. `struct termios`

The `struct termios` structure stores terminal configuration settings.

The program maintains the original terminal configuration so that it can be restored when the program terminates.

```c
struct termios original_terminal;
```

A separate `struct termios` variable is used to configure the raw terminal mode.

```c
struct termios raw;
```

---

### 3. Canonical Mode

In canonical mode, the terminal normally collects an entire line of input.

The program receives the input after the user presses the Enter key.

This is the normal behavior experienced when typing commands in a standard terminal.

---

### 4. Non-Canonical Mode

In non-canonical mode, input can be read one character at a time.

This is important for this task because the program needs to recognize special keys such as:

- Up Arrow
- Down Arrow
- Backspace
- Enter

The program disables canonical mode using:

```c
raw.c_lflag &= ~(ICANON | ECHO);
```

It also configures the terminal to read one character at a time:

```c
raw.c_cc[VMIN] = 1;
raw.c_cc[VTIME] = 0;
```

---

### 5. Escape Sequences

Special keyboard keys such as the arrow keys generate escape sequences.

The program detects the Escape character:

```c
if (c == 27)
```

It then checks the following characters to determine which arrow key was pressed.

The important escape sequences used are:

```text
Up Arrow    → ESC [ A
Down Arrow  → ESC [ B
```

This allows the shell to identify the Up and Down Arrow keys.

---

## Functions Used

| Function | Purpose |
|---|---|
| `tcgetattr()` | Gets the current terminal settings |
| `tcsetattr()` | Applies modified terminal settings |
| `atexit()` | Registers a function to restore terminal settings |
| `read()` | Reads individual characters from the terminal |
| `printf()` | Displays messages and commands |
| `strlen()` | Determines the length of a command |
| `strcpy()` | Copies commands into the history array |
| `strcmp()` | Compares the entered command with `history` and `exit` |
| `memset()` | Initializes the command buffer |
| `exit()` | Terminates the program when an error occurs |

---

## Command History

The program stores commands in an array:

```c
char history[MAX_HISTORY][MAX_COMMAND];
```

The program supports up to:

```text
100 commands
```

Each command can contain up to:

```text
1023 characters
```

The number of currently stored commands is maintained using:

```c
int history_count = 0;
```

Whenever a non-empty command is entered, it is added to the history.

---

## Input Buffer

The current command being typed is stored in:

```c
char command[MAX_COMMAND];
```

The program updates this buffer whenever the user:

- Types a character.
- Presses Backspace.
- Recalls an older command.
- Navigates to a newer command.
- Clears the current command.

---

## Working of the Program

### Step 1: Save Terminal Settings

The program first obtains the current terminal configuration using:

```c
tcgetattr(STDIN_FILENO, &original_terminal);
```

The original settings are saved so they can be restored later.

---

### Step 2: Enable Non-Canonical Mode

The program creates a modified copy of the terminal settings.

Canonical mode and automatic echoing are disabled:

```c
raw.c_lflag &= ~(ICANON | ECHO);
```

The terminal is configured to read one character at a time.

```c
raw.c_cc[VMIN] = 1;
raw.c_cc[VTIME] = 0;
```

The modified settings are then applied using:

```c
tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
```

---

### Step 3: Read Individual Characters

The program reads input one character at a time:

```c
read(STDIN_FILENO, &c, 1);
```

This makes it possible to identify special keys before the user presses Enter.

---

### Step 4: Handle Normal Characters

If the user enters a normal printable character, it is added to the current command buffer.

For example:

```text
myshell> hello
```

The characters are stored in the command buffer.

---

### Step 5: Handle Backspace

When Backspace is pressed, the program removes the last character from the input buffer.

For example:

```text
hello
```

can be changed to:

```text
hell
```

This demonstrates updating the input buffer.

---

### Step 6: Handle Up Arrow

When the Up Arrow is pressed, the program checks the command history.

The most recently stored command is recalled first.

For example, if the history contains:

```text
hello
world
```

pressing the Up Arrow recalls:

```text
world
```

Pressing it again recalls:

```text
hello
```

---

### Step 7: Handle Down Arrow

The Down Arrow moves forward through the command history.

For example:

```text
hello
world
```

If `hello` is currently displayed and the Down Arrow is pressed, the next command:

```text
world
```

is displayed.

Pressing Down Arrow again moves beyond the latest stored command and clears the input buffer.

---

### Step 8: Store Commands

When the user presses Enter, the current command is completed.

If the command is not empty, it is added to the history array.

For example:

```text
hello
world
```

becomes:

```text
1  hello
2  world
```

---

### Step 9: Display History

When the user enters:

```text
history
```

the program displays all stored commands.

Example:

```text
Command History:
1  hello
2  world
3  test
```

---

### Step 10: Exit the Shell

When the user enters:

```text
exit
```

the program prints:

```text
Exiting shell...
```

and terminates.

Before termination, the original terminal settings are restored.

---

## Program Flow

```text
                    START
                      |
                      v
          Save Terminal Settings
                      |
                      v
          Enable Non-Canonical Mode
                      |
                      v
              Display Prompt
                      |
                      v
             Read One Character
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      Character    Arrow Key    Enter
          |           |           |
          v           v           v
      Add to       Process      Store
      Buffer       Escape       Command
                       |
                +------+------+
                |             |
                v             v
             Up Arrow      Down Arrow
                |             |
                v             v
          Previous Cmd     Next Cmd
                |             |
                +------+------+
                       |
                       v
                 Display Buffer
                       |
                       v
                  Next Input
                       |
                       v
                  `exit`?
                  /      \
                No        Yes
                |          |
                v          v
          Continue     Restore
                       Terminal
                           |
                           v
                          END
```

---

## Testing the Functionality

### Test 1: Store History

Commands entered:

```text
hello
world
```

Both commands are stored in the command history.

---

### Test 2: Navigate Previous Commands

After entering:

```text
hello
world
```

press the **Up Arrow** key.

The most recent command is displayed:

```text
world
```

Press **Up Arrow** again.

The previous command is displayed:

```text
hello
```

---

### Test 3: Navigate Next Commands

While an older command is displayed, press the **Down Arrow** key.

The shell moves toward the next command in the history.

When the end of the history is reached, pressing Down Arrow again clears the input buffer.

---

### Test 4: Update the Input Buffer

An old command can be recalled using the Up Arrow.

The recalled command can then be modified using Backspace.

For example:

```text
hello
```

can be modified to:

```text
hell
```

Pressing Enter stores the modified command as a new history entry.

---

### Test 5: Test Command Recall

Enter:

```text
history
```

The shell displays the complete command history.

Example:

```text
Command History:
1  hello
2  world
3  hello
4  helloworld
5  helllo
6  helo
7  helllo
```

The exact history depends on the commands entered during testing.

---

### Test 6: Exit

Enter:

```text
exit
```

The shell terminates with:

```text
Exiting shell...
```

---

## Sample Output

A sample execution of the program is:

```text
========================================
      TASK 14 - COMMAND HISTORY
========================================
Use Up/Down arrows to navigate history.
Type 'history' to display commands.
Type 'exit' to quit.

myshell> hello

myshell> world

myshell> hello

myshell> helloworld

myshell> helllo

myshell> helo

myshell> helllo

myshell> history


Command History:

1  hello
2  world
3  hello
4  helloworld
5  helllo
6  helo
7  helllo

myshell> exit
Exiting shell...
```

The exact output and command-history entries depend on the commands entered during execution.

---

## Source File

The C source code for this task is:

```text
task14_command_history.c
```

---

## Compilation

The program can be compiled using:

```bash
gcc task14_command_history.c -o task14_command_history
```

---

## Execution

The compiled program can be executed using:

```bash
./task14_command_history
```

---

## Key Learning

This task demonstrates how a shell can process keyboard input at the character level instead of waiting for a complete line.

The main concepts demonstrated are:

```text
termios
   ↓
Non-Canonical Mode
   ↓
Read Individual Characters
   ↓
Detect Escape Sequences
   ↓
Handle Up/Down Arrow Keys
   ↓
Maintain Command History
   ↓
Update Input Buffer
```

The program therefore demonstrates the basic mechanisms required for interactive command-history functionality in a shell.

---

## Conclusion

Task 14 successfully demonstrates command-history management and interactive keyboard handling using the `termios` interface.

The program uses non-canonical terminal mode to read individual keystrokes, recognizes escape sequences generated by the arrow keys, stores previously entered commands, allows navigation through command history, supports input-buffer modification using Backspace, and displays the complete history using the `history` command.

The task provides a practical understanding of terminal control, escape sequences, input buffering, and command-history implementation in a shell.
