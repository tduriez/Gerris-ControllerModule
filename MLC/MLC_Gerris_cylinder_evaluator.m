function J=MLC_Gerris_cylinder_evaluator(idv,parameters,i,fig)
    %% Variable grocery
    curdir=pwd;


    %% Setting up the simulation
    xSetFinalTime(parameters.problem_variables,parameters.verbose>2);
    xSetActuator(idv,parameters);
    
    try
    
    %% Simulation
    cd(parameters.problem_variables.SimDirectory)
    system('./exec_from_steady_state.sh')
    
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
    
    