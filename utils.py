'''
File reader function : 
    reads input file
    returns a list of task objects

Hyperperiod calculator : 
    takes a list of task objects
    returns the hyperperiod of all those tasks
    
Job generator : 
    Takes a list of tasks
    Takes the hyperperiod
    Taks a pattern
    For each task, generates a list of tuples of (job objects according to the m-k pattern, arrival time) for the hyperperiod
    Returns a dictionary with keys as the task and the list of tuples as values for the correspoding tasks

Custom_queues, and priority_queues for implementation.

'''


import math
from functools import reduce
import tkinter as tk
from tkinter import messagebox, filedialog
import Task 
import heapq


# # Helper function to calculate LCM of two numbers
# def nLcm(a, b):
#     return abs(a.deadline * b.deadline) // math.gcd(a.deadline, b.deadline)

# # Helper function to calculate LCM of a list of numbers
# def nHyperperiod(numbers):
#     return reduce(nLcm, numbers)

def lcm(a, b):
    return a * b // math.gcd(a, b)

def hyperperiod(tasks):
    """
    Calculate the LCM of deadlines of all tasks in the list.

    Parameters:
    - tasks: List of task objects, each with a 'deadline' attribute.

    Returns:
    - The LCM of all task deadlines.
    """
    deadlines = [task.deadline for task in tasks]
    lcm_result = deadlines[0]
    for deadline in deadlines[1:]:
        lcm_result = lcm(lcm_result, deadline)
    return lcm_result

    


def file_reader():
        file_path = filedialog.askopenfilename(title="Select Task File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        
        if not file_path:
            return
        
        task_list = []

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) != 6:
                        raise ValueError("Invalid line format")

                    task_name, period ,deadline, wcet,m, k = parts
                    wcet = int(wcet)
                    period = int(period)
                    deadline = int(deadline)
                    m = int(m)
                    k = int(k)

                    if wcet <= 0 or period <=0 or deadline <= 0 or m <= 0 or k <= 0 or m > k:
                        raise ValueError("Invalid task parameters")
                                        
                    # Task object format : (name, period, deadline, wcet, m, k)
                    task_list.append(Task.Task(task_name, period, deadline, wcet, m, k))

        except (ValueError, IOError) as e:
            messagebox.showerror("Error Loading File", f"An error occurred while loading the file:\n{e}")
    
        return task_list


class CustomQueue:
    def __init__(self):
        self.queue = []
        
    def __repr__(self) -> str:
        return f"{self.queue}"
            

    def insert(self, element):
        """Insert an element at the end of the queue."""
        self.queue.append(element)

    def pop(self):
        """Remove and return the front element of the queue. Raise an exception if the queue is empty."""
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            raise IndexError("Pop from an empty queue")

    def front(self):
        """Return the front element of the queue without removing it. Raise an exception if the queue is empty."""
        if not self.is_empty():
            return self.queue[0]
        else:
            raise IndexError("Front called on an empty queue")

    def size(self):
        """Return the size of the queue."""
        return len(self.queue)

    def is_empty(self):
        """Return whether the queue is empty or not."""
        return len(self.queue) == 0
    
    def print_queue(self):
        print(self.queue)
        


