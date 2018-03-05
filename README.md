
# Cassandra
 [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/hyperium/hyper/master/LICENSE) [![Docker Build Status](https://img.shields.io/docker/build/nanogru/cassandra.svg)](https://hub.docker.com/r/nanogru/cassandra)

Monte-carlo dispersion analysis in the browser, powered by [OpenRocket](https://github.com/openrocket/openrocket).  Created by and for MIT Rocket Team.

## Usage

1) Download the [custom Cassandra build of OpenRocket](https://github.com/joshuagruenstein/cassandra/raw/master/req/OpenRocket.jar).
2) Create a rocket file, or open one from another version of OpenRocket.  Most .ork files should work, but if not create a new one.
3) Run at least one simulation using the motor you want Cassandra to simulate on, and make sure it succeeds.
4) Save the `.ork` file somewhere accessible.
5) Navigate to Cassandra in the browser. Enter all the required Gaussian variables and the number of points you want to plot, select the `.ork` file, and mark any additional variables you want Cassandra to keep track of.
6) Enter the master password, and click `Run Simulation`.

This should bring you to a new page, with a blank grid on the right.  Give Cassandra a couple seconds to start plotting points.  Once you've got a few, you can download a CSV report and open it in Excel, or a full report to analyse using a tool like Python.

## Installation

Rather than running on bare metal, Cassandra instead runs on [Docker](https://www.docker.com/).  This is because Cassandra relies on strange hackiness for its integration with OpenRocket, and thus benefits from the control Docker provides.  This also makes running Cassandra very easy.

1) [Install Docker CE](https://www.docker.com/community-edition#/download), and start it.
2) In your command line of choice, run the following command: `docker run -e PASSWORD=mypassword -p 4000:80 nanogru/cassandra`, where `mypassword` is the password you want and `4000` is the port you want to run Cassandra on.
3) Wait a bit for everything to download (probably a fair while).
4) Navigate to `http://localhost:4000/` in your web browser (if you chose another port number, replace it here too).

If you have any issues with the installation process, post an issue in this repo. If you'd like to deploy Cassandra to a cloud VM, I recommend using Google Compute Engine, as it lets you easily deploy a Docker container on one of their VMs.

## Development

If you want to modify/develop on Cassandra rather than just pulling the latest version, you can build the container froms scratch using the following steps.

1) [Install Docker CE](https://www.docker.com/community-edition#/download), and start it.
2) Clone the repo, and navigate to it in the command line.
3) Make whatever edits you want to make.
4) Build the container using `docker build -t mcda .`.
5) Run your custom Cassandra with `docker run -e PASSWORD=mypassword -p 4000:80 mcda`.

Cassandra is written in Python 2.7, and works by communicating with OpenRocket using [JPype](https://github.com/originell/jpype).  The webapp functionality is written in Flask and primarily contained in `app.py`.  Simulation related functionality lives in `monte_carlo.py`, OpenRocket integration in `orhelper.py`, and HTML templates in `templates/`.

Every time a simulation is requested, Cassandra starts a simulation in a new thread, which incrementally outputs the results of each simulation in JSON to a `.cass` file.  To generate the highlights CSV and dispersion plot, Cassandra incrementally reads this `.cass` file and extracts relevant information.  After the simulation is aborted or restarted, the `.cass` file is deleted, and all record of the simulation lost.

### License

Cassandra is open source software.  The Python and OpenRocket integration is distributed under the [GPL v3](https://www.gnu.org/licenses/gpl-3.0) license, while the frontend is distributed under the [MIT](https://opensource.org/licenses/MIT) license.
