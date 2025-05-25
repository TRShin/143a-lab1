### Fill in the following information before submitting
# Group id: 46
# Members: Wilberth Gonzalez, Varun Sunkavalli, Trentin Shin



from collections import deque

# PID is just an integer, but it is used to make it clear when a integer is expected to be a valid PID.
PID = int

# This class represents the PCB of processes.
# It is only here for your convinience and can be modified however you see fit.
class PCB:
    pid: PID
    priority: int

    def __init__(self, pid: PID, priority: int):
        self.pid = pid
        self.priority = priority

# This class represents the Kernel of the simulation.
# The simulator will create an instance of this object and use it to respond to syscalls and interrupts.
# DO NOT modify the name of this class or remove it.
class Kernel:
    scheduling_algorithm: str
    ready_queue: deque[PCB]
    waiting_queue: deque[PCB]
    rr_queue: deque[PCB]
    running: PCB
    idle_pcb: PCB
    time_elapsed: int
    process_start_time: int
    time_quantum: int

    # Called before the simulation begins.
    # Use this method to initilize any variables you need throughout the simulation.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def __init__(self, scheduling_algorithm: str, logger):
        self.scheduling_algorithm = scheduling_algorithm
        self.ready_queue = deque()
        self.waiting_queue = deque()
        self.rr_queue = deque()
        self.idle_pcb = PCB(0, float('inf'))
        self.running = self.idle_pcb
        self.logger = logger
        self.time_elapsed = 0
        self.process_start_time = 0
        self.time_quantum = 40

    # This method is triggered every time a new process has arrived.
    # new_process is this process's PID.
    # priority is the priority of new_process.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def new_process_arrived(self, new_process: PID, priority: int, process_type: str) -> PID:
        if self.scheduling_algorithm == "FCFS":
            new_pcb = PCB(new_process, priority)
            if self.running == self.idle_pcb:
                self.running = new_pcb
            else:
                self.ready_queue.append(new_pcb)
        elif self.scheduling_algorithm == "Priority":
            new_pcb = PCB(new_process, priority)
            if self.running == self.idle_pcb:
                self.running = new_pcb
            else:
                running_priority = self.running.priority
                running_pid = self.running.pid
                if (priority < running_priority) or (priority == running_priority and new_process < running_pid):
                    self.ready_queue.append(self.running)
                    self.running = new_pcb
                else:
                    self.ready_queue.append(new_pcb)
        elif self.scheduling_algorithm == "RR":
            new_pcb = PCB(new_process, priority)
            if self.running == self.idle_pcb:
                self.running = new_pcb
                self.process_start_time = self.time_elapsed
            else:
                self.rr_queue.append(new_pcb)

        return self.running.pid

    # This method is triggered every time the current process performs an exit syscall.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_exit(self) -> PID:
        self.choose_next_process()

        if self.scheduling_algorithm == "RR" and self.running != self.idle_pcb:
            self.process_start_time = self.time_elapsed

        return self.running.pid

    # This method is triggered when the currently running process requests to change its priority.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_set_priority(self, new_priority: int) -> PID:
        self.running.priority = new_priority
        if self.scheduling_algorithm == "Priority":
            self.ready_queue.append(self.running)
            self.choose_next_process()

        return self.running.pid


    # This is where you can select the next process to run.
    # This method is not directly called by the simulator and is purely for your convinience.
    # Feel free to modify this method as you see fit.
    # It is not required to actually use this method but it is recommended.
    def choose_next_process(self):
        if self.scheduling_algorithm == "RR":
            if len(self.rr_queue) > 0:
                self.running = self.rr_queue.popleft()
            else:
                self.running = self.idle_pcb
        elif self.scheduling_algorithm == "FCFS":
            if len(self.ready_queue) > 0:
                self.running = self.ready_queue.popleft()
            else:
                self.running = self.idle_pcb
        elif self.scheduling_algorithm == "Priority":
            if len(self.ready_queue) > 0:
                best_priority = min(self.ready_queue, key=lambda pcb: (pcb.priority, pcb.pid))
                self.ready_queue.remove(best_priority)
                self.running = best_priority
            else:
                self.running = self.idle_pcb

    # Second Lab Methods:
    # This method is triggered when the currently running process requests to initialize a new semaphore.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_init_semaphore(self, semaphore_id: int, initial_value: int):
        return

    # This method is triggered when the currently running process calls p() on an existing semaphore.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_semaphore_p(self, semaphore_id: int) -> PID:
        return self.running.pid

    # This method is triggered when the currently running process calls v() on an existing semaphore.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_semaphore_v(self, semaphore_id: int) -> PID:
        return self.running.pid

    # This method is triggered when the currently running process requests to initialize a new mutex.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_init_mutex(self, mutex_id: int):
        return

    # This method is triggered when the currently running process calls lock() on an existing mutex.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_mutex_lock(self, mutex_id: int) -> PID:
        return self.running.pid

    # This method is triggered when the currently running process calls unlock() on an existing mutex.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_mutex_unlock(self, mutex_id: int) -> PID:
        return self.running.pid

    # This function represents the hardware timer interrupt.
    # It is triggered every 10 microseconds and is the only way a kernel can track passing time.
    # Do not use real time to track how much time has passed as time is simulated.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def timer_interrupt(self) -> PID:
        self.time_elapsed += 10

        if self.scheduling_algorithm == "RR" and self.running != self.idle_pcb:
            current_process_time = self.time_elapsed - self.process_start_time
            if current_process_time >= self.time_quantum and len(self.rr_queue) > 0:
                self.rr_queue.append(self.running)
                self.logger.log(f" Quantum Expired! Process: {self.running.pid} preempted. ")
                self.choose_next_process()
                if self.running != self.idle_pcb:
                    self.process_start_time = self.time_elapsed

        return self.running.pid