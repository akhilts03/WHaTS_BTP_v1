'''
This will have the Task and Job classes.

Task : 
    Name
    period
    deadline
    wcet
    m
    k
    jobsmissed = 0 by default.


Job : 
    Task
    isMandatory



'''

class Task:
    def __init__(self, name, period,deadline, wcet, m, k):
        self.name = name
        self.period = period
        self.deadline = deadline
        self.wcet = wcet
        self.m = m
        self.k = k
        self.Mandatory_jobsmissed = 0
        self.Optional_jobsmissed = 0
    
    
    def __repr__(self):
        return f"({self.name} : {self.period},{self.deadline},{self.wcet},{self.m},{self.k})"
    

class Job():
    def __init__(self, task, bIsMandatory):
        self.task = task
        self.bIsMandatory = bool(bIsMandatory)
        
    def __lt__(self, other):    
        return self.task.deadline > other.task.deadline  # Later deadline = lower priority in the heap
        
    def __repr__(self):
        return f"(Job : {self.bIsMandatory})"
    

#--DEBUGGING---
    
# t1 = Task("t1",2,2,2,2,2)
# t2 = Task("t2",3,3,3,3,3)

# j1 = Job(t1,1)
# j2 = Job(t1,0)

# print(j1==j1)
# print(j1==j2)


