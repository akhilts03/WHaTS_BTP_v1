def EarliestDeadlineFirstSchedular(dispatcher_object): 

        for t in range(dispatcher_object.hyperperiod) :
            
            while not dispatcher_object.Queue.is_empty() and dispatcher_object.Queue.front()[1] == t : # pre-emptive arriving tasks handling 
                
                j = dispatcher_object.Queue.front()[0]
                j_ttd = j.task.deadline
                
                p_max_mand = None # keeping track of the processors running tasks with the lowest priority.
                p_max_opt = None
                t_max_mand = -1
                t_max_opt = -1
                
                foundProcessorForTask = 0
                for p in dispatcher_object.processor_list:
                    
                    if p.Time_remaining == 0:
                        p.job = dispatcher_object.Queue.front()[0]
                        p.Time_remaining = p.job.task.wcet
                        dispatcher_object.Queue.pop()
                        foundProcessorForTask = 1 # if you've found an idle processor for the task, then assign it to the incoming task and proceed to next incoming task
                        break
                    
                    if p.job.bIsMandatory :
                        
                        ttd = ((t//p.job.task.period)+1)*p.job.task.deadline - t
                        
                        if ttd > t_max_mand :
                            t_max_mand = ttd
                            p_max_mand = p
                        
                    else :
                        
                        ttd = ((t//p.job.task.period)+1)*p.job.task.deadline - t
                        
                        if ttd > t_max_opt : 
                            t_max_opt = ttd
                            p_max_opt = p
                
                if foundProcessorForTask : 
                    continue
                    
                if not dispatcher_object.Queue.front()[0].bIsMandatory : 
                    dispatcher_object.pq_o.push(dispatcher_object.Queue.front()[0], j_ttd, dispatcher_object.Queue.front()[0].task.wcet, t)
                    dispatcher_object.Queue.pop()
                    continue
                
                if j_ttd > t_max_mand and not p_max_opt : 
                    dispatcher_object.pq_m.push(dispatcher_object.Queue.front()[0], j_ttd , dispatcher_object.Queue.front()[0].task.wcet, t)
                    dispatcher_object.Queue.pop() 
                    continue   
                
                # pre-emption logic 
                if p_max_opt :     #------job-----------------ttd------------rem exec time------------------arrival time----------------------------#
                    dispatcher_object.pq_o.push(p_max_opt.job,  ((t//p_max_opt.job.task.period)+1)*p_max_opt.job.task.deadline - t,  p_max_opt.Time_remaining, 
                                   (t//p_max_opt.job.task.period) * p_max_opt.job.task.period )
                    p_max_opt.job = dispatcher_object.Queue.front()[0]
                    p_max_opt.Time_remaining = p_max_opt.job.task.wcet
                    dispatcher_object.Queue.pop()
                    continue
                 
                if p_max_mand : 
                    dispatcher_object.pq_m.push(p_max_mand.job,  ((t//p_max_mand.job.task.period)+1)*p_max_mand.job.task.deadline - t,  p_max_mand.Time_remaining, 
                                   (t//p_max_mand.job.task.period) * p_max_mand.job.task.period )
                    p_max_mand.job = dispatcher_object.Queue.front()[0]
                    p_max_mand.Time_remaining = p_max_mand.job.task.wcet
                    dispatcher_object.Queue.pop()
                    continue
              
            # pre-emptive pending tasks handling
            while not dispatcher_object.pq_m.is_empty() : 
                
                j_tuple = dispatcher_object.pq_m.top()
                j = j_tuple[-1]
                j_ttd = j_tuple[0]
                
                # if(j_tuple[1] + t > (t//j.task.period)*j.task.period + j.task.period) :
                #     dispatcher_object.pq_m.pop()
                #    # dispatcher_object.p_handle.track_missing(j,dispatcher_object.hyperperiod) ## to Handle missed tasks
                #     j.task.Mandatory_jobsmissed += 1
                #     continue
                
                Assigned = 0
                
                for p in dispatcher_object.processor_list : 
                    
                    if p.Time_remaining == 0 : 
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_m.pop()
                        Assigned = 1
                        break
                    
                    if not p.job.bIsMandatory : 
                        dispatcher_object.pq_o.push(p.job,  ((t//p.job.task.period)+1)*p.job.task.deadline - t,  p.Time_remaining, 
                                   (t//p.job.task.period) * p.job.task.period )
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_m.pop()
                        Assigned = 1
                        break
                    
                    ttd = ((t//p.job.task.period)+1)*p.job.task.deadline - t
                    
                    if j_ttd < ttd : 
                        dispatcher_object.pq_m.push(p.job,  ((t//p.job.task.period)+1)*p.job.task.deadline - t,  p.Time_remaining, 
                                   (t//p.job.task.period) * p.job.task.period)   
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_m.pop()
                        Assigned = 1
                    
                
                if not Assigned : 
                    break
                  
            while not dispatcher_object.pq_o.is_empty():
                
                j_tuple = dispatcher_object.pq_o.top()
                j = j_tuple[-1]
                j_ttd = j_tuple[0]
                
                # if(j_tuple[1] + t > (t//j.task.period)*j.task.period + j.task.period) : -- this part is not required for job level scheduling. Update_pending_queues() takes care of this
                #     dispatcher_object.pq_o.pop()
                #     #dispatcher_object.p_handle.track_missing(j,dispatcher_object.hyperperiod) ## to Handle missed tasks
                #     j.task.Optional_jobsmissed += 1 
                #     continue
                
                Assigned = 0
                
                for p in dispatcher_object.processor_list : 
                    
                    if p.Time_remaining == 0 : 
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_o.pop()
                        Assigned = 1
                        break                    
                    
                    if p.job.bIsMandatory : 
                        continue
                    
                    ttd = ((t//p.job.task.period)+1)*p.job.task.deadline - t
                    
                    if j_ttd < ttd :
                        dispatcher_object.pq_o.push(p.job,  ((t//p.job.task.period)+1)*p.job.task.deadline - t,  p.Time_remaining, 
                                   (t//p.job.task.period) * p.job.task.period)   
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_o.pop()
                        Assigned = 1
                        break 
                    
                if not Assigned :
                    break    
                       
                            
            dispatcher_object.update_processors(t)
            dispatcher_object.update_pending_queues(t,"EDF") # Need to write a function that dynamically updates the laxities of all jobs in the pending queues. should pop out jobs if their rem-exec-time
            # exceeds hyperperiod.--- DONE !
        
        # clean up
        
        while not dispatcher_object.pq_m.is_empty(): 
            t = dispatcher_object.pq_m.top()
            t[-1].task.Mandatory_jobsmissed+=1
            dispatcher_object.pq_m.pop()
        
        while not dispatcher_object.pq_o.is_empty():
            t = dispatcher_object.pq_o.top()
            t[-1].task.Optional_jobsmissed+=1
            dispatcher_object.pq_o.pop()