def RateMonoPreemptiveSchedular(dispatcher_object):
        for t in range(dispatcher_object.hyperperiod): 
            
            while not dispatcher_object.Queue.is_empty() and dispatcher_object.Queue.front()[1]==t : 

                p_max_mand = None # keeping track of the processors running tasks with the lowest priority (max deadline).
                p_max_opt = None
                d_max_mand = -1
                d_max_opt = -1
                
                foundProcessorForTask = 0
                for p in dispatcher_object.processor_list:
                    
                    if p.Time_remaining == 0:
                        p.job = dispatcher_object.Queue.front()[0]
                        p.Time_remaining = p.job.task.wcet
                        dispatcher_object.Queue.pop()
                        foundProcessorForTask = 1 # if you've found an idle processor for the task, then assign it to the incoming task and proceed to next incoming task
                        break
                    
                    if p.job.bIsMandatory :
                        if p.job.task.deadline > d_max_mand :
                            d_max_mand = p.job.task.deadline
                            p_max_mand = p
                        
                    else :
                        if p.job.task.deadline > d_max_opt : 
                            d_max_opt = p.job.task.deadline
                            p_max_opt = p
                                       
                # if you reach here in this while loop, that means there was no processor available for the the arriving task
                
                if foundProcessorForTask : 
                    continue
                
                if not dispatcher_object.Queue.front()[0].bIsMandatory : 
                    dispatcher_object.pq_o.push(dispatcher_object.Queue.front()[0],dispatcher_object.Queue.front()[0].task.deadline,dispatcher_object.Queue.front()[0].task.wcet,dispatcher_object.Queue.front()[1])
                    dispatcher_object.Queue.pop()
                    continue
                
                if dispatcher_object.Queue.front()[0].task.deadline > d_max_mand and not p_max_opt: 
                    dispatcher_object.pq_m.push(dispatcher_object.Queue.front()[0],dispatcher_object.Queue.front()[0].task.deadline,dispatcher_object.Queue.front()[0].task.wcet,dispatcher_object.Queue.front()[1])
                    dispatcher_object.Queue.pop() 
                    continue
                                
                # pre-emption logic 
                if p_max_opt :     #------job-----------------deadline------------rem exec time------------------arrival time----------------------------#
                    dispatcher_object.pq_o.push(p_max_opt.job, p_max_opt.job.task.deadline, p_max_opt.Time_remaining, (t//p_max_opt.job.task.period) * p_max_opt.job.task.period)
                    p_max_opt.job = dispatcher_object.Queue.front()[0]
                    p_max_opt.Time_remaining = p_max_opt.job.task.wcet
                    dispatcher_object.Queue.pop()
                    continue
                 
                if p_max_mand : 
                    dispatcher_object.pq_m.push(p_max_mand.job, p_max_mand.job.task.deadline, p_max_mand.Time_remaining, (t//p_max_mand.job.task.period) * p_max_mand.job.task.period )
                    p_max_mand.job = dispatcher_object.Queue.front()[0]
                    p_max_mand.Time_remaining = p_max_mand.job.task.wcet
                    dispatcher_object.Queue.pop()
                    continue
                
                
            # # pre-emptive pending tasks handling
            while not dispatcher_object.pq_m.is_empty() : 
                
                j_tuple = dispatcher_object.pq_m.top()
                j = j_tuple[-1]
                j_d = j_tuple[0] # not required.
                
                if(j_tuple[1] + t > (t//j.task.period)*j.task.period + j.task.period) :
                    dispatcher_object.pq_m.pop()
                   # dispatcher_object.p_handle.track_missing(j,dispatcher_object.hyperperiod) ## to Handle missed tasks
                    j.task.Mandatory_jobsmissed += 1
                    continue
                
                Assigned = 0
                
                for p in dispatcher_object.processor_list : 
                    
                    if p.Time_remaining == 0 : 
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_m.pop()
                        Assigned = 1
                        break
                    
                    if not p.job.bIsMandatory : 
                        dispatcher_object.pq_o.push(p.job,  p.job.task.deadline,  p.Time_remaining, 
                                   (t//p.job.task.period) * p.job.task.period )
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_m.pop()
                        Assigned = 1
                        break
                    
                    d = p.job.task.deadline
                    
                    if j_d < d : 
                        dispatcher_object.pq_m.push(p.job,  p.job.task.deadline,  p.Time_remaining, 
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
                j_d = j_tuple[0]
                
                if(j_tuple[1] + t > (t//j.task.period)*j.task.period + j.task.period) :
                    dispatcher_object.pq_o.pop()
                    #dispatcher_object.p_handle.track_missing(j,dispatcher_object.hyperperiod) ## to Handle missed tasks
                    j.task.Optional_jobsmissed += 1 
                    continue
                
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
                    
                    d = p.job.task.deadline
                    
                    if j_d < d :
                        dispatcher_object.pq_o.push(p.job, p.job.task.deadline,  p.Time_remaining, 
                                   (t//p.job.task.period) * p.job.task.period)   
                        p.job = j
                        p.Time_remaining = j_tuple[1]
                        dispatcher_object.pq_o.pop()
                        Assigned = 1
                        break 
                    
                if not Assigned :
                    break    
                
            
            # # after assigning all the tasks that arrive at time = t, if there are still idle processors, then assign them some pending tasks or tasks that were pre-empted.
            # for p in dispatcher_object.processor_list :   # This part is non-pre-emptive
            #     if p.Time_remaining== 0: 
                    
            #         processorassigned = 0
                    
            #         while not dispatcher_object.pq_m.is_empty():
            #                #---if the task cannot complete before it's deadline and before the end of the hyperperiod, then it has been missed. Need to report.---------------#
            #             if t + dispatcher_object.pq_m.top()[1] <= dispatcher_object.pq_m.top()[2] + dispatcher_object.pq_m.top()[-1].task.period and t + dispatcher_object.pq_m.top()[1] <= dispatcher_object.hyperperiod : 
            #                 p.job = dispatcher_object.pq_m.top()[-1]
            #                 p.Time_remaining = p.job.task.wcet
            #                 dispatcher_object.pq_m.pop()
            #                 processorassigned = 1
            #                 break
            #             else :
            #                 dispatcher_object.p_handle.track_missing(dispatcher_object.pq_m.top()[-1],t) ## to Handle missed tasks
            #                 dispatcher_object.pq_m.top()[-1].task.Mandatory_jobsmissed +=1
            #                 dispatcher_object.pq_m.pop()
                    
            #         if processorassigned:
            #             continue
                    
            #         while not dispatcher_object.pq_o.is_empty():
            #                #---if the task cannot complete before it's deadline and before the end of the hyperperiod, then it has been missed. Need to report.---------------#
            #             if t + dispatcher_object.pq_o.top()[1] <= dispatcher_object.pq_o.top()[2] + dispatcher_object.pq_o.top()[-1].task.period and t + dispatcher_object.pq_o.top()[1] <= dispatcher_object.hyperperiod : 
            #                 p.job = dispatcher_object.pq_o.top()[-1]
            #                 p.Time_remaining = p.job.task.wcet
            #                 dispatcher_object.pq_o.pop()
            #                 break
            #             else :
            #                 dispatcher_object.p_handle.track_missing(dispatcher_object.pq_o.top()[-1],t) ## to Handle missed tasks
            #                 dispatcher_object.pq_o.top()[-1].task.Optional_jobsmissed +=1
            #                 dispatcher_object.pq_o.pop()
                
            dispatcher_object.update_processors(t)
        
        while not dispatcher_object.pq_m.is_empty(): 
            t = dispatcher_object.pq_m.top()
           # dispatcher_object.p_handle.track_missing(dispatcher_object.pq_m.top()[-1],dispatcher_object.hyperperiod) ## to Handle missed tasks
            t[-1].task.Mandatory_jobsmissed+=1
            dispatcher_object.pq_m.pop()
        
        while not dispatcher_object.pq_o.is_empty():
            t = dispatcher_object.pq_o.top()
           # dispatcher_object.p_handle.track_missing(dispatcher_object.pq_o.top()[-1],dispatcher_object.hyperperiod) ## to Handle missed tasks
            t[-1].task.Optional_jobsmissed+=1
            dispatcher_object.pq_o.pop()
            
        
        # for task,l in dispatcher_object.p_handle.Missed_jobs_dict.items() :
        #     print(task, list(set(l))) 
    
