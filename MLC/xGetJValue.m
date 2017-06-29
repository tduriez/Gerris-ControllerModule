function J=xGetJValue(idv,parameters,WorkerID)
    if nargin <3
        WorkerID=[];
    end

    curdir=pwd;
    workingdir=sprintf('%s%d',parameters.problem_variables.SimDirectory,WorkerID);
    
    cd(workingdir);
    
    %% Get sensor values.
    logfile=fullfile('results','sensors.txt');
    A=importdata(logfile);
    n=size(A.data,1);
    t=reshape(A.data(:,1),8,n/8)';
    t=t(:,1);
    s=reshape(A.data(:,9),8,n/8)';
    x=A.data(1:8,2)
    y=A.data(1:8,3)
    figure(667)
   
    J=0
    cd(curdir)
    dJa=sum(s,2);
    
    ControlLaw=idv.formal;
    for i=1:8
        ControlLaw=strrep(ControlLaw,sprintf('S%d',i-1),sprintf('s(:,%d)',i));
    end
    b=0;
    eval(sprintf('b=%s;',ControlLaw));
    b=b+s(:,1)*0;
    
    dJb=b.^2;
    
    subplot(4,1,1)
    plot(t,s)
    
    subplot(4,1,2)
    plot(t,b)
    
    subplot(4,1,3)
    plot(t,dJa,t,dJb);
    
    subplot(4,1,4)
    plot(t,cumtrapz(t,dJa),t,cumtrapz(t,dJb),...
    t,cumtrapz(t,dJa+parameters.problem_variables.gamma*dJb));
    
    
    