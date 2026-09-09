# Task 16: Multi-Client Full-Duplex IPC Using Named Pipes (FIFOs)

## Objective

To develop a **multi-client, full-duplex Inter-Process Communication (IPC) system** using **Named Pipes (FIFOs)** in Linux.

The system consists of:

- One **Server**
- Three **Clients**
- Three **Handler Processes**
- Six **Named Pipes (FIFOs)**
- Signal handling for process management and communication

The server communicates independently with each client using a separate pair of FIFOs.

---

# Problem Statement

The objective is to implement a multi-client communication system in which:

- Three clients can communicate with a single server.
- Each client has a dedicated handler process on the server side.
- Communication between each client and the server is **full-duplex**, meaning data can travel in both directions.
- Named Pipes (FIFOs) are used for communication.
- Signals are used for process control and notification.

The communication structure is:

```text
                    SERVER
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Handler 1     Handler 2     Handler 3
          |            |            |
          |            |            |
       FIFO Pair    FIFO Pair    FIFO Pair
          |            |            |
          v            v            v
      Client 1      Client 2      Client 3
```

---

# System Architecture

The system contains one server and three independent clients.

Each client communicates with its corresponding server-side handler through **two FIFOs**.

## Client 1

```text
Client 1
   |
   | client1_to_server
   v
Handler 1
   |
   | server_to_client1
   v
Client 1
```

## Client 2

```text
Client 2
   |
   | client2_to_server
   v
Handler 2
   |
   | server_to_client2
   v
Client 2
```

## Client 3

```text
Client 3
   |
   | client3_to_server
   v
Handler 3
   |
   | server_to_client3
   v
Client 3
```

Each client therefore has its own independent communication channel.

---

# FIFO Structure

A total of **six named pipes** are used.

| Client | Client → Server | Server → Client |
|--------|------------------|------------------|
| Client 1 | `client1_to_server` | `server_to_client1` |
| Client 2 | `client2_to_server` | `server_to_client2` |
| Client 3 | `client3_to_server` | `server_to_client3` |

The first FIFO in each pair carries messages from the client to the server.

The second FIFO carries responses from the server back to the client.

---

# Important Concepts Used

## 1. Inter-Process Communication (IPC)

**Inter-Process Communication** allows different processes to exchange information.

In this practical, IPC is implemented using **Named Pipes (FIFOs)**.

---

## 2. Named Pipe (FIFO)

A FIFO is a special file that provides a communication channel between processes.

Unlike an anonymous pipe, a named pipe has a name in the file system and can be accessed by unrelated processes.

The FIFO is created using:

```c
mkfifo()
```

---

## 3. Full-Duplex Communication

Full-duplex communication means that communication can occur in both directions.

In this practical:

```text
Client → Server
```

and

```text
Server → Client
```

are handled using separate FIFOs.

Therefore, each client has two-way communication with its corresponding handler.

---

## 4. `fork()`

The `fork()` system call creates a new child process.

The server uses `fork()` to create separate handler processes.

The process structure is:

```text
Server
  |
  +---- Handler 1
  |
  +---- Handler 2
  |
  +---- Handler 3
```

Each handler is responsible for one client.

---

## 5. `open()`

The `open()` system call is used to open the FIFO for reading or writing.

For example:

```c
open(fifo_name, O_RDONLY);
```

opens a FIFO for reading.

Similarly:

```c
open(fifo_name, O_WRONLY);
```

opens a FIFO for writing.

---

## 6. `read()`

The `read()` system call reads data from the FIFO.

Example:

```c
read(fd, buffer, sizeof(buffer));
```

The handler uses `read()` to receive messages sent by the client.

---

## 7. `write()`

The `write()` system call sends data through the FIFO.

Example:

```c
write(fd, response, strlen(response) + 1);
```

The handler uses `write()` to send a response back to the client.

---

## 8. Signals

Signals are used for process control and notification.

The implementation uses signals such as:

