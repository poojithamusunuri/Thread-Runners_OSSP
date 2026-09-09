# Task 15: Commands Used

This file contains the terminal commands I used while creating, compiling, and executing the Task 15 pipe pipeline program.

---

## 1. Navigate to the Task-15 Directory

I opened the Task-15 directory using:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-15
```

I checked my current location using:

```bash
pwd
```

---

## 2. Create the C Source File

I created the source file using:

```bash
nano task15_pipe_pipeline.c
```

I entered the Task 15 C program in the editor and saved the file.

---

## 3. Compile the Program

I compiled the C program using:

```bash
gcc task15_pipe_pipeline.c -o task15_pipe_pipeline
```

This created the executable:

```text
task15_pipe_pipeline
```

---

## 4. Run the Program

I executed the compiled program using:

```bash
./task15_pipe_pipeline
```

The program demonstrated the following pipeline:

```bash
ls -l | grep ".c"
```

The output showed the `.c` files present in the current directory.

---

## 5. Check the Files in the Directory

I can check the files present in the Task-15 directory using:

```bash
ls -l
```

This helps me verify that the source file and compiled executable are present.

---

## 6. Check the Source File

I can view the source code from the terminal using:

```bash
cat task15_pipe_pipeline.c
```

---

## 7. Verify the Documentation Files

I can check that the README and commands files are present using:

```bash
ls -l README.md commands.md
```

---

## 8. Remove the Executable If Required

If I need to remove the locally compiled executable before committing, I can use:

```bash
rm task15_pipe_pipeline
```

If the practical requires the compiled executable to be included in the repository, I can keep it instead.

---

## 9. Summary of Important Commands

The main commands used for this practical were:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-15
nano task15_pipe_pipeline.c
gcc task15_pipe_pipeline.c -o task15_pipe_pipeline
./task15_pipe_pipeline
ls -l
cat task15_pipe_pipeline.c
```

---

## 10. Result

The program executed successfully and demonstrated the pipeline:

```text
ls -l
   |
   v
 pipe()
   |
   v
grep ".c"
```

The program displayed the matching `.c` file information and completed the pipeline execution successfully.
