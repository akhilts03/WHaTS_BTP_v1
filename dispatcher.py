'''
This will have the dispatcher class

dispatcher : 
    an arrival queue
    a pending_mandatory_PQ
    a pending_optional_PQ
    list of processors
    a schedular for each algorithm
    a diagnostic function to print diagnostics
    a print schedule function to print the final schedule of each processor 
    
'''

import utils
import processor
import LLF
import EDF
import RM_P_New
import RM_NP
import preemption_handler

class Dispatcher: 
    def __init__(self,no_of_processors,tasklist):
        self.Queue = utils.CustomQueue()
        self.pq_m = utils.CustomPriorityQueue() # this has to be a priority queue. 
        self.pq_o = utils.CustomPriorityQueue() # this should also be a priority queue.
        self.processor_list = [processor.processor(i) for i in range(no_of_processors)]
        self.hyperperiod = None
        self.tasklist = tasklist
        self.p_handle = preemption_handler.preemption_handler(self)
        
    def load_tasks_into_queue(self,mk_pattern):
        if self.tasklist is None:
            t = utils.file_reader()
        else :
            t = self.tasklist
        self.tasklist = t
        d = utils.generate_jobs(t,utils.hyperperiod(t),mk_pattern)
        d_sorted = dict(sorted(d.items(),key=lambda item: item[0].deadline))  # They are sorted in ascending order of deadline of tasks
        self.hyperperiod = utils.hyperperiod(t)
        
        for t in range(self.hyperperiod) : 
            
            for task, jobs in d_sorted.items() : 
                
                if jobs.is_empty() or jobs.front()[1]>t : 
                    continue
                 
                self.Queue.insert(jobs.front())
                jobs.pop()
        
    
    def update_processors(self, time):
        for p in self.processor_list:
            p.update(time)
    
    def update_pending_queues(self,time, mode): 
        if mode == "LLF" :
            self.pq_m.update_laxities(time,self.hyperperiod)
            self.pq_o.update_laxities(time,self.hyperperiod)
        if mode == "EDF":
            self.pq_m.update_ttds(time,self.hyperperiod)
            self.pq_o.update_ttds(time,self.hyperperiod)
        
    #------------------------#------------------------#------------------------#------------------------#------------------------#------------------------#------------------------
    def run_np_rm(self):
        RM_NP.RateMonoNonPreemptiveSchedular(self)
    #------------------------#------------------------#------------------------#------------------------#------------------------#------------------------#------------------------
    def run_p_rm(self): # hybrid pre-emption -> preemption allowed for newly arriving tasks, but not for pending tasks
        RM_P_New.RateMonoPreemptiveSchedular(self)        
    #------------------------#------------------------#------------------------#------------------------#------------------------#------------------------#------------------------
    def run_edf(self):
        EDF.EarliestDeadlineFirstSchedular(self)
    #------------------------#------------------------#------------------------#------------------------#------------------------#------------------------#------------------------
    def run_llf(self): 
        LLF.LeastLaxityFirstSchedular(self)
    #------------------------#------------------------#------------------------#------------------------#------------------------#------------------------#------------------------
  
    def run(self, mode, mk_pattern):
        
        self.load_tasks_into_queue(mk_pattern)
        
        if mode == "RM_NP":
            self.run_np_rm()
        if mode == "RM_P":
            self.run_p_rm()
        if mode == "EDF":
            self.run_edf()
        if mode == "LLF":
            self.run_llf()

    def print_all_schedules(self) : 
        
        with open("schedule_output.txt", "w") as file:
            pass
    
        for p in self.processor_list: 
            p.print_schedule()
        

    def print_diagnostics(self) : 
        for t in self.tasklist : 
            print(t.name , t.Mandatory_jobsmissed , t.Optional_jobsmissed)
            # print(t.Mandatory_jobsmissed)
            # print(t.Optional_jobsmissed)
    
    def get_all_schedules(self):
        d = {}
        for p in self.processor_list:
            d[p.name] = p.get_schedule()
        
        return d


# testing        
# d = Dispatcher(2)
# d.run("np_rm","evenly")
# d.print_all_schedules()
# d.print_diagnostics()


     

            
            
        
        
        

