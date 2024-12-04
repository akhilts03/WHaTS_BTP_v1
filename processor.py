'''
The processor class will have : 

The name of the processor.
The job object that it is running.
The amount of time left for it to run that job.
A final schedule of all tasks that ran on this processor.
An update function that reduces the time left to run the job, and adds a new entry to the final_schedule on what to run in that interval. If it hits 0, set the job to None.
It could be a derived class of the dispatcher module for it to share the time variable with the dispatcher.

'''

import numpy as np

class processor: 
    def __init__(self,name):
        self.name = name
        self.job = None
        self.Time_remaining = 0
        self.extra_information = None
        self.final_schedule = {}
        self.job_schedule = {}
    
    def update(self, time):

        if self.Time_remaining == 0 : 
            self.job = None
            self.extra_information = None
            self.final_schedule[(time,time+1)] = None
            return

        self.final_schedule[(time,time+1)] = self.job.task.name
        self.job_schedule[(time,time+1)] = self.job
        self.Time_remaining -= 1
                
    def get_schedule(self) : 
        return self.final_schedule
        
    def utilization(self) :
        t = 0
        n = 0
        for time,task in self.final_schedule.items() :
            n+=1
            if task is not None :
                t+=1
        
        return (t/n) * 100.0
    
    # def print_schedule(self, filename="schedule_output.txt"):
    #     with open(filename, 'a') as file:
    #         file.write("Processor: " + str(self.name) + " , " + "Utilization : " + f"{self.utilization():.2f}%\n")

    #         max_interval = max(interval[1] for interval in self.final_schedule.keys())  # Max interval for column width
    #         row = []

    #         for t in range(max_interval + 1):
    #             # Add task or None if interval is empty
    #             task = self.final_schedule.get((t, t+1), None)
    #             row.append(task if task is not None else "None")

    #         file.write(" ".join(row) + "\n")  # Write row as a line of tasks for this processor

            
    def print_schedule(self, filename="schedule_output.txt"):
        with open(filename, 'a') as file:
            # Write processor name
            file.write("Processor: " + str(self.name) + " , " + "Utilization : " + str(self.utilization()) + "%" + "\n")
            
            # Write each entry in the final schedule
            for t, j in self.final_schedule.items():
                file.write(f"{t}: {j}\n")
            