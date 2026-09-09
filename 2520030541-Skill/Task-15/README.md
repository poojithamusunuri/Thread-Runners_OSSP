# Task 15: Pipe and Pipeline Execution

## Objective

To demonstrate inter-process communication using the `pipe()` system call and to execute a command pipeline using `fork()`, `dup2()`, `exec()`, and `waitpid()`.

---

## Problem Statement

A shell allows multiple commands to be connected using a pipe (`|`).

For example:

```bash
ls -l | grep ".c"
```

In this pipeline:

- `ls -l` lists the files and directories.
- Its output is sent through a pipe.
- `grep ".c"` receives the output from the pipe.
- `grep` displays only the lines containing `.c`.

This practical demonstrates how such a pipeline can be implemented using system calls in C.

---

## Concepts Used

### 1. `pipe()`

The `pipe()` system call creates a communication channel between processes.

It provides two file descriptors:

```c
fd[0]
```

for reading from the pipe, and

```c
fd[1]
```

for writing to the pipe.

The general form used in the program is:

```c
pipe(fd);
```

---

### 2. `fork()`

The `fork()` system call creates a new child process.

The program creates two child processes:

- The first child executes `ls -l`.
- The second child executes `grep ".c"`.

The parent process waits for both child processes to finish.

---

### 3. `dup2()`

The `dup2()` system call is used to redirect standard input or standard output.

For the first child:

```c
dup2(fd[1], STDOUT_FILENO);
```

This redirects the output of `ls -l` into the pipe.

For the second child:

```c
dup2(fd[0], STDIN_FILENO);
```

This redirects the input of `grep` from the pipe.

---

### 4. `execlp()`

The `execlp()` function is used to execute external commands.

The first child executes:

```c
execlp("ls", "ls", "-l", NULL);
```

The second child executes:

```c
execlp("grep", "grep", ".c", NULL);
```

After a successful `exec()` call, the current child process is replaced by the new program.

---

### 5. `waitpid()`

The `waitpid()` system call allows the parent process to wait for a particular child process to complete.

The program uses:

```c
waitpid(pid1, NULL, 0);
waitpid(pid2, NULL, 0);
```

This ensures that the parent waits for both child processes.

---

## System Calls and Functions Used

| Function / System Call | Purpose |
|---|---|
| `pipe()` | Creates a communication channel between processes |
| `fork()` | Creates child processes |
| `dup2()` | Redirects standard input/output |
| `execlp()` | Executes an external command |
| `waitpid()` | Waits for child processes to complete |
| `close()` | Closes unused pipe file descriptors |
| `perror()` | Displays error messages |
| `exit()` | Terminates the process |

---

## Pipeline Demonstrated

The program demonstrates the following shell pipeline:

```bash
ls -l | grep ".c"
```

The data flow is:

```text
             ls -l
               |
               | Standard Output
               v
        +---------------+
        |     PIPE      |
        +---------------+
               |
               | Standard Input
               v
          grep ".c"
               |
               v
        Matching output
```

---

## Program Workflow

The program follows these steps:

```text
                    START
                      |
                      v
                Create Pipe
                      |
                      v
                 fork()
                /      \
               /        \
              v          v
        Child 1       Child 2
           |              |
           v              v
         ls -l        grep ".c"
           |              ^
           |              |
           +--> PIPE -----+
                      |
                      v
               Parent waits
                      |
                      v
               Pipeline ends
                      |
                      v
                     END
```

---

## Working of the Program

### Step 1: Create the Pipe

The program first creates a pipe:

```c
int fd[2];

pipe(fd);
```

The pipe provides two ends:

```text
fd[0] → Read end
fd[1] → Write end
```

---

### Step 2: Create the First Child

The first `fork()` creates a child process.

The first child is responsible for executing:

```bash
ls -l
```

The child closes the unused read end:

```c
close(fd[0]);
```

Then its standard output is redirected to the pipe:

```c
dup2(fd[1], STDOUT_FILENO);
```

Therefore, the output produced by `ls -l` goes into the pipe instead of directly to the terminal.

The child then executes:

```c
execlp("ls", "ls", "-l", NULL);
```

---

### Step 3: Create the Second Child

The second `fork()` creates another child process.

This child is responsible for executing:

```bash
grep ".c"
```

The child closes the unused write end:

```c
close(fd[1]);
```

Its standard input is redirected from the pipe:

```c
dup2(fd[0], STDIN_FILENO);
```

The child then executes:

```c
execlp("grep", "grep", ".c", NULL);
```

Therefore, `grep` receives the output of `ls -l` from the pipe.

---

### Step 4: Parent Closes the Pipe

The parent process does not need either end of the pipe, so it closes both:

```c
close(fd[0]);
close(fd[1]);
```

---

### Step 5: Parent Waits for the Children

The parent waits for both child processes:

```c
waitpid(pid1, NULL, 0);
waitpid(pid2, NULL, 0);
```

After both child processes finish, the parent prints:

```text
Pipeline execution completed.
```

---

## Process Relationship

The process relationship can be represented as:

```text
                  Parent Process
                       |
                +------+------+
                |             |
              fork()        fork()
                |             |
                v             v
             Child 1       Child 2
                |             |
                v             v
              ls -l        grep ".c"
                |             ^
                |             |
                +---- PIPE ---+
```

The first child writes data into the pipe, while the second child reads the data from the pipe.

---

## Expected Output

When the program is executed, the output is similar to:

```text
========================================
       TASK 15 - PIPE PIPELINE
========================================

Executing: ls -l | grep ".c"

-rw-r--r--  1 user  staff  1748  Sep 9 12:35 task15_pipe_pipeline.c

Pipeline execution completed.
```

The exact file information may vary depending on the system and the files present in the `Task-15` directory.

---

## Source Code

The source code is stored in:

```text
task15_pipe_pipeline.c
```

The program:

1. Creates a pipe.
2. Creates two child processes.
3. Redirects the first child's output to the pipe.
4. Redirects the second child's input from the pipe.
5. Executes `ls -l`.
6. Executes `grep ".c"`.
7. Waits for both child processes.
8. Displays the completion message.

---

## Compilation

The program can be compiled using:

```bash
gcc task15_pipe_pipeline.c -o task15_pipe_pipeline
```

---

## Execution

The compiled program can be executed using:

```bash
./task15_pipe_pipeline
```

The program demonstrates the equivalent of:

```bash
ls -l | grep ".c"
```

---

## Important File Descriptors

The pipe uses two file descriptors:

```text
fd[0] → Read end of the pipe
fd[1] → Write end of the pipe
```

For the first child:

```text
ls -l
  |
  v
STDOUT
  |
  v
fd[1]
  |
  v
PIPE
```

For the second child:

```text
PIPE
  |
  v
fd[0]
  |
  v
STDIN
  |
  v
grep ".c"
```

---

## Key Learning

This practical demonstrates how a shell pipeline can be implemented using process-management and inter-process communication system calls.

The main sequence is:

```text
pipe()
   ↓
fork()
   ↓
dup2()
   ↓
exec()
   ↓
waitpid()
```

The `pipe()` system call provides communication between processes, `fork()` creates the processes, `dup2()` redirects input and output, `exec()` executes the required commands, and `waitpid()` allows the parent to synchronize with its children.

---

## Conclusion

The practical successfully demonstrates the implementation of a command pipeline using C system calls.

The program creates two child processes and connects them using a pipe. The first child executes `ls -l`, and its output is passed through the pipe to the second child, which executes `grep ".c"`.

Thus, the practical demonstrates important concepts of inter-process communication, process creation, input/output redirection, command execution, and process synchronization.