- `SIGINT`
- `SIGUSR1`
- `SIGCHLD`
- `SIGTERM`

---

# Signals Used

## `SIGINT`

`SIGINT` is generated when the user presses:

```text
Ctrl + C
```

The server and client have signal handling for controlled termination.

The server uses `SIGINT` to begin its shutdown process.

---

## `SIGUSR1`

`SIGUSR1` is a user-defined signal.

In this practical, it is used to notify a corresponding process about communication-related events.

The client can notify its handler using:

```c
kill(handler_pid, SIGUSR1);
```

---

## `SIGCHLD`

`SIGCHLD` is sent to the parent when a child process terminates.

The server installs a handler for `SIGCHLD` to handle terminated child processes.

---

## `SIGTERM`

`SIGTERM` is used by the server to request termination of handler processes during shutdown.

For example:

```c
kill(handler_pids[i], SIGTERM);
```

---

# Header Files Used

The programs use standard POSIX and C header files.

Important headers include:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <sys/wait.h>
```

---

# Important Functions and Their Purposes

| Function / System Call | Purpose |
|------------------------|---------|
| `mkfifo()` | Creates a named pipe |
| `open()` | Opens a FIFO |
| `read()` | Reads data from a FIFO |
| `write()` | Writes data to a FIFO |
| `close()` | Closes a file descriptor |
| `fork()` | Creates a child process |
| `kill()` | Sends a signal to another process |
| `signal()` | Installs a signal handler |
| `waitpid()` | Waits for a child process |
| `unlink()` | Removes a FIFO |
| `getpid()` | Returns the current process ID |

---

# Server Process

The server is responsible for managing the entire IPC system.

## Server Responsibilities

The server:

1. Creates six FIFOs.
2. Creates three handler processes.
3. Assigns one handler to each client.
4. Waits for client communication.
5. Receives messages through the appropriate FIFO.
6. Sends responses back through the corresponding FIFO.
7. Handles signals.
8. Terminates handler processes during shutdown.
9. Removes the FIFOs before exiting.

---

# Handler Processes

The server creates three handler processes.

```text
Server
  |
  +---- Handler 1 → Client 1
  |
  +---- Handler 2 → Client 2
  |
  +---- Handler 3 → Client 3
```

Each handler operates independently.

## Handler 1

Handler 1 communicates only with Client 1.

## Handler 2

Handler 2 communicates only with Client 2.

## Handler 3

Handler 3 communicates only with Client 3.

This separation prevents messages from different clients from being mixed together.

---

# Client Process

Each client connects to its corresponding handler.

A client:

1. Opens its input FIFO.
2. Opens its output FIFO.
3. Accepts user input.
4. Sends the message to the server.
5. Receives a response.
6. Displays the response.
7. Handles signals such as `SIGINT` and `SIGUSR1`.

The same client program can be executed in three separate terminals.

---

# Complete Workflow

The overall workflow is:

```text
                         START
                           |
                           v
                    Start Server
                           |
                           v
                 Create Six FIFOs
                           |
                           v
              Create Three Handlers
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Handler 1    Handler 2    Handler 3
              |            |            |
              v            v            v
          Client 1      Client 2      Client 3
              |            |            |
              v            v            v
          Send Message  Send Message  Send Message
              |            |            |
              v            v            v
          Handler 1    Handler 2    Handler 3
              |            |            |
              v            v            v
          Process       Process       Process
          Message       Message       Message
              |            |            |
              v            v            v
          Send Response Send Response Send Response
              |            |            |
              +------------+------------+
                           |
                           v
                    Continue Running
                           |
                           v
                    Ctrl + C / SIGINT
                           |
                           v
                   Shutdown Server
                           |
                           v
                Terminate Handlers
                           |
                           v
                    Remove FIFOs
                           |
                           v
                          END
```

---

# Communication Workflow

For Client 1, the communication occurs as follows:

```text
Client 1
   |
   | write()
   v
client1_to_server
   |
   v
