def RateMonoNonPreemptiveSchedular(self):
        for t in range(self.hyperperiod):            
            
            while not self.Queue.is_empty() and self.Queue.front()[1]==t:
                
                # subcase 2 : 
                
                assignedProcessor = 0
                
                for p in self.processor_list : 
                    if p.Time_remaining == 0:
                        
                        p.job = self.Queue.front()[0]
                        p.Time_remaining = p.job.task.wcet
                        assignedProcessor = 1
                        self.Queue.pop()
                        break
                 
                # subcase 1 : 
                
                if not assignedProcessor : 
                    if self.Queue.front()[0].bIsMandatory : 
                        self.pq_m.push(self.Queue.front()[0],self.Queue.front()[1],self.Queue.front()[0].task.deadline) # priority :  arrival time first then deadline
                        self.Queue.pop()
                    else : 
                        self.pq_o.push(self.Queue.front()[0],self.Queue.front()[1],self.Queue.front()[0].task.deadline)
                        self.Queue.pop()
             
            # after assigning all the tasks that arrive at time = t, if there are still idle processors, then assign them some pending tasks 
            
            for p in self.processor_list : 
                if p.Time_remaining== 0: 
                    
                    processorassigned = 0
                    
                    while not self.pq_m.is_empty():
                        if t + self.pq_m.top()[-1].task.wcet <= self.pq_m.top()[0] + self.pq_m.top()[-1].task.period and t + self.pq_m.top()[-1].task.wcet <= self.hyperperiod : 
                            p.job = self.pq_m.top()[-1]
                            p.Time_remaining = p.job.task.wcet
                            self.pq_m.pop()
                            processorassigned = 1
                            break
                        else :
                            self.pq_m.top()[-1].task.Mandatory_jobsmissed +=1
                            self.pq_m.pop()
                    
                    if processorassigned:
                        continue
                    
                    while not self.pq_o.is_empty():
                        if t + self.pq_o.top()[-1].task.wcet <= self.pq_o.top()[0] + self.pq_o.top()[-1].task.period and t + self.pq_o.top()[-1].task.wcet <= self.hyperperiod : 
                            p.job = self.pq_o.top()[-1]
                            p.Time_remaining = p.job.task.wcet
                            self.pq_o.pop()
                            break
                        else :
                            self.pq_o.top()[-1].task.Optional_jobsmissed +=1
                            self.pq_o.pop()
                                                        
            self.update_processors(t)

        while not self.pq_m.is_empty(): 
            t = self.pq_m.top()
            t[-1].task.Mandatory_jobsmissed+=1
            self.pq_m.pop()
        
        while not self.pq_o.is_empty():
            t = self.pq_o.top()
            t[-1].task.Optional_jobsmissed+=1
            self.pq_o.pop()