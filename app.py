from flask import Flask, render_template
import monte_carlo

app = Flask(__name__, template_folder='.')

running = False
thread = None

@app.route("/")
def main():
    if running:
        return render_template('running.html')
    else:
        return render_template('start.html')

@app.route("/status")
def sim_status():
    return "Status"

@app.route("/kill")
def kill_sim():
    #kill
    return download_sim()

@app.route("/download")
def download_sim():
    return "download"

@app.route("/start")
def upload_ork():
    return "started"