Handler 1
   |
   | read()
   |
   | Process message
   |
   | write()
   v
server_to_client1
   |
   v
Client 1
```

The same process occurs independently for Client 2 and Client 3.

---

# Example Communication

## Client 1

The client may send:

```text
Hello Server
```

The corresponding handler receives:

```text
[Handler 1] Message received: Hello Server
```

The handler then sends a response to Client 1.

---

## Client 2

Client 2 may send:

```text
hello from client 2
```

The server displays:

```text
[Handler 2] Message received: hello from client 2
[Handler 2] Response sent to Client 2.
```

---

## Client 3

Client 3 may send:

```text
hello from client 3
```

The server displays:

```text
[Handler 3] Message received: hello from client 3
[Handler 3] Response sent to Client 3.
```

---

# Process Relationship

The process relationship can be represented as:

```text
                         SERVER
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Handler 1    Handler 2    Handler 3
              |            |            |
              v            v            v
          Client 1      Client 2      Client 3
```

The server is the parent process.

The three handlers are child processes created using `fork()`.

Each handler is responsible for one client.

---

# Signal Handling Workflow

The server installs signal handlers for process management.

```text
                    Server Running
                          |
                          |
                     Ctrl + C
                          |
                          v
                       SIGINT
                          |
                          v
                 Server Signal Handler
                          |
                          v
               Begin Server Shutdown
                          |
                          v
             Send SIGTERM to Handlers
                          |
                          v
                Handler Processes End
                          |
                          v
                  Remove Six FIFOs
                          |
                          v
                  Server Terminates
```

---

# Testing the Program

The program was tested using multiple terminal windows.

## Terminal 1 - Server

The server was started using:

```bash
./server
```

The server displayed output similar to:

```text
========================================
        TASK 16 - FIFO IPC SERVER
========================================

Six FIFOs created successfully.

Handler 1 created with PID 14519.
Handler 1 started. PID = 14519

Handler 2 created with PID 14520.
Handler 2 started. PID = 14520

Handler 3 created with PID 14521.
Handler 3 started. PID = 14521

Server is ready for three clients.
Press Ctrl+C to stop the server.
```

The PIDs can be different during each execution.

---

# Client Testing

Three separate terminals were used for the three client instances.

## Client 1

```bash
./client
```

## Client 2

```bash
./client
```

## Client 3

```bash
./client
```

Each client communicates independently with its corresponding handler.

---

# Sample Test

## Client 1 Input

```text
Hello Server
```

Expected server-side message:

```text
[Handler 1] Message received: Hello Server
[Handler 1] Response sent to Client 1.
```

---

## Client 2 Input

```text
hello from client 2
```

Expected server-side message:

```text
[Handler 2] Message received: hello from client 2
[Handler 2] Response sent to Client 2.
```

---

## Client 3 Input

```text
hello from client 3
```

Expected server-side message:

```text
[Handler 3] Message received: hello from client 3
[Handler 3] Response sent to Client 3.
```

---

# Checking the FIFO Files

The FIFO files can be inspected using:

```bash
ls -l
```

The six FIFOs are:

```text
client1_to_server
server_to_client1

client2_to_server
server_to_client2

client3_to_server
server_to_client3
```

The FIFO files are special files created using `mkfifo()`.

---

# Verifying Signal Handling

The signal implementation can be checked using:

```bash
grep -E "signal|SIGUSR1|SIGINT|SIGCHLD|kill|sigaction" server.c client.c
```

The command verifies the presence of signal-related code.

The server contains signal handling for:

```text
SIGINT
SIGCHLD
SIGUSR1
SIGTERM
```

The client contains signal handling for:

```text
SIGINT
SIGUSR1
```

---

# Stopping the Server

The running server can be stopped by pressing:

```text
Ctrl + C
```

This generates:

```text
SIGINT
```

The server then performs its shutdown procedure.

A typical shutdown sequence is:

```text
Server received SIGINT.
Shutting down server...

Terminating handler processes...

