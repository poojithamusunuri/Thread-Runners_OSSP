# Task 11: A Web Browser Opens a PDF

## Objective

To demonstrate how a web browser can launch an external PDF viewer as a separate process using the `fork()` and `exec()` system calls.

---

## Problem Statement

Imagine a student downloading lecture notes from a college website.

The sequence of events is:

1. The student opens Google Chrome.
2. The student downloads a PDF file containing lecture notes.
3. The student clicks on the downloaded PDF file.
4. Instead of the browser itself becoming the PDF reader, the operating system launches another application to open the PDF.
5. The browser continues to remain open while the PDF viewer runs as a separate process.

This practical demonstrates this process using Linux process-management system calls such as `fork()`, `exec()`, and `wait()`.

---

## Concepts Used

### 1. `fork()`

The `fork()` system call is used to create a new child process.

After calling `fork()`:

- The parent process continues execution in the parent section.
- The child process continues execution in the child section.

In this program, the child process is responsible for launching the external PDF viewer.

---

### 2. `exec()`

The `exec()` family of system calls is used to replace the current process with another program.

The child process uses `execlp()` to launch the external application that opens the PDF file.

#### Linux

```c
execlp("xdg-open", "xdg-open", "lecture_notes.pdf", NULL);
```

`xdg-open` opens the file using the user's default application.

#### macOS

The equivalent command used in the current implementation is:

```c
execlp("open", "open", "lecture_notes.pdf", NULL);
```

The `open` command launches the appropriate default application for the file.

---

### 3. `wait()`

The `wait()` system call is used by the parent process to wait for the child process to complete.

In this program, the parent waits while the child launches the PDF viewer.

```c
wait(NULL);
```

Once the child process completes, the parent continues execution.

---

### 4. `getpid()`

The `getpid()` system call returns the Process ID (PID) of the currently executing process.

It is used in the program to display the PID of the parent and child processes.

```c
getpid();
```

---

### 5. `exit()`

The `exit()` function is used to terminate a process when an error occurs.

For example, if `exec()` fails:

```c
exit(1);
```

---

## System Calls and Functions Used

| Function / System Call | Purpose |
|---|---|
| `fork()` | Creates a new child process |
| `execlp()` | Executes an external program |
| `wait()` | Makes the parent wait for the child |
| `getpid()` | Obtains the Process ID |
| `perror()` | Displays an error message |
| `exit()` | Terminates the process |

---

## Program Workflow

```text
                         START
                           |
                           v
                   Parent Process
                           |
                           v
                         fork()
                       /        \
                      /          \
                     v            v
              Child Process   Parent Process
                    |                |
                    |              wait()
                    |
                    v
                  exec()
                    |
                    v
           External PDF Viewer
                    |
                    v
          Opens lecture_notes.pdf
                    |
                    v
             Child Process Ends
                    |
                    v
             Parent Continues
                    |
                    v
                   END
```

---

## Working of the Program

### Step 1: Start the Parent Process

The program begins execution in the parent process.

It displays:

- A message indicating that the parent process has started.
- The Process ID of the parent.

---

### Step 2: Create a Child Process

The `fork()` system call is called.

```c
pid = fork();
```

The return value is checked to determine whether:

- `fork()` failed.
- The current process is the child.
- The current process is the parent.

---

### Step 3: Child Process Launches the PDF Viewer

When:

```c
pid == 0
```

the program is executing inside the child process.

The child displays its Process ID and then calls `execlp()`.

#### On Linux

```c
execlp("xdg-open", "xdg-open", "lecture_notes.pdf", NULL);
```

This launches the system's default application for opening the PDF file.

The important point is that the child process is replaced by the program launched using `exec()`.

---

### Step 4: Parent Process Waits

The parent process executes:

```c
wait(NULL);
```

This makes the parent wait until the child process terminates.

The parent therefore does not immediately finish while the child is executing.

---

### Step 5: Completion

After the child process completes, the parent process resumes execution.

The program displays:

```text
Child process completed.
Parent process finished.
```

The program then terminates successfully.

---

