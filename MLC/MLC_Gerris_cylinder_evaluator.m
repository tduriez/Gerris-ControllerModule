function J=MLC_Gerris_cylinder_evaluator(idv,parameters,i,fig)
    %% Variable grocery
    curdir=pwd;
    if nargin<3
        i=[];
    end

    
    %% Setting up the simulation
    
    
    try
    
    %% Simulation
    
    if strcmp(parameters.evaluation_method,'mfile_multi')
        t=getCurrentTask();
        WorkerID=t.ID;
    else
        WorkerID=[];
    end
        
        
        
        if ~exist(sprintf('%s%d',parameters.problem_variables.SimDirectory,WorkerID),'dir')
            copyfile(parameters.problem_variables.SimDirectory,sprintf('%s%d',parameters.problem_variables.SimDirectory,WorkerID));
            pause(2);
        end
            
        xSetFinalTime(parameters.problem_variables,parameters.verbose>2,WorkerID);
        xSetActuator(idv,parameters,WorkerID);
            
    cd(sprintf('%s%d',parameters.problem_variables.SimDirectory,WorkerID))
    system('./clear_results')
    system('./exec_from_steady_state.sh')
    cd (curdir)
    
        
     
    
    
    
    
    %% Get the cost
    
    [t,x,y,s,b,dJa,dJb]=xGetResults(idv,parameters,WorkerID);
    
    if t(end)==parameters.problem_variables.total_time
        J=trapz(t,dJa+parameters.problem_variables.gamma*dJb);
    else
        J=t(end)*parameters.badvalue;
    end
    
    %% Show results
    figure(667)
    if nargin>3
          subplot(4,1,1)
    plot(t,s)
    
    subplot(4,1,2)
    plot(t,b)
    
    subplot(4,1,3)
    plot(t,dJa,t,dJb);
    
    subplot(4,1,4)
    plot(t,cumtrapz(t,dJa),t,cumtrapz(t,dJb),...
    t,cumtrapz(t,dJa+parameters.problem_variables.gamma*dJb));
    
    drawnow
    
    end
    %% deal with errors
    catch err
        fprintf(err.message);
       J=parameters.badvalue; 
    end
    
    