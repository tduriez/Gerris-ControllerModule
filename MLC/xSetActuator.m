function xSetActuator(idv,parameters)
ControllerFile=fullfile(parameters.problem_variables.SimDirectory,'python','user','controller.py');
if exist(ControllerFile,'file')
    delete(ControllerFile)
    while exist(ControllerFile,'file')
        fprintf('Waiting for controller file to disappear.\n');
        pause(0.1);
    end
end

fid=fopen(ControllerFile,'w');
fprintf(fid,'from math import *\n');
fprintf(fid,'import logging\n');
fprintf(fid,'import ConfigParser\n');
fprintf(fid,'import numpy as np\n');
fprintf(fid,'import math\n');
fprintf(fid,'import csv\n');
fprintf(fid,'import os, os.path\n');
fprintf(fid,'import time\n');
fprintf(fid,'\n');

fprintf(fid,'def custom_filter_inputs(all_samples,completed_time):\n');
fprintf(fid,'    values = [s.data.value for s in all_samples\n');
fprintf(fid,'                           if s.data.variable == ''T'' and s.time == completed_time\n');
fprintf(fid,'             ]\n');
fprintf(fid,'    return values\n');
fprintf(fid,'\n');

fprintf(fid,'def init(proc_index):\n');
fprintf(fid,'    pass\n');
fprintf(fid,'\n');

fprintf(fid,'def destroy(proc_index):\n');
fprintf(fid,'    pass\n');
fprintf(fid,'\n');

fprintf(fid,'def actuation(time, step, samples):\n');



fprintf(fid,'    act = 0\n');
fprintf(fid,'    completed_time = samples.getPreviousClosestTime(time)\n');
fprintf(fid,'    if completed_time:\n');
fprintf(fid,'        S = S = custom_filter_inputs(samples.all,completed_time)\n');
for i=1:8
fprintf(fid,'        S%d = S[%d]\n',i-1,i-1);
end
%fprintf(fid,'        filtered_samples = samples.samplesByTime(completed_time)\n');
%fprintf(fid,'        filtered_samples = samples.samplesByVariable(''T'')\n');
%fprintf(fid,'        filtered_samples = samples.samplesByLocation( (3,1,0) )\n');
%fprintf(fid,'        filtered_samples = custom_filter_inputs(samples.all)\n');
fprintf(fid,'        act = %s\n',strrep(idv.formal,'.*','*'));
fprintf(fid,'        if act < 0:\n');
fprintf(fid,'                act=0\n');
fprintf(fid,'        if act > %f:\n',parameters.problem_variables.maxact);
fprintf(fid,'                act=%f\n',parameters.problem_variables.maxact);
fprintf(fid,'        logging.info(''** fixed actuation ** step=%%d - t=%%.3f - act=%%.2f **'' %% (step, completed_time, act))\n');
fprintf(fid,'    return act\n');
    


%%