Handler child terminated.
Handler child terminated.
Handler child terminated.

All FIFOs removed successfully.

Server terminated successfully.
```

---

# Source Files

The Task 16 implementation contains:

```text
Task-16/
│
├── server.c
├── client.c
├── server
├── client
├── README.md
└── commands.md
```

---

# `server.c`

The `server.c` program implements the server-side functionality.

It is responsible for:

- Creating FIFOs
- Creating handler processes
- Managing three clients
- Receiving messages
- Sending responses
- Handling signals
- Terminating handlers
- Cleaning up FIFOs

---

# `client.c`

The `client.c` program implements the client-side functionality.

It is responsible for:

- Connecting to the appropriate FIFOs
- Accepting user input
- Sending messages
- Receiving server responses
- Handling signals

The same executable can be run in three separate terminals to represent three clients.

---

# Compilation

## Compile the Server

```bash
gcc server.c -o server
```

This creates the executable:

```text
server
```

---

## Compile the Client

```bash
gcc client.c -o client
```

This creates the executable:

```text
client
```

---

# Execution

## Start the Server

```bash
./server
```

The server should be started first because it creates the FIFOs and handler processes.

---

## Start Client 1

In a separate terminal:

```bash
./client
```

---

## Start Client 2

In another terminal:

```bash
./client
```

---

## Start Client 3

In another terminal:

```bash
./client
```

The three client instances communicate independently with the server.

---

# Difference Between Anonymous Pipes and Named Pipes

| Feature | Anonymous Pipe | Named Pipe (FIFO) |
|---------|-----------------|--------------------|
| Name in file system | No | Yes |
| Communication | Usually related processes | Related or unrelated processes |
| Created using | `pipe()` | `mkfifo()` |
| Persistent file-system entry | No | Yes, until removed |
| Used in this task | No | Yes |

Task 15 used an **anonymous pipe**, while Task 16 uses **Named Pipes (FIFOs)**.

---

# Difference Between Task 15 and Task 16

## Task 15

Task 15 implements:

```text
ls -l | grep ".c"
```

using:

- `pipe()`
- `fork()`
- `dup2()`
- `exec()`
- `waitpid()`

It demonstrates a **producer-consumer pipeline** using an anonymous pipe.

---

## Task 16

Task 16 implements:

```text
Server ↔ Client 1
Server ↔ Client 2
Server ↔ Client 3
```

using:

- Named Pipes / FIFOs
- `mkfifo()`
- `fork()`
- `open()`
- `read()`
- `write()`
- `kill()`
- Signals
- `waitpid()`

It demonstrates **multi-client full-duplex IPC**.

---

# Key Learning Outcomes

After completing this task, I understood:

1. How Named Pipes (FIFOs) are used for IPC.
2. How `mkfifo()` creates a named communication channel.
3. How two FIFOs can provide full-duplex communication.
4. How a server can communicate with multiple clients.
5. How `fork()` can create independent handler processes.
6. How separate handlers can manage separate clients.
7. How `read()` and `write()` are used for FIFO communication.
8. How signals can be used for process notification and control.
9. How `SIGINT` can be used for controlled server termination.
10. How `SIGCHLD` can be used to handle terminated child processes.
11. How `SIGTERM` can be used to terminate handler processes.
12. How IPC resources should be cleaned up when the server terminates.

---

# Conclusion

The Task 16 program successfully demonstrates a **multi-client, full-duplex Inter-Process Communication system using Named Pipes (FIFOs)**.

A single server manages three independent clients. Each client has a dedicated handler process and a separate pair of FIFOs for two-way communication.

The implementation demonstrates important operating-system concepts including:

- Inter-Process Communication
- Named Pipes
- Full-duplex communication
- Process creation using `fork()`
- Process management
- Signal handling
- Parent-child process relationships
- Synchronization
- Resource cleanup

The successful communication between all three clients and their corresponding handlers demonstrates that the multi-client FIFO IPC system is functioning correctly.