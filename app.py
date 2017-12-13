from flask import Flask, Response, request, render_template, current_app, send_from_directory
from werkzeug.utils import secure_filename
from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
import string, json, random, os
import monte_carlo

class MyFlask(Flask):
    def get_send_file_max_age(self, name):
        if name.lower().endswith('.cass'):
            return 0
        return Flask.get_send_file_max_age(self, name)

app = MyFlask(__name__)
cron = BackgroundScheduler()

PASSWORD = "a"

running = None
thread = None
wasAt = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'ork'

def new_id():
    return ''.join([random.choice(string.ascii_letters + string.digits + string.digits) for _ in range(20)])

def jog_thread():
    global thread
    global wasAt

    wasAt = None

    if running:
        if thread:
            thread.terminate()
    
        thread = Process(target=monte_carlo.run_sims, args=(running,))
        thread.start()

def jog_poller():
    global wasAt
    
    if running:
        monte_carlo.get_points(running['id'],running['points'])
        num_points = len(running['points'])

        if num_points != running['iters'] and wasAt == num_points:
            jog_thread()
        else:
            wasAt = num_points

cron.add_job(jog_poller, trigger='interval', seconds=30)
cron.start()

@app.route("/")
def main():
    if running:
        monte_carlo.get_points(running['id'],running['points'])
        img = monte_carlo.plot_points(running['points'])
        return render_template('running.html',sim=running,rep={'iters':len(running['points']),'img':img})
    else:
        return render_template('start.html',vars=monte_carlo.MASTER_VARS, params=monte_carlo.MASTER_STATS)

@app.route("/abort",methods=['POST'])
def kill_sim():
    global running
    global thread
    global wasAt

    wasAt = None

    if request.form.get('password') != PASSWORD:
        return "Wrong password", 401

    if thread:
        thread.terminate()
    thread = None
    running = None

    return "success", 200

@app.route("/restart",methods=['POST'])
def restart():
    global running

    if request.form.get('password') != PASSWORD:
        return "Wrong password", 401

    running['id'] = new_id()
    running['points'] = []
    
    jog_thread()
    
    return "success", 200

@app.route("/addpoints",methods=['POST'])
def addpoints():
    global running

    #if request.form.get('password') != PASSWORD:
    #    return "Wrong password", 401
    try:
        points = int(request.form.get('points'))
    except Exception:
        return "Noninteger points summand", 400

    running['iters'] += points

    jog_thread()

    return "success", 200

@app.route("/status")
def status():
    if running:
        monte_carlo.get_points(running['id'],running['points'])
        img = monte_carlo.plot_points(running['points'])

        return json.dumps({'points':len(running['points']),'img':img})
    else:
        return "No simulation running", 400

@app.route("/download")
def download_sim():
    logs = os.path.join(current_app.root_path, 'logs')
    return send_from_directory(directory=logs, filename=running['id']+".cass")

@app.route("/highlights")
def download_highlights():
    if running:
        monte_carlo.get_points(running['id'],running['points'])
        csv = monte_carlo.highlight_csv(running['points'])

        return Response(csv,mimetype="text/csv",headers={"Content-disposition":"attachment; filename=highlights.csv","Cache-Control":"no-cache, no-store, must-revalidate"})
    else:
        return "No simulation running", 400

@app.route("/start",methods=['POST'])
def start():
    global running
    global thread

    gauss = json.loads(request.form.get('gauss'))
    params = json.loads(request.form.get('params'))
    iters = int(request.form.get('iters'))
    password = request.form.get('password')

    if password != PASSWORD:
        return "Wrong password", 401

    ork = request.files['ork']
    if not ork or not allowed_file(ork.filename) or ork.filename == '':
        return "File upload error", 500

    filename = secure_filename(ork.filename)
    ork.save(os.path.join('rockets', filename))

    sim_id = new_id()

    running = {'gauss':gauss,'params':params,'iters':iters, 'filename':filename, 'id': sim_id}

    thread = Process(target=monte_carlo.run_sims, args=(running,))
    thread.start()

    running['points'] = []

    return "success", 200

