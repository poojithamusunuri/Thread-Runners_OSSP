# Task 13: Command Processor — Commands Used

## 1. Creating the Source File

I created the C source file for the command processor using:

```bash
nano task13_command_processor.c
```

I wrote the command processor program in this file.

---

## 2. Compiling the Program

I compiled the C program using:

```bash
gcc task13_command_processor.c -o task13_command_processor
```

This created the executable file:

```text
task13_command_processor
```

---

## 3. Running the Program

I ran the compiled program using:

```bash
./task13_command_processor
```

The program displayed the shell prompt:

```text
myshell>
```

---

## 4. Testing the `hello` Command

I entered:

```text
hello
```

The program displayed:

```text
Hello! Welcome to my shell.
```

This confirmed that the `hello` command was recognized correctly.

---

## 5. Testing an Unknown Command

I entered:

```text
abc
```

The program displayed:

```text
Unknown command: abc
```

This confirmed that the program correctly handles commands that are not defined.

I also tested:

```text
hello!
```

which produced:

```text
Unknown command: hello!
```

because `hello!` is different from the predefined `hello` command.

---

## 6. Testing the `help` Command

I entered:

```text
help
```

The program displayed:

```text
Available commands:
  hello - Display greeting
  help  - Display available commands
  exit  - Exit the shell
```

This confirmed that the `help` command displays the available commands correctly.

---

## 7. Testing Empty Input

I pressed Enter without entering a command.

The program displayed:

```text
Do nothing for empty input.
```

This confirmed that empty input is handled without executing a command.

---

## 8. Testing the `exit` Command

I entered:

```text
exit
```

The program displayed:

```text
Exiting shell...
```

The command processor then terminated.

---

## 9. Complete Command Sequence Used for Testing

The following commands were used during testing:

```text
hello!
hello
abc
help
[empty input]
exit
```

The program correctly handled each input according to its purpose.

---

## 10. Files in This Task

The Task-13 folder contains:

```text
task13_command_processor.c
task13_command_processor
README.md
commands.md
```

---

## 11. Summary

The main commands used for this practical were:

```bash
nano task13_command_processor.c
gcc task13_command_processor.c -o task13_command_processor
./task13_command_processor
nano README.md
nano commands.md
```

These commands were used to create, compile, execute, document, and test the command processor program.
