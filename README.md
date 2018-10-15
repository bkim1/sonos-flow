# Sonos Flo

Sonos Flo is a project created for the Sonos Challenge: Boston hackathon.

---

Authors: Branden Kim, Brian Hempe, Caroline Downey, Fin Elliot, Victoria Napolitano

---


## Setting up the project

1. Clone the repository using the command `git clone https://github.com/bkim1/sonos-flo.git`
2. Navigate into the newly created directory
3. Setup the virtualenv by running `python3 -m venv venv`
    * We are using Python3's native venv tool
4. Run `. venv/bin/activate`
5. Install all dependencies using `pip install -r requirements.txt`
6. Congrats! The project is now ready to be run


## Running the project

### For First Time Only

1. Run `export FLASK_APP=flo` and `export FLASK_ENV=development`

### Otherwise

1. Run `flask run`
2. The server will start and be up on port 5000