## Expected Output

A typical execution produces output similar to:

```text
Parent process started.
Parent PID: 12345

--- Parent Process ---
Parent is waiting for the child process.

--- Child Process ---
Child PID: 12346
Child is launching the PDF viewer using exec().

Child process completed.
Parent process finished.
```

> **Note:** The Process IDs will be different each time the program is executed.

---

## Process Relationship

The program creates the following process relationship:

```text
                    Parent Process
                          |
                          | fork()
                          |
              +-----------+-----------+
              |                       |
              v                       v
       Parent Process           Child Process
              |                       |
              |                       | exec()
              |                       |
              |                       v
              |                  PDF Viewer
              |                       |
              |                       v
              |                PDF is opened
              |                       |
              |                    finishes
              |                       |
              +------ wait() <--------+
                       |
                       v
                Parent continues
```

This demonstrates how the browser and the PDF viewer can exist as separate processes.

---

## Source Code

The program is available in:

```text
task11_web_browser_pdf.c
```

The program:

- Creates a child process using `fork()`.
- Uses `execlp()` in the child process.
- Launches the PDF-opening application.
- Uses `wait()` in the parent process.
- Displays the parent and child Process IDs.

---

## Compilation

### Linux

Compile the program using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
```

---

### macOS

Compile using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
```

The compilation command is the same on both Linux and macOS. The difference is in the command used by `execlp()` to open the PDF.

---

## Execution

Run the compiled program using:

```bash
./task11_web_browser_pdf
```

Make sure the PDF file:

```text
lecture_notes.pdf
```

is available at the location expected by the program.

---

## Linux and macOS Difference

The concept of the practical is the same on both operating systems, but the command used to open a PDF differs.

### Linux

Linux commonly uses:

```c
execlp("xdg-open", "xdg-open", "lecture_notes.pdf", NULL);
```

`xdg-open` opens the file using the user's default application.

---

### macOS

macOS uses:

```c
execlp("open", "open", "lecture_notes.pdf", NULL);
```

The `open` command launches the appropriate default application for the file.

---

### Important Note

If the practical is executed on Linux, the `xdg-open` version should be used.

If the practical is executed on macOS, the `open` version should be used.

The underlying concept remains the same:

```text
fork()
  ↓
Create child process
  ↓
exec()
  ↓
Launch external PDF viewer
  ↓
wait()
  ↓
Parent waits for child
```

---

## Key Learning

This practical demonstrates the relationship between three important process-management operations:

```text
fork()
   ↓
Creates a child process

exec()
   ↓
Child executes another program

wait()
   ↓
Parent waits for the child
```

Together, these system calls demonstrate how one process can create another process and how the child can execute a completely different program.

---

## Conclusion

The practical successfully demonstrates how a web browser can launch an external PDF viewer as a separate process.

The `fork()` system call creates the child process, `exec()` allows the child to execute the external PDF-opening application, and `wait()` allows the parent process to wait for the child process to complete.

Thus, the practical demonstrates fundamental concepts of:

- Process creation
- Process execution
- Parent-child relationships
- Process synchronization
- External program execution

---

## Summary

| Concept | Role in the Practical |
|---|---|
| `fork()` | Creates the child process |
| `exec()` | Replaces the child process with the PDF-opening program |
| `wait()` | Allows the parent to wait for the child |
| `getpid()` | Displays process IDs |
| `perror()` | Displays errors |
| `exit()` | Terminates the process in case of failure |

### Overall Process

```text
Web Browser
     |
     | fork()
     v
Child Process
     |
     | exec()
     v
PDF Viewer
     |
     v
Opens PDF

Meanwhile:

Parent Process
     |
     | wait()
     v
Waits for Child
     |
     v
Continues Execution
```

---

## Result

The web browser process successfully creates a child process using `fork()`, and the child process uses `exec()` to launch an external application for opening the PDF file.

The parent process uses `wait()` to synchronize with the child process.

Thus, **Task 11: A Web Browser Opens a PDF** is successfully demonstrated using process creation, execution, and synchronization system calls.
