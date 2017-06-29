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
    system('./exec_from_steady_state_single.sh')
    cd (curdir)
    
        
     
    
    
    
    
    %% Get the cost
    
    
    
    %% Show results
    if nargin>3
    
    
    
    end
    %% deal with errors
    catch err
        fprintf(err.message);
       J=parameters.badvalue; 
    end
    
    