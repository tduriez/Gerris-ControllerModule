function J=MLC_Gerris_cylinder_evaluator(idv,parameters,i,fig)
    %% Variable grocery
    TControlStart=MLC_parameters.problem_variables.control_time;
    PythonScript=MLC_parameters.problem_variables.Python_script;
    ActMax=MLC_parameters.problem_variables.actmax;



    %% Setting up the simulation
    out=xSetFinalTime(parameters);
    out=xSetActuator(parameters);
    out=xSetMeasurement(parameters);
    
    try
    
    %% Simulation
    
        
     
    
    
    
    
    %% Get the cost
    
    
    
    %% Show results
    if nargin>3
    
    
    
    end
    %% deal with errors
    catch err
        fprintf(err.message);
       J=parameters.badvalue; 
    end
    
    