class CustomPriorityQueue:
    def __init__(self):
        self.queue = []
    
    def push(self, item, *args):
        # Insert (args..., item) so *args are used as sorting parameters
        # and item is stored at the end
        heapq.heappush(self.queue, (*args, item))
    
    def pop(self):
        # Removes and returns the item with the highest combined priority
        if not self.is_empty():
            return heapq.heappop(self.queue)[-1]  # Return only the item
        else:
            raise IndexError("pop from empty priority queue")
    
    def top(self):
        # Look at the item with the highest priority without removing it
        if not self.is_empty():
            return self.queue[0] #[-1],self.queue[0][0]  # Return only the item
        else:
            raise IndexError("peek from empty priority queue")
    
    def is_empty(self):
        # Returns True if the queue is empty
        return len(self.queue) == 0

    def __len__(self):
        # Returns the number of items in the queue
        return len(self.queue)
    
    def update_laxities(self,current_time, hyperperiod):
        # Create a new queue to avoid modifying the queue during iteration
        new_queue = []
        
        while self.queue:
            # Pop each item from the queue
            item = heapq.heappop(self.queue)
            laxity, remaining_exec_time, arrival_time, job = item
            
            # Decrease laxity by one
            updated_laxity = laxity - 1
            
            # Check if job should be removed due to negative laxity or exceeding hyperperiod
            if updated_laxity < 0 or current_time + remaining_exec_time > hyperperiod:
                job.task.Mandatory_jobsmissed += job.bIsMandatory
                job.task.Optional_jobsmissed += not job.bIsMandatory
                continue  # Skip adding this job back to the queue
            
            # Push the updated item back into the new queue
            heapq.heappush(new_queue, (updated_laxity, remaining_exec_time, arrival_time, job))
        
        # Replace the old queue with the updated queue
        self.queue = new_queue

    def update_ttds(self,current_time, hyperperiod):
        # Create a new queue to avoid modifying the queue during iteration
        new_queue = []
        
        while self.queue:
            # Pop each item from the queue
            item = heapq.heappop(self.queue)
            ttd, remaining_exec_time, arrival_time, job = item
            
            # Decrease laxity by one
            updated_ttd = ttd - 1
            
            # Check if job should be removed due to negative laxity or exceeding hyperperiod
            if updated_ttd < remaining_exec_time or current_time + remaining_exec_time > hyperperiod:
                job.task.Mandatory_jobsmissed += job.bIsMandatory
                job.task.Optional_jobsmissed += not job.bIsMandatory
                continue  # Skip adding this job back to the queue
            
            # Push the updated item back into the new queue
            heapq.heappush(new_queue, (updated_ttd, remaining_exec_time, arrival_time, job))
        
        # Replace the old queue with the updated queue
        self.queue = new_queue
        
        

# # Example usage:
# pq = FlexiblePriorityQueue()
# pq.push("task1", 3, 10, "A")  # Priority, deadline, task name
# pq.push("task2", 1, 5, "B")   # Priority, deadline, task name
# pq.push("task3", 1, 3, "C")   # Priority, deadline, task name
# pq.push("task4", 2, 8, "D")   # Priority, deadline, task name

# while not pq.is_empty():
#     print(pq.pop())  # Should print tasks in order of priority, deadline, task name


         
def sGenerate_evenly_pattern2(task, hyperperiod) :  # this is the window logic.
    pattern = ""
    m = task.m
    k = task.k
    p = task.period
    n = hyperperiod // p   # assumption: n >= k  --- edge case to fix

    # Handle edge case where n < k
    if n < k:
        for j in range(n):
            success_index = math.floor(j * k / n)
            if j == success_index:
                pattern += "1"
            else:
                pattern += "0"
    else:
        # Ensure m executions in every k interval
        for i in range(n):
            count = sum(1 for char in pattern[max(0, i - k + 1):i + 1] if char == "1")
            if count < m:
                pattern += "1"
            else:
                pattern += "0"

    return pattern



def sGenerate_deeply_red_pattern2(task, hyperperiod):
    m = task.m 
    k = task.k
    p = task.period
    n = hyperperiod // p  # assumption: n >= k --- edge case fixed
    
    # Generate a basic pattern first
    pattern = "1" * m + "0" * (k - m)
    pattern = (pattern * math.ceil(n / k))[:n]

    # Adjust to ensure at least m executions in every k interval
    for i in range(n - k + 1):
        window = pattern[i:i + k]
        if window.count("1") < m:
            # Add more "1"s to meet the minimum requirement
            for j in range(i, i + k):
                if pattern[j] == "0":
                    pattern = pattern[:j] + "1" + pattern[j + 1:]
                    if pattern[i:i + k].count("1") >= m:
                        break

    return pattern


def sGenerate_evenly_pattern(task, hyperperiod): # this is the book logic. 
        pattern = ""
        m = task.m
        k = task.k
        p = task.period
        n = hyperperiod // p   # assumption: n >= k  --- edge case to fix
        
        # Handle edge case where n < k
        if n < k:
            for j in range(n):
                success_index = math.floor(j * k / n)
                if j == success_index:
                    pattern += "1"
                else:
                    pattern += "0"
        else:
            for j in range(n):
                # Apply the given formula for the regular case
                success_index = math.floor(math.ceil(j * m / k) * k / m)
                if j == success_index:
                    pattern += "1"
                else:
                    pattern += "0"
        
        return pattern


