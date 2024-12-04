
'''
This class is meant to enable preemption handling and track deadline misses. Needs to be worked on.

'''

class preemption_handler: # preemption handler object
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        # self.pq_m = dispatcher.pq_m
        # self.pq_o = dispatcher.pq_o -- not really required.
        self.Missed_jobs_dict = {}
        self.preemption_dict = {}
        
    def preempt(self,job):
        if job.task.name not in self.preempt_dict : 
            self.preemption_dict[job.task.name] = 1
        else:
            self.preemption_dict[job.task.name] +=1
    
    def track_missing(self,job,time = None):
        
        for p in self.dispatcher.processor_list :
            
            d = p.job_schedule 
            
            for t,j in d.items():
                if j is job : 
                    if job.task.name not in self.Missed_jobs_dict : 
                        self.Missed_jobs_dict[job.task.name] = [t]
                        if time :
                            self.Missed_jobs_dict[job.task.name].append((time,time+1))
                    else : 
                        self.Missed_jobs_dict[job.task.name].append(t)
                        if time : 
                            self.Missed_jobs_dict[job.task.name].append((time,time+1))
            
        

