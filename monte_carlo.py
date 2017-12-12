import numpy as np
from jpype import *
import orhelper
from random import gauss
import math
import os
import json

MASTER_STATS = ['Altitude','Time','Vertical velocity','Vertical acceleration','Lateral distance','Lateral direction','Lateral velocity','Lateral acceleration','Roll rate','Pitch rate','Yaw rate','Thrust']

MASTER_VARS = [{'name':'Rod angle','units':'degrees','defaults':[0,5]}, {'name':'Rod direction','units':'degrees','defaults':[0,5]}, {'name':'Wind speed','units':'m/s','defaults':[15,5]}]

def get_prop(gauss,name):
    next((i for i in gauss if i['name'] == name), None)

def run_sims(settings):
    log_file = "logs/" + settings['id'] + ".cass"
    with open(log_file,'w') as sim_file:
        sim_file.write('MIT Rocket Team Cassandra v0.1 Analysis' + os.linesep)
        sim_file.write('Date: ' + str(datetime.date.today()) + os.linesep)
        sim_file.write('Params: ' + json.dumps(settings) + os.linesep + os.linesep)

    with orhelper.OpenRocketInstance('/root/OpenRocket.jar', log_level='DEBUG'):
        # Load the document and get simulation
        orh = orhelper.Helper()
        doc = orh.load_doc('/root/mcda/rockets/'+settings['filename'])
        sim = doc.getSimulation(0)

        opts = sim.getOptions()
        rocket = opts.getRocket()

        sims = []

        for p in range(settings['iters']):
            print('Running simulation ', p)
            i = get_prop(settings.gauss,'Rod angle')
            opts.setLaunchRodAngle(math.radians(gauss(i['mu'], i['sigma'])))

            i = get_prop(settings.gauss,'Rod direction')
            opts.setLaunchRodDirection(math.radians(gauss(i['mu'], i['sigma'])))

            i = get_prop(settings.gauss,'Wind speed')
            opts.setWindSpeedAverage(gauss(i['mu'], i['sigma']))

            """
            for component_name in ('Nose cone', 'Body tube'):       # 5% in the mass of various components
                component = orh.get_component_named( rocket, component_name )
                mass = component.getMass()
                component.setMassOverridden(True)
                component.setOverrideMass( mass * gauss(1.0, 0.05) )
            """

            orh.run_simulation(sim)
            data = orh.get_timeseries(sim, settings['params'])
            events = orh.get_events(sim)

            for key in data:
                data[key] = data[key].tolist()

            sims.append({'data':data,'events':events})
            with open(log_file,'a') as sim_file:
                json.dump(sims[-1], sim_file)
                sim_file.write(os.linesep)

        return sims
