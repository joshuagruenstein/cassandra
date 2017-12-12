from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from multiprocessing import Process
import string, json, random, os
import monte_carlo

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'rockets'

PASSWORD = "a"

running = None
thread = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'ork'

@app.route("/")
def main():
    if running:
        return render_template('running.html',sim=running,rep={'iters':3,'img':'a'})
    else:
        return render_template('start.html',vars=monte_carlo.MASTER_VARS, params=monte_carlo.MASTER_STATS)

@app.route("/abort")
def kill_sim():
    global running
    global thread

    thread.terminate()
    thread = None
    running = None

    return "success", 200

@app.route("/download")
def download_sim():
    return "download"

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
    ork.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    sim_id = ''.join([random.choice(string.ascii_letters + string.digits + string.digits) for _ in range(20)])

    running = {'gauss':gauss,'params':params,'iters':iters, 'filename':filename, 'id': sim_id}

    thread = Process(target=monte_carlo.run_sims, args=(running,))
    #thread.start()

    return "success", 200
