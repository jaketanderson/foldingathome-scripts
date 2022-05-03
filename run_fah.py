import os
import json
import multiprocessing as mp
import time
import subprocess


#My script for running Folding@Home on Ubuntu 20.04 and restarting the client if the cpu gets too hot.



#Get the temperatures of the cpus from the `sensors` package
def get_temps():

    stream = os.popen("sensors -j")
    output_json = json.loads(stream.read())
    
    list_temps = []
    
    #Should work for any # of cpus, starting with 0
    for i in range(0, int(mp.cpu_count()/2)):
        
        #If you have a different cpu architecture, you may need to navigate to a
        #different part of the dictionary given by running the `sensors` command.
        list_temps.append(output_json[u'coretemp-isa-0000'][u'Core {}'.format(i)][u'temp{}_input'.format(i+2)])
    
    return list_temps


    
def initiate_fah(cpu_usage):
    
    #Begin a FAH process
    #The `None` arguments are important because they let the process run without python waiting for the results
    #The full command I use here is:
        #` FAHClient --client-type='bigadv' --cpu_usage={cpu_usage} --power='FULL' `
    
    process = subprocess.Popen(['FAHClient', "--client-type='bigadv'", "--power='FULL'", "--cpu-usage={}".format(cpu_usage)], stdin=None, stdout=None, stderr=None)
    
    return



#Writing this function made me eligible for a job at FAANG, but I turned them down:
def mean(ls):
    return sum(ls)/len(ls)



#Initial FAH client run
usage = 90
initiate_fah(usage)



while True:
    
    #Check if temp is >= your maximum preferred operating temperature
    if mean(get_temps()) >= 88:
        
        print("Average temperature >= 88 degrees celsius. Repeating measurement to avoid false positives.")
        
        #Repeat the measurement to avoid restarting FAH because of a random spike
        #You could repeat more than once if you see too many false positives
        time.sleep(5)
        if mean(get_temps()) >= 88:
            
            #Reduce usage, but reduce it by less and less every time. Just what works well for me.
            usage -= usage/35
            usage = int(usage)
            print("After repeat measurement, average temperature was >= 88 degrees celsius.\nRestarting FAHClient with a new cpu-usage value of {}.".format(usage))
            
            #Kill the FAH processes
            stream = os.popen("killall FAHClient")
            
            #Sleep to give cpu time to cool & ensure FAH client wraps up properly
            time.sleep(20)
            
            print("Restarting.")
            
            #Restart
            initiate_fah(cpu_usage=usage)
    
