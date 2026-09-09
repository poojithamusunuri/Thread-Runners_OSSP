#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

#define MAX_PROCESSES 10

typedef struct cpu {
    int pid;
    int at;              // Arrival Time
    int bt;              // Burst Time
    int priority;

    int ct;              // Completion Time
    int tat;             // Turnaround Time
    int wt;              // Waiting Time
    int ret;             // Response Time

    int remaining_bt;    // Remaining Burst Time

    bool proc_status;    // Completion Status
    bool started;        // Whether process has started
} Process;


/* =========================================================
   DISPLAY ORIGINAL PROCESS DATA
   ========================================================= */

void display(Process *p, int n) {

    printf("\n====================================================\n");
    printf("                 PROCESS DATA\n");
    printf("====================================================\n");

    printf("PID\tAT\tBT\tPRI\n");

    for (int i = 0; i < n; i++) {

        printf("P%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].at,
               p[i].bt,
               p[i].priority);
    }
}


/* =========================================================
   DISPLAY SCHEDULING RESULTS
   ========================================================= */

void scheduling_display(Process *p, int n) {

    int sum_tat = 0;
    int sum_wt = 0;
    int sum_rt = 0;

    printf("\n====================================================\n");
    printf("               SCHEDULING RESULT\n");
    printf("====================================================\n");

    printf("PID\tAT\tBT\tPRI\tCT\tTAT\tWT\tRT\n");

    for (int i = 0; i < n; i++) {

        sum_tat += p[i].tat;
        sum_wt += p[i].wt;
        sum_rt += p[i].ret;

        printf("P%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].at,
               p[i].bt,
               p[i].priority,
               p[i].ct,
               p[i].tat,
               p[i].wt,
               p[i].ret);
    }

    printf("\nAverage Turnaround Time : %.2f\n",
           (float)sum_tat / n);

    printf("Average Waiting Time    : %.2f\n",
           (float)sum_wt / n);

    printf("Average Response Time   : %.2f\n",
           (float)sum_rt / n);
}


/* =========================================================
   RESET PROCESS DATA
   ========================================================= */

void reset_processes(Process p[], int n) {

    for (int i = 0; i < n; i++) {

        p[i].ct = 0;
        p[i].tat = 0;
        p[i].wt = 0;
        p[i].ret = 0;

        p[i].remaining_bt = p[i].bt;

        p[i].proc_status = false;
        p[i].started = false;
    }
}


/* =========================================================
   COPY PROCESS ARRAY
   ========================================================= */

void copy_processes(Process source[], Process destination[], int n) {

    for (int i = 0; i < n; i++) {
        destination[i] = source[i];
    }
}


/* =========================================================
   SORT BY ARRIVAL TIME
   ========================================================= */

