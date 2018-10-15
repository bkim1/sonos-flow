# Sonos Flo

Sonos Flo is a project created for the Sonos Challenge: Boston hackathon.

---

Authors: Branden Kim, Brian Hempe, Caroline Downey, Fin Elliot, Victoria Napolitano

Codebase: Python 3.7

---


## Setting up the project

1. Clone the repository using the command `git clone https://github.com/bkim1/sonos-flo.git`
2. Navigate into the newly created directory
3. Setup the virtualenv by running `python3 -m venv venv`
    * We are using Python3's native venv tool
4. Run `. venv/bin/activate`
5. Install all dependencies using `pip install -r requirements.txt`
6. Congrats! The project is now ready to be run


## Running the project as a developer

### For First Time Only

1. Run `export FLASK_APP=app` and `export FLASK_ENV=development`

### Otherwise

1. Run `flask run`
2. The server will start and be up on port 5000


## Running the project for production
1. Run `gunicorn -b :5000 --access-logfile - --error-logfile - flo:app`

## To deploy the server using Zeit Now
1. Run `./deploy.sh`

Note: This project is deploying a docker image, so if you want to deploy the project, you must have Docker installed.