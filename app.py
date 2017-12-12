import flask
from flask import Flask, request, render_template, current_app, send_from_directory
from werkzeug.utils import secure_filename
from multiprocessing import Process
import string, json, random, os
import monte_carlo

class MyFlask(flask.Flask):
    def get_send_file_max_age(self, name):
        if name.lower().endswith('.cass'):
            return 0
        return flask.Flask.get_send_file_max_age(self, name)

app = MyFlask(__name__)

PASSWORD = "a"

running = None
thread = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'ork'

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

    if request.form.get('password') != PASSWORD:
        return "Wrong password", 401

    if thread:
        thread.terminate()
    thread = None
    running = None

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

    sim_id = ''.join([random.choice(string.ascii_letters + string.digits + string.digits) for _ in range(20)])

    running = {'gauss':gauss,'params':params,'iters':iters, 'filename':filename, 'id': sim_id}

    thread = Process(target=monte_carlo.run_sims, args=(running,))
    thread.start()

    running['points'] = []

    return "success", 200