void sort_by_arrival(Process p[], int n) {

    for (int i = 0; i < n - 1; i++) {

        for (int j = 0; j < n - i - 1; j++) {

            if (p[j].at > p[j + 1].at ||
                (p[j].at == p[j + 1].at &&
                 p[j].pid > p[j + 1].pid)) {

                Process temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}


/* =========================================================
   1. FCFS
   ========================================================= */

void Fcfs(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    sort_by_arrival(p, n);

    int cpu_time = 0;

    printf("\nOperations of FCFS\n");

    for (int i = 0; i < n; i++) {

        /* CPU Idle Condition */

        if (cpu_time < p[i].at) {

            printf("CPU Idle from %d to %d\n",
                   cpu_time,
                   p[i].at);

            cpu_time = p[i].at;
        }

        printf("P%d starts at time %d\n",
               p[i].pid,
               cpu_time);

        p[i].ret = cpu_time - p[i].at;

        cpu_time += p[i].bt;

        p[i].ct = cpu_time;

        p[i].tat = p[i].ct - p[i].at;

        p[i].wt = p[i].tat - p[i].bt;

        p[i].proc_status = true;

        printf("P%d completes at time %d\n",
               p[i].pid,
               p[i].ct);
    }

    scheduling_display(p, n);
}


/* =========================================================
   2. SJF NON-PREEMPTIVE
   ========================================================= */

void Sjf(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    int completed = 0;
    int cpu_time = 0;

    printf("\nOperations of SJF Non-Preemptive\n");

    while (completed < n) {

        int index = -1;
        int minimum_bt = INT_MAX;

        /* Find shortest arrived process */

        for (int i = 0; i < n; i++) {

            if (!p[i].proc_status &&
                p[i].at <= cpu_time) {

                if (p[i].bt < minimum_bt) {

                    minimum_bt = p[i].bt;
                    index = i;
                }

                else if (p[i].bt == minimum_bt &&
                         p[i].at < p[index].at) {

                    index = i;
                }
            }
        }

        /* CPU Idle Condition */

        if (index == -1) {

            int next_arrival = INT_MAX;

            for (int i = 0; i < n; i++) {

                if (!p[i].proc_status &&
                    p[i].at < next_arrival) {

                    next_arrival = p[i].at;
                }
            }

            printf("CPU Idle from %d to %d\n",
                   cpu_time,
                   next_arrival);

            cpu_time = next_arrival;

            continue;
        }

        printf("P%d starts at time %d\n",
               p[index].pid,
               cpu_time);

        p[index].ret = cpu_time - p[index].at;

        cpu_time += p[index].bt;

        p[index].ct = cpu_time;

        p[index].tat =
            p[index].ct - p[index].at;

        p[index].wt =
            p[index].tat - p[index].bt;

        p[index].proc_status = true;

        completed++;

        printf("P%d completes at time %d\n",
               p[index].pid,
               p[index].ct);
    }

    scheduling_display(p, n);
}


/* =========================================================
   3. SRTF
   SHORTEST REMAINING TIME FIRST
   ========================================================= */

void Srtf(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    int completed = 0;
    int cpu_time = 0;

    printf("\nOperations of SRTF Preemptive Scheduling\n");

    while (completed < n) {

        int index = -1;
        int minimum_remaining = INT_MAX;

        /* Select process with smallest remaining time */

        for (int i = 0; i < n; i++) {

            if (!p[i].proc_status &&
                p[i].at <= cpu_time &&
                p[i].remaining_bt > 0) {

                if (p[i].remaining_bt <
                    minimum_remaining) {

                    minimum_remaining =
                        p[i].remaining_bt;

                    index = i;
                }
            }
        }

        /* CPU Idle */

        if (index == -1) {

            printf("Time %d : CPU Idle\n",
                   cpu_time);

            cpu_time++;

            continue;
        }

        /* First Response */

        if (!p[index].started) {

            p[index].ret =
                cpu_time - p[index].at;

            p[index].started = true;

            printf("P%d starts at time %d\n",
                   p[index].pid,
                   cpu_time);
        }

        /* Execute for one unit */

        p[index].remaining_bt--;

        cpu_time++;

        /* Process Completed */

        if (p[index].remaining_bt == 0) {

            p[index].ct = cpu_time;

            p[index].tat =
                p[index].ct - p[index].at;

            p[index].wt =
                p[index].tat - p[index].bt;

            p[index].proc_status = true;

            completed++;

            printf("P%d completes at time %d\n",
                   p[index].pid,
                   cpu_time);
        }
    }

    scheduling_display(p, n);
}


/* =========================================================
   4. PRIORITY NON-PREEMPTIVE

   Smaller Priority Number = Higher Priority
   ========================================================= */

void Priority_NonPreemptive(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    int completed = 0;
    int cpu_time = 0;

    printf("\nOperations of Priority Non-Preemptive\n");

    while (completed < n) {

        int index = -1;
        int highest_priority = INT_MAX;

        /* Find highest priority arrived process */

        for (int i = 0; i < n; i++) {

            if (!p[i].proc_status &&
                p[i].at <= cpu_time) {

                if (p[i].priority <
                    highest_priority) {

                    highest_priority =
                        p[i].priority;

                    index = i;
                }
            }
        }

        /* CPU Idle */

        if (index == -1) {

            int next_arrival = INT_MAX;

            for (int i = 0; i < n; i++) {

                if (!p[i].proc_status &&
                    p[i].at < next_arrival) {

                    next_arrival = p[i].at;
                }
            }

            printf("CPU Idle from %d to %d\n",
                   cpu_time,
                   next_arrival);

            cpu_time = next_arrival;

            continue;
        }

        printf("P%d starts at time %d\n",
               p[index].pid,
               cpu_time);

        p[index].ret =
            cpu_time - p[index].at;

        /* Non-preemptive:
           process runs until completion */

        cpu_time += p[index].bt;

        p[index].ct = cpu_time;

        p[index].tat =
            p[index].ct - p[index].at;

        p[index].wt =
            p[index].tat - p[index].bt;

        p[index].proc_status = true;

        completed++;

        printf("P%d completes at time %d\n",
               p[index].pid,
               cpu_time);
    }

    scheduling_display(p, n);
}


/* =========================================================
   5. PRIORITY PREEMPTIVE

   Smaller Priority Number = Higher Priority
   ========================================================= */

void Priority_Preemptive(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    int completed = 0;
    int cpu_time = 0;

    printf("\nOperations of Priority Preemptive\n");

    while (completed < n) {

        int index = -1;
        int highest_priority = INT_MAX;

        /* Select highest priority available process */

        for (int i = 0; i < n; i++) {

            if (!p[i].proc_status &&
                p[i].at <= cpu_time &&
                p[i].remaining_bt > 0) {

                if (p[i].priority <
                    highest_priority) {

                    highest_priority =
                        p[i].priority;

                    index = i;
                }
            }
        }

        /* CPU Idle */

        if (index == -1) {

            printf("Time %d : CPU Idle\n",
                   cpu_time);

            cpu_time++;

            continue;
        }

        /* First Response */

        if (!p[index].started) {

            p[index].ret =
                cpu_time - p[index].at;

            p[index].started = true;

            printf("P%d starts at time %d\n",
                   p[index].pid,
                   cpu_time);
        }

        /* Execute one unit */

        p[index].remaining_bt--;

        cpu_time++;

        /* Completion */

        if (p[index].remaining_bt == 0) {

            p[index].ct = cpu_time;

            p[index].tat =
                p[index].ct - p[index].at;

            p[index].wt =
                p[index].tat - p[index].bt;

            p[index].proc_status = true;

            completed++;

            printf("P%d completes at time %d\n",
                   p[index].pid,
                   cpu_time);
        }
    }

    scheduling_display(p, n);
}


/* =========================================================
   6. ROUND ROBIN
   ========================================================= */

void RoundRobin(Process original[], int n) {

    Process p[MAX_PROCESSES];

    copy_processes(original, p, n);
    reset_processes(p, n);

    int quantum;

    printf("\nEnter Time Quantum: ");
    scanf("%d", &quantum);

    if (quantum <= 0) {

        printf("Invalid Time Quantum!\n");
        return;
    }

    int queue[100];
    int front = 0;
    int rear = 0;

    int cpu_time = 0;
    int completed = 0;

    bool added[MAX_PROCESSES] = {false};

    printf("\nOperations of Round Robin\n");

    while (completed < n) {

        /* Add newly arrived processes */

        for (int i = 0; i < n; i++) {

            if (!added[i] &&
                p[i].at <= cpu_time) {

                queue[rear++] = i;

                added[i] = true;
            }
        }

        /* CPU Idle */

        if (front == rear) {

            int next_arrival = INT_MAX;

            for (int i = 0; i < n; i++) {

                if (!added[i] &&
                    p[i].at < next_arrival) {

                    next_arrival = p[i].at;
                }
            }

            if (next_arrival != INT_MAX) {

                printf("CPU Idle from %d to %d\n",
                       cpu_time,
                       next_arrival);

                cpu_time = next_arrival;

                continue;
            }
        }

        int index = queue[front++];

        /* First Response */

        if (!p[index].started) {

            p[index].ret =
                cpu_time - p[index].at;

            p[index].started = true;

            printf("P%d starts at time %d\n",
                   p[index].pid,
                   cpu_time);
        }

        int execution_time;

        if (p[index].remaining_bt > quantum) {

            execution_time = quantum;
        }
        else {

            execution_time =
                p[index].remaining_bt;
        }

        printf("P%d executes from %d to %d\n",
               p[index].pid,
               cpu_time,
               cpu_time + execution_time);

        p[index].remaining_bt -= execution_time;

        cpu_time += execution_time;

        /* Add processes that arrived during execution */

        for (int i = 0; i < n; i++) {

            if (!added[i] &&
                p[i].at <= cpu_time) {

                queue[rear++] = i;

                added[i] = true;
            }
        }

        /* Process completed */

        if (p[index].remaining_bt == 0) {

            p[index].ct = cpu_time;

            p[index].tat =
                p[index].ct - p[index].at;

            p[index].wt =
                p[index].tat - p[index].bt;

            p[index].proc_status = true;

            completed++;

            printf("P%d completes at time %d\n",
                   p[index].pid,
                   cpu_time);
        }

        /* Process still remaining */

        else {

            queue[rear++] = index;
        }
    }

    scheduling_display(p, n);
}


/* =========================================================
   MAIN FUNCTION
   ========================================================= */

int main() {

    int choice;
    int n;

    Process p[MAX_PROCESSES];

    printf("\nEnter number of processes: ");
    scanf("%d", &n);

    if (n <= 0 || n > MAX_PROCESSES) {

        printf("Invalid number of processes!\n");

        return 0;
    }


    /* INPUT */

    for (int i = 0; i < n; i++) {

        p[i].pid = i + 1;

        printf("\nEnter AT of P%d: ",
               i + 1);

        scanf("%d", &p[i].at);

        printf("Enter BT of P%d: ",
               i + 1);

        scanf("%d", &p[i].bt);

        printf("Enter Priority of P%d: ",
               i + 1);

        scanf("%d", &p[i].priority);

        p[i].ct = 0;
        p[i].tat = 0;
        p[i].wt = 0;
        p[i].ret = 0;

        p[i].remaining_bt = p[i].bt;

        p[i].proc_status = false;
        p[i].started = false;
    }


    /* DISPLAY INPUT DATA */

    display(p, n);


    /* MENU */

    while (1) {

        printf("\n====================================================\n");
        printf("             CPU SCHEDULING ALGORITHMS\n");
        printf("====================================================\n");

        printf("1. FCFS\n");

        printf("2. SJF (Non-Preemptive)\n");

        printf("3. SRTF (Preemptive SJF)\n");

        printf("4. Priority Scheduling (Non-Preemptive)\n");

        printf("5. Priority Scheduling (Preemptive)\n");

        printf("6. Round Robin\n");

        printf("7. Exit\n");

        printf("\nSelect one of the CPU Scheduling Algorithms: ");

        scanf("%d", &choice);


        switch (choice) {

            case 1:

                Fcfs(p, n);

                break;


            case 2:

                Sjf(p, n);

                break;


            case 3:

                Srtf(p, n);

                break;


            case 4:

                Priority_NonPreemptive(p, n);

                break;


            case 5:

                Priority_Preemptive(p, n);

                break;


            case 6:

                RoundRobin(p, n);

                break;


            case 7:

                printf("\nExiting CPU Scheduling Program...\n");

                exit(0);


            default:

                printf("\nInvalid Choice!\n");
        }
    }

    return 0;
}
