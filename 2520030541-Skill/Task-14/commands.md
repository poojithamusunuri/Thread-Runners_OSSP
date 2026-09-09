# Task 14: Commands Used

## Directory Setup

I created the Task 14 directory inside the skill folder:

```bash
mkdir -p ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-14
```

I then moved into the Task 14 directory:

```bash
cd ~/Documents/ForkFusion_OSSP/2520030541-Skill/Task-14
```

I checked my current location using:

```bash
pwd
```

---

## Creating the Source File

I created the C source file using:

```bash
nano task14_command_history.c
```

I entered the Task 14 program into the file and saved it.

---

## Compiling the Program

I compiled the program using:

```bash
gcc task14_command_history.c -o task14_command_history
```

The compiler displayed a linker alignment warning on macOS, but the executable was successfully created and the program ran correctly.

---

## Checking the Files

I checked the contents of the directory using:

```bash
ls -l
```

The directory contained the source file and the compiled executable:

```text
task14_command_history.c
task14_command_history
```

---

## Running the Program

I executed the compiled program using:

```bash
./task14_command_history
```

The program displayed:

```text
========================================
      TASK 14 - COMMAND HISTORY
========================================
Use Up/Down arrows to navigate history.
Type 'history' to display commands.
Type 'exit' to quit.

myshell>
```

---

## Testing Command History

I entered commands such as:

```text
hello
world
hello
helloworld
```

and pressed Enter after each command.

The commands were stored in the program's history.

---

## Testing Previous Commands

I used the **Up Arrow** key to recall previously entered commands.

For example:

```text
Up Arrow → world
Up Arrow → hello
```

This tested navigation through previous commands.

---

## Testing Next Commands

I used the **Down Arrow** key to navigate toward newer commands.

When the end of the history was reached, pressing Down Arrow again cleared the current input buffer.

---

## Testing Backspace

I recalled an earlier command using the Up Arrow and used the **Backspace** key to modify the command.

For example:

```text
helloworld
```

could be edited using Backspace before pressing Enter.

This tested input-buffer modification.

---

## Testing the `history` Command

I entered:

```text
history
```

The program displayed the stored commands.

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

---

## Testing the `exit` Command

I entered:

```text
exit
```

The program terminated and displayed:

```text
Exiting shell...
```

---

## Files Created

The Task 14 directory contains:

```text
Task-14/
├── task14_command_history.c
├── task14_command_history
├── README.md
└── commands.md
```

---

## Final Verification

I checked the files once more using:

```bash
ls -l
```

The source file, compiled executable, README, and commands file were present in the Task 14 directory.
