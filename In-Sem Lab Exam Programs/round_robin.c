
#include <stdio.h>

#define MAX 100
#define QSIZE (MAX + 1)

typedef struct {
    int pid;
    int arrival;
    int burst;
    int remaining;
    int first_start;
    int completion;
    int waiting;
    int turnaround;
    int response;
    int entered_queue;
} Process;

typedef struct {
    int items[QSIZE];
    int front;
    int rear;
    int count;
} ReadyQueue;

void enqueue(ReadyQueue *q, int pid) {
    if (q->count >= QSIZE) {
        printf("Ready queue overflow.\n");
        return;
    }

    q->items[q->rear] = pid;
    q->rear = (q->rear + 1) % QSIZE;
    q->count++;
}

int dequeue(ReadyQueue *q) {
    int pid = q->items[q->front];
    q->front = (q->front + 1) % QSIZE;
    q->count--;
    return pid;
}

void add_arrivals(Process p[], int n, int time,
                  ReadyQueue *q) {
    for (int i = 0; i < n; i++) {
        if (!p[i].entered_queue && p[i].arrival <= time) {
            enqueue(q, i);
            p[i].entered_queue = 1;
        }
    }
}

int main(void) {
    Process p[MAX];
    ReadyQueue q = {{0}, 0, 0, 0};

    int n, quantum;
    int time = 0;
    int completed = 0;
    int execution_pid[MAX * 100];
    int execution_start[MAX * 100];
    int execution_end[MAX * 100];
    int segments = 0;

    double total_waiting = 0;
    double total_turnaround = 0;
    double total_response = 0;

    printf("ROUND ROBIN CPU SCHEDULING\n");

    printf("Enter number of processes (1-%d): ", MAX);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX) {
        printf("Invalid number of processes.\n");
        return 1;
    }

    printf("Enter Time Quantum: ");
    if (scanf("%d", &quantum) != 1 || quantum <= 0) {
        printf("Time quantum must be positive.\n");
        return 1;
    }

    for (int i = 0; i < n; i++) {
        p[i].pid = i;
        p[i].first_start = -1;
        p[i].completion = 0;
        p[i].entered_queue = 0;

        printf("Enter arrival time and burst time for P%d: ", i);

        if (scanf("%d%d", &p[i].arrival, &p[i].burst) != 2 ||
            p[i].arrival < 0 || p[i].burst <= 0) {
            printf("Invalid arrival or burst time.\n");
            return 1;
        }

        p[i].remaining = p[i].burst;
    }

    printf("\n--- CPU Execution ---\n");

    while (completed < n) {
        add_arrivals(p, n, time, &q);

        if (q.count == 0) {
            int next_arrival = -1;

            for (int i = 0; i < n; i++) {
                if (!p[i].entered_queue &&
                    (next_arrival == -1 ||
                     p[i].arrival < next_arrival)) {
                    next_arrival = p[i].arrival;
                }
            }

            if (next_arrival == -1)
                break;

            if (time < next_arrival) {
                printf("CPU idle: %d -> %d\n",
                       time, next_arrival);
                time = next_arrival;
            }

            add_arrivals(p, n, time, &q);
        }

        int current = dequeue(&q);

        if (p[current].first_start == -1)
            p[current].first_start = time;

        int run_time = p[current].remaining < quantum
                     ? p[current].remaining : quantum;

        int start = time;
        time += run_time;
        p[current].remaining -= run_time;

        if (segments < MAX * 100) {
            execution_pid[segments] = current;
            execution_start[segments] = start;
            execution_end[segments] = time;
            segments++;
        }

        printf("P%d: %d -> %d\n", current, start, time);

        /* New arrivals join the queue before the running
           process is requeued. */
        add_arrivals(p, n, time, &q);

        if (p[current].remaining > 0) {
            enqueue(&q, current);
        } else {
            p[current].completion = time;
            completed++;
        }
    }

    printf("\n--- Scheduling Results ---\n");
    printf("PID\tAT\tBT\tCT\tTAT\tWT\tRT\n");

    for (int i = 0; i < n; i++) {
        p[i].turnaround = p[i].completion - p[i].arrival;
        p[i].waiting = p[i].turnaround - p[i].burst;
        p[i].response = p[i].first_start - p[i].arrival;

        total_waiting += p[i].waiting;
        total_turnaround += p[i].turnaround;
        total_response += p[i].response;

        printf("P%d\t%d\t%d\t%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].arrival,
               p[i].burst,
               p[i].completion,
               p[i].turnaround,
               p[i].waiting,
               p[i].response);
    }

    printf("\nAverage Waiting Time: %.2f\n",
           total_waiting / n);
    printf("Average Turnaround Time: %.2f\n",
           total_turnaround / n);
    printf("Average Response Time: %.2f\n",
           total_response / n);

    printf("\nExecution Sequence:\n");
    for (int i = 0; i < segments; i++) {
        printf("P%d (%d-%d)",
               execution_pid[i],
               execution_start[i],
               execution_end[i]);

        if (i < segments - 1)
            printf(" -> ");
    }
    printf("\n");

    return 0;
}

