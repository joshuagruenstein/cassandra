import numpy as np
from jpype import *
import orhelper
from random import gauss
import math
import os
import json

def run_sims(rocket_file,properties,num,filename,an_id):
    with open(filename,'w') as sim_file:
        sim_file.write('MIT Rocket Team OpenRocket MCDA v0.1 Analysis' + os.linesep)
        sim_file.write('Date: ' + str(datetime.date.today()) + os.linesep)
        sim_file.write('Analysis ID: ' + str(an_id) + os.linesep + os.linesep)

    with orhelper.OpenRocketInstance('/root/OpenRocket.jar', log_level='DEBUG'):

        # Load the document and get simulation
        orh = orhelper.Helper()
        doc = orh.load_doc(rocket_file)
        sim = doc.getSimulation(0)

        opts = sim.getOptions()
        rocket = opts.getRocket()

        sims = []

        for p in range(num):
            print 'Running simulation ', p

            opts.setLaunchRodAngle(math.radians( gauss(45, 5) ))    # 45 +- 5 deg in direction
            opts.setLaunchRodDirection(math.radians( gauss(0, 5) )) # 0 +- 5 deg in direction
            opts.setWindSpeedAverage( gauss(15, 5) )                # 15 +- 5 m/s in wind
            for component_name in ('Nose cone', 'Body tube'):       # 5% in the mass of various components
                component = orh.get_component_named( rocket, component_name )
                mass = component.getMass()
                component.setMassOverridden(True)
                component.setOverrideMass( mass * gauss(1.0, 0.05) )

            orh.run_simulation(sim)
            data = orh.get_timeseries(sim, properties)
            events = orh.get_events(sim)
            
            for key in data:
                data[key] = data[key].tolist()

            sims.append({'data':data,'events':events})
            with open(filename,'a') as sim_file:
                json.dump(sims[-1], sim_file)
                sim_file.write(os.linesep)

        return sims

if __name__ == '__main__':
    props = ['Altitude','Time','Vertical velocity','Vertical acceleration','Lateral distance','Lateral direction','Lateral velocity','Lateral acceleration','Roll rate','Pitch rate','Yaw rate','Thrust']
    run_sims('/root/rockets/testrocket.ork', props, 20, 'results.txt','Test1')
