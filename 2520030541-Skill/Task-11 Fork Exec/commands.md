# Task 11: Web Browser Opens a PDF — Commands

This file contains the terminal commands used to create, compile, execute, and verify the Task 11 program demonstrating how a parent process can create a child process using `fork()` and launch an external PDF viewer using `exec()`.

---

## 1. Navigating to the Task 11 Folder

I first navigated to the Week 6 practical directory:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Practical/Week\ 6
```

I then entered the folder containing the Task 11 program:

```bash
cd "Task 11 - Web Browser Opens PDF"
```

The current directory was checked using:

```bash
pwd
```

The files in the directory were checked using:

```bash
ls
```

---

## 2. Creating the C Program

I created the C source file using:

```bash
touch task11_web_browser_pdf.c
```

The program was then edited using a text editor.

For example, on macOS:

```bash
nano task11_web_browser_pdf.c
```

The source code was saved and the editor was exited.

---

## 3. Checking the Source Code

I checked whether the C source file was present using:

```bash
ls -l
```

I also viewed the source code from the terminal using:

```bash
cat task11_web_browser_pdf.c
```

---

## 4. Creating the PDF File

The program requires a PDF file to demonstrate the external PDF viewer.

I created or placed a sample PDF named:

```text
lecture_notes.pdf
```

The presence of the PDF was checked using:

```bash
ls -l lecture_notes.pdf
```

---

## 5. Compiling the Program

I compiled the C program using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
```

After successful compilation, I checked the generated executable using:

```bash
ls -l task11_web_browser_pdf
```

---

## 6. Running the Program

I executed the compiled program using:

```bash
./task11_web_browser_pdf
```

The program creates a child process using `fork()`.

The child process uses `exec()` to launch the external application for opening the PDF.

The parent process uses `wait()` to wait for the child process.

---

## 7. Linux PDF Viewer Command

On Linux, the external PDF-opening command used by the child process is:

```c
execlp("xdg-open", "xdg-open", "lecture_notes.pdf", NULL);
```

The `xdg-open` command opens the PDF using the system's default PDF application.

If the program is intended specifically for Linux, the program can be compiled and executed using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
./task11_web_browser_pdf
```

---

## 8. macOS PDF Viewer Command

Since I am working on macOS, the equivalent command for opening the PDF is:

```c
execlp("open", "open", "lecture_notes.pdf", NULL);
```

The macOS `open` command launches the default application associated with PDF files.

The program can therefore be compiled and executed on macOS using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
./task11_web_browser_pdf
```

---

## 9. Checking the Program After Execution

I checked the files in the directory after running the program using:

```bash
ls -l
```

The executable and source file should be present along with the PDF file.

---

## 10. Checking the Process Information

The program displays the Process ID (PID) of the parent and child processes.

The process information can also be viewed from the terminal using:

```bash
ps
```

For more detailed process information, I can use:

```bash
ps aux
```

---

## 11. Checking for Compilation Errors

If the program compiles successfully, the `gcc` command does not display any compilation errors.

I used:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
```

If an error occurs, I can inspect the source code again using:

```bash
cat task11_web_browser_pdf.c
```

---

## 12. Removing the Executable

If I need to remove the previously compiled executable and compile the program again, I can use:

```bash
rm task11_web_browser_pdf
```

The program can then be compiled again using:

```bash
gcc task11_web_browser_pdf.c -o task11_web_browser_pdf
```

---

## 13. Git Commands Used for the Practical

After completing the practical, I checked the Git status from the repository root:

```bash
cd ~/Documents/ForkFusion_OSSP
git status
```

I added the Task 11 files to Git using:

```bash
git add "2520030541-Practical/Week 6/Task 11 - Web Browser Opens PDF/"
```

I checked the staged files using:

```bash
git status
```

I committed the changes using:

```bash
git commit -m "Add Task 11 web browser PDF process program"
```

I then pushed the changes to GitHub using:

```bash
git push origin main
```

---

## 14. If GitHub Rejects the Push

If the push is rejected because the remote repository contains changes that are not present locally, I first update my local branch using:

```bash
git pull --rebase origin main
```

After the rebase is completed, I push again using:

```bash
git push origin main
```

---

## 15. Final Verification

I finally checked that my working tree was clean using:

```bash
git status
```

A successful final status should show that there are no uncommitted changes.

```bash
git status
```

The Task 11 files are then available in my GitHub repository under the Week 6 practical directory.

---

## Command Summary

| Purpose | Command |
|---|---|
| Navigate to Week 6 | `cd ~/Documents/ForkFusion_OSSP/2520030541-Practical/Week\ 6` |
| Enter Task 11 folder | `cd "Task 11 - Web Browser Opens PDF"` |
| Check current directory | `pwd` |
| List files | `ls` |
| Create C file | `touch task11_web_browser_pdf.c` |
| Edit C file | `nano task11_web_browser_pdf.c` |
| View C file | `cat task11_web_browser_pdf.c` |
| Compile program | `gcc task11_web_browser_pdf.c -o task11_web_browser_pdf` |
| Run program | `./task11_web_browser_pdf` |
| Check files | `ls -l` |
| View processes | `ps` |
| Detailed process information | `ps aux` |
| Remove executable | `rm task11_web_browser_pdf` |
| Go to Git repository | `cd ~/Documents/ForkFusion_OSSP` |
| Check Git status | `git status` |
| Stage Task 11 | `git add "2520030541-Practical/Week 6/Task 11 - Web Browser Opens PDF/"` |
| Commit changes | `git commit -m "Add Task 11 web browser PDF process program"` |
| Push to GitHub | `git push origin main` |
| Update local branch | `git pull --rebase origin main` |

---

## Result

The Task 11 program was compiled and executed successfully. It demonstrates process creation using `fork()`, execution of an external PDF-opening application using `exec()`, and synchronization of the parent and child processes using `wait()`.