def sGenerate_deeply_red_pattern(task,hyperperiod):
        m = task.m 
        k = task.k
        p = task.period
        # n is no. of instances of the task.
        n = hyperperiod//p  #assumption : n>=k  --- edge case yet to fix # FIXED !
        
        # hyperperiod would be more than k*p since n (no. of instances) is >=k. if less, ceiling integer division would return 1. no need to change anything...
        pattern = "1" * m + "0" * (k - m) 
        pattern = (pattern * math.ceil(n/k))[:n]
        #pattern = (pattern * math.ceil(hyperperiod // (k)*p))[:n]  # why is it k-1 and not k ? # changed k-1 to k.
                    
        return pattern
    
def sGenerate_all_mandatory(task,hyperperiod):
        p = task.period
        n = hyperperiod//p
        pattern = "1"*n 
        return pattern

# Function to generate jobs for each task according to the pattern
def generate_jobs(tasks, hyperperiod, pattern_type="evenly"):
    """
    Generate jobs for each task based on the chosen pattern and return as a dictionary.

    Parameters:
    - tasks: List of task objects, each with m, k, period attributes.
    - hyperperiod: The hyperperiod value for which the patterns are generated.
    - pattern_type: The type of pattern to generate ('evenly', 'deeply_red', 'all_mandatory').

    Returns:
    - Dictionary where keys are tasks and values are queues of jobs (1 for mandatory, 0 for optional).
    """
    jobs_dict = {}

    for task in tasks:
        # Generate the pattern based on the specified type
        if pattern_type == "evenly":
            pattern = sGenerate_evenly_pattern(task, hyperperiod)
        elif pattern_type == "deeply_red":
            pattern = sGenerate_deeply_red_pattern(task, hyperperiod)
        elif pattern_type == "all_mandatory":
            pattern = sGenerate_all_mandatory(task, hyperperiod)
        else:
            raise ValueError("Invalid pattern type. Choose 'evenly', 'deeply_red', or 'all_mandatory'.")

        # Convert pattern string to list of integers (1 for mandatory, 0 for optional)
        
        jobs = CustomQueue()
        
        i = 0
        
        for char in pattern: 
            jobs.insert((Task.Job(task,bool(int(char))),i*task.period))   
            i += 1    
        # jobs = [Task.Job(task,bool(int(char))) for char in pattern]
        
        jobs_dict[task] = jobs

    return jobs_dict

# testing

# t = [Task.Task("t1",4,4,1,3,5),Task.Task("t2",3,3,1,1,4),Task.Task("t3",7,7,1,4,5)]
# # t2 = Task.Task("t2",3,3,1,4)
# # t3 = Task.Task("t3",7,7,4,5)

# hp = hyperperiod(t)

# s1 = sGenerate_evenly_pattern2(t[0],hp)
# s2 = sGenerate_evenly_pattern2(t[1],hp)
# s3 = sGenerate_evenly_pattern2(t[2],hp)

# print(s1)
# print(s2)
# print(s3)

# print("---------------------------------------------")

# s1 = sGenerate_evenly_pattern(t[0],hp)
# s2 = sGenerate_evenly_pattern(t[1],hp)
# s3 = sGenerate_evenly_pattern(t[2],hp)

# print(s1)
# print(s2)
# print(s3)

# print(bool(int("0")))


# d = generate_jobs(t,hp,"evenly")

# print(d)

# these two are enough.
# t = file_reader()
# d = generate_jobs(t,hyperperiod(t),"evenly")

# print(d)


# pq = CustomPriorityQueue()


# pq.push(t[2],0,t[2].deadline)
# pq.push(t[0],0,t[0].deadline)
# pq.push(t[1],0,t[1].deadline)


# print(pq.top())
# pq.pop()

# print(pq.top())
# pq.pop()
# print(pq.top())
# pq.pop()
