# System V Shared Memory - Producer Consumer

## Objective

To demonstrate inter-process communication using System V shared memory, where a Producer process writes student marks into shared memory and a Consumer process reads the marks and calculates the total and average.

## Programs

### producer.c

The Producer process:

1. Generates a shared memory key using `ftok()`.
2. Creates a shared memory segment using `shmget()`.
3. Attaches the shared memory using `shmat()`.
4. Accepts marks for five subjects.
5. Stores the marks in shared memory.
6. Detaches from shared memory using `shmdt()`.

### consumer.c

The Consumer process:

1. Generates the same key using `ftok()`.
2. Accesses the existing shared memory using `shmget()`.
3. Attaches to the shared memory using `shmat()`.
4. Reads the five marks.
5. Calculates total and average.
6. Detaches using `shmdt()`.
7. Removes the shared memory using `shmctl()`.

## System Calls / Functions Used

- `ftok()` - Generates a System V IPC key.
- `shmget()` - Creates or accesses shared memory.
- `shmat()` - Attaches shared memory to the process address space.
- `shmdt()` - Detaches shared memory.
- `shmctl()` - Controls and removes the shared memory segment.

## Compilation

```bash
gcc producer.c -o producer
gcc consumer.c -o consumer

Created the key file:

touch shmfile
