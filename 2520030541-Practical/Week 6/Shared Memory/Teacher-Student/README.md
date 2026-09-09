# Teacher–Student Shared Memory

## Objective

To demonstrate **Inter-Process Communication (IPC) using shared memory**, where a Teacher process stores the marks of two students in separate shared-memory regions, and each Student process accesses only its respective marks to calculate the total and average.

---

## Problem Statement

The Teacher process maintains the marks of two students.

- Student 1 has five subject marks stored in `student1_marks`.
- Student 2 has five subject marks stored in `student2_marks`.
- Student 1 can access only `student1_marks`.
- Student 2 can access only `student2_marks`.
- Each student reads their five marks and calculates the total and average.
- After both students complete their calculations, the shared-memory objects are cleaned up.

---

## Program Structure

This implementation consists of three C programs:

### 1. `producer.c`

The **Teacher (Producer)** process:

1. Creates two separate shared-memory regions:
   - `student1_marks`
   - `student2_marks`
2. Accepts five subject marks for Student 1.
3. Stores Student 1's marks in `student1_marks`.
4. Accepts five subject marks for Student 2.
5. Stores Student 2's marks in `student2_marks`.
6. Starts the respective student processes.
7. Waits for both student processes to complete.
8. Cleans up and unlinks the shared-memory objects.

### 2. `student1.c`

The **Student 1 (Consumer)** process:

1. Accesses only the `student1_marks` shared-memory region.
2. Reads the five subject marks.
3. Calculates the total marks.
4. Calculates the average marks.
5. Displays the marks, total, and average.
6. Closes its access to the shared memory.

### 3. `student2.c`

The **Student 2 (Consumer)** process:

1. Accesses only the `student2_marks` shared-memory region.
2. Reads the five subject marks.
3. Calculates the total marks.
4. Calculates the average marks.
5. Displays the marks, total, and average.
6. Closes its access to the shared memory.

---

## Workflow

```text
                 TEACHER / PRODUCER
                        |
             -----------------------
             |                     |
             v                     v
      student1_marks        student2_marks
             |                     |
             v                     v
        STUDENT 1              STUDENT 2
             |                     |
             v                     v
       Read 5 marks           Read 5 marks
             |                     |
             v                     v
       Total & Average        Total & Average
             |                     |
             -----------+-----------
                        |
                        v
              Both processes finish
                        |
                        v
             Shared memory cleanup

Shared Memory Design

Two independent shared-memory objects are used:

Shared Memory	Used By	Data Stored
student1_marks	Teacher + Student 1	Five marks of Student 1
student2_marks	Teacher + Student 2	Five marks of Student 2

This separation ensures that each student process accesses only its own marks.

System Calls / POSIX APIs Used
shm_open()

Creates or opens a POSIX shared-memory object.

ftruncate()

Sets the size of the shared-memory object.

mmap()

Maps the shared-memory object into the process's address space so that the process can read or write the data.

munmap()

Unmaps the shared-memory region from the process's address space.

shm_unlink()

Removes the shared-memory object after the processes have completed.

fork()

Creates child processes for the student processes.

wait()

Allows the Teacher process to wait for the student processes to finish.

Compilation

Compile the three programs using:

gcc producer.c -o producer
gcc student1.c -o student1
gcc student2.c -o student2
Execution

Run the Teacher process:

./producer

The Teacher accepts five marks for Student 1 and five marks for Student 2.

The student processes are then executed to read their respective shared-memory regions and calculate their results.

Sample Input
Student 1
Subject 1: 85
Subject 2: 90
Subject 3: 78
Subject 4: 92
Subject 5: 88
Student 2
Subject 1: 75
Subject 2: 82
Subject 3: 91
Subject 4: 68
Subject 5: 84
Sample Output
Student 1
Student 1
--------------------------------
Subject 1 : 85
Subject 2 : 90
Subject 3 : 78
Subject 4 : 92
Subject 5 : 88

Total : 433
Average : 86.60
Student 2
Student 2
--------------------------------
Subject 1 : 75
Subject 2 : 82
Subject 3 : 91
Subject 4 : 68
Subject 5 : 84

Total : 400
Average : 80.00

After both student processes finish:

Both student processes completed.
Shared-memory objects cleaned up successfully.
Concepts Demonstrated

This program demonstrates:

Inter-Process Communication (IPC)
POSIX Shared Memory
Producer–Consumer communication
Process creation using fork()
Parent-child process synchronization using wait()
Memory mapping using mmap()
Shared-memory cleanup using shm_unlink()
Separate data access for independent processes
Expected Result

The Teacher successfully stores the marks of both students in separate shared-memory regions. Each student process accesses only its assigned shared memory, calculates the total and average marks, and displays the results. After both students complete their calculations, the Teacher cleans up the shared-memory objects.
