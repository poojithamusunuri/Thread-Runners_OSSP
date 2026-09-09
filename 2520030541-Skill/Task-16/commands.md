# Task 16: Commands

This file contains the terminal commands used while creating, compiling, executing, testing, and verifying the multi-client full-duplex IPC program using Named Pipes (FIFOs).

---

## 1. Opening the Task 16 Directory

I first moved to the Task 16 directory using:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16
```

---

## 2. Creating the Server Source File

I created the server source file using:

```bash
nano server.c
```

I entered the server-side C program and saved the file.

---

## 3. Creating the Client Source File

I created the client source file using:

```bash
nano client.c
```

I entered the client-side C program and saved the file.

---

## 4. Compiling the Server

I compiled the server program using:

```bash
gcc server.c -o server
```

The compilation generated the executable:

```text
server
```

---

## 5. Compiling the Client

I compiled the client program using:

```bash
gcc client.c -o client
```

The compilation generated the executable:

```text
client
```

---

## 6. Checking the Files

I checked the contents of the Task 16 directory using:

```bash
ls
```

The directory contained the source files, executable files, and documentation files.

The main files were:

```text
server.c
client.c
server
client
README.md
commands.md
```

---

# 7. Running the Server

I started the server using:

```bash
./server
```

The server created the required FIFO files and handler processes.

The output was similar to:

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

The Process IDs can be different each time the program is executed.

---

# 8. Running Client 1

I opened a separate terminal and moved to the Task 16 directory:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16
```

Then I started the client program:

```bash
./client
```

This terminal was used as Client 1.

---

# 9. Running Client 2

I opened another terminal and moved to the Task 16 directory:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16
```

Then I started:

```bash
./client
```

This terminal was used as Client 2.

---

# 10. Running Client 3

I opened a third terminal and moved to the Task 16 directory:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16
```

Then I started:

```bash
./client
```

This terminal was used as Client 3.

---

# 11. Testing Client 1

From the Client 1 terminal, I entered a message such as:

```text
Hello Server
```

The corresponding handler displayed a message similar to:

```text
[Handler 1] Message received: Hello Server
[Handler 1] Response sent to Client 1.
```

This verified communication between Client 1 and Handler 1.

---

# 12. Testing Client 2

From the Client 2 terminal, I entered:

```text
hello from client 2
```

The corresponding handler displayed:

```text
[Handler 2] Message received: hello from client 2
[Handler 2] Response sent to Client 2.
```

This verified communication between Client 2 and Handler 2.

---

# 13. Testing Client 3

From the Client 3 terminal, I entered:

```text
hello from client 3
```

The corresponding handler displayed:

```text
[Handler 3] Message received: hello from client 3
[Handler 3] Response sent to Client 3.
```

This verified communication between Client 3 and Handler 3.

---

# 14. Checking the FIFO Files

While the server was running, I checked the directory contents using:

```bash
ls -l
```

The six FIFO files created by the server corresponded to the following communication channels:

```text
client1_to_server
server_to_client1

client2_to_server
server_to_client2

client3_to_server
server_to_client3
```

Each client therefore had one FIFO for sending data to the server and another FIFO for receiving data from the server.

---

# 15. Verifying Signal Handling

I checked the server and client source files for signal-related implementation using:

```bash
grep -E "signal|SIGUSR1|SIGINT|SIGCHLD|kill|sigaction" server.c client.c
```

The command displayed signal-related code from both source files.

The output included lines similar to:

```text
server.c:#include <signal.h>
server.c:signal(SIGUSR1, handle_sigusr1);
server.c:signal(SIGINT, SIG_DFL);
server.c:signal(SIGINT, handle_sigint);
server.c:signal(SIGCHLD, handle_sigchld);
server.c:kill(handler_pids[i], SIGTERM);

client.c:#include <signal.h>
client.c:signal(SIGINT, handle_sigint);
client.c:signal(SIGUSR1, handle_sigusr1);
client.c:kill(handler_pid, SIGUSR1);
```

This confirmed that signal handling was present in both the server and client programs.

---

# 16. Stopping the Running Server

I stopped the server using:

```text
Ctrl + C
```

Pressing `Ctrl + C` generated the `SIGINT` signal.

The server then started its shutdown procedure.

The output was similar to:

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

This confirmed that the server handled `SIGINT` and performed the required cleanup.

---

# 17. Recompiling After Making Changes

Whenever I made changes to `server.c`, I recompiled it using:

```bash
gcc server.c -o server
```

Whenever I made changes to `client.c`, I recompiled it using:

```bash
gcc client.c -o client
```

---

# 18. Running the Program Again

After recompiling, I started the server again using:

```bash
./server
```

Then I opened three separate terminals and ran:

```bash
./client
```

in each terminal.

This allowed me to test the communication between the server and all three clients again.

---

# 19. Main Commands Used

The main commands used during the practical were:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16

nano server.c

nano client.c

gcc server.c -o server

gcc client.c -o client

ls

./server

./client

ls -l

grep -E "signal|SIGUSR1|SIGINT|SIGCHLD|kill|sigaction" server.c client.c
```

The running server was stopped using:

```text
Ctrl + C
```

---

# 20. Command Summary

| Purpose | Command |
|---|---|
| Open Task 16 directory | `cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-16` |
| Create/edit server source | `nano server.c` |
| Create/edit client source | `nano client.c` |
| Compile server | `gcc server.c -o server` |
| Compile client | `gcc client.c -o client` |
| List files | `ls` |
| Run server | `./server` |
| Run client | `./client` |
| Display detailed file information | `ls -l` |
| Check signal implementation | `grep -E "signal|SIGUSR1|SIGINT|SIGCHLD|kill|sigaction" server.c client.c` |
| Stop the server | `Ctrl + C` |

---

# 21. Testing Summary

The testing was performed using multiple terminal windows.

The overall sequence was:

```text
Compile server
      ↓
Compile client
      ↓
Start server
      ↓
Six FIFOs created
      ↓
Three handler processes created
      ↓
Start Client 1
      ↓
Start Client 2
      ↓
Start Client 3
      ↓
Send messages from clients
      ↓
Handlers receive messages
      ↓
Handlers send responses
      ↓
Verify signal handling
      ↓
Press Ctrl + C
      ↓
Server shuts down
      ↓
Handler processes terminate
      ↓
FIFO files are removed
```

---

# 22. Final Result

The commands successfully supported the implementation and testing of the Task 16 multi-client FIFO IPC system.

The server was able to create the required FIFO communication channels and handler processes.

Three client instances were executed in separate terminals, and messages were successfully exchanged between the clients and their corresponding handlers.

Signal handling was also verified using the `grep` command, and the server was successfully stopped using `Ctrl + C`.

The final shutdown removed the FIFO resources and terminated the handler processes.
```