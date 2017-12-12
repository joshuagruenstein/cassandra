import numpy as np
from jpype import *
import orhelper
import random
import math
import os
import json
import datetime

import matplotlib, StringIO, urllib, base64
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DEFAULT_STATS = ['Lateral distance', 'Lateral direction', 'Time']

MASTER_STATS = ['Altitude','Vertical velocity','Vertical acceleration','Lateral velocity','Lateral acceleration','Roll rate','Pitch rate','Yaw rate','Thrust']

MASTER_VARS = [
    {'name':'Rod angle','units':'degrees','defaults':[0,5]},
    {'name':'Rod direction','units':'degrees','defaults':[0,5]},
    {'name':'Wind speed','units':'m/s','defaults':[15,5]},
    {'name':'Launch temperature','units':'celcius','defaults':[15,2]},
    {'name':'Launch pressure','units':'pascal','defaults':[101325,100]},
    {'name':'Rod length','units':'m','defaults':[1,0.05]}
]

def get_prop(gauss,name):
    i = next((i for i in gauss if str(i['name'].split('(')[0].strip()) == str(name)), None)
    return random.gauss(i['mu'], i['sigma'])

def get_points(id,old_points):
    i = -4
    points = []
    with open("logs/" + id + ".cass",'r') as f:
        for x in f:
            if i > len(old_points):
                sim = json.loads(x)

                if 'data' in sim:
                    lastDist = sim['data']['Lateral distance'][-1]
                    lastDir = sim['data']['Lateral direction'][-1]

                    old_points.append((lastDist*math.cos(lastDir), lastDist*math.sin(lastDir)))
            i += 1
def plot_points(points):

    ax = plt.figure().add_subplot(1, 1, 1)
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('center')
    ax.grid(True)

    if len(points) > 0:
        plt.scatter(*zip(*points))

    imgdata = StringIO.StringIO()
    plt.gcf().savefig(imgdata, format='png', bbox_inches='tight')
    imgdata.seek(0)

    uri = 'data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf))

    plt.close('all')

    return uri

def run_sims(settings):
    log_file = "logs/" + settings['id'] + ".cass"
    with open(log_file,'w') as sim_file:
        sim_file.write('MIT Rocket Team Cassandra v0.1 Analysis' + os.linesep)
        sim_file.write('Date: ' + str(datetime.date.today()) + os.linesep)
        sim_file.write('Params: ' + json.dumps(settings) + os.linesep + os.linesep)

    with orhelper.OpenRocketInstance('/root/mcda/req/OpenRocket.jar', log_level='ERROR'):
        # Load the document and get simulation
        orh = orhelper.Helper()
        doc = orh.load_doc('/root/mcda/rockets/'+settings['filename'])
        sim = doc.getSimulation(0)

        opts = sim.getOptions()
        rocket = opts.getRocket()

        sims = []

        for p in range(settings['iters']+1):
            print('Running simulation ', p)

            opts.setLaunchRodAngle(math.radians(get_prop(settings['gauss'],'Rod angle')))
            opts.setLaunchRodDirection(math.radians(get_prop(settings['gauss'],'Rod direction')))

            opts.setWindSpeedAverage(get_prop(settings['gauss'],'Wind speed'))
            opts.setLaunchTemperature(273.15+get_prop(settings['gauss'],'Launch temperature'))
            opts.setLaunchPressure(get_prop(settings['gauss'],'Launch pressure'))
            opts.setLaunchRodLength(get_prop(settings['gauss'],'Rod length'))

            """
            for component_name in ('Nose cone', 'Body tube'):       # 5% in the mass of various components
                component = orh.get_component_named( rocket, component_name )
                mass = component.getMass()
                component.setMassOverridden(True)
                component.setOverrideMass( mass * gauss(1.0, 0.05) )
            """

            orh.run_simulation(sim)
            data = orh.get_timeseries(sim,DEFAULT_STATS+settings['params'])
            events = orh.get_events(sim)

            for key in data:
                data[key] = data[key].tolist()

            sims.append({'data':data,'events':events})
            with open(log_file,'a') as sim_file:
                json.dump(sims[-1], sim_file)
                sim_file.write(os.linesep)

        return sims

if __name__ == '__main__':
    print(plot_points(get_points('pB85W2mtmIKR20ibY2GQ')))
