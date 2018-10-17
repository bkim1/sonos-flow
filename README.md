# Sonos Flow

Sonos Flow is a project created for the Sonos Challenge: Boston hackathon. It allows the user to have sound follow them throughout their home.

Sonos Flow is compatible with Sonos.

This repository holds one component of Sonos Flow. It is a Flask web server that interacts with the Sonos API to control the speakers within a household.

---

Authors: Branden Kim, Brian Hempe, Caroline Downey, Fin Elliot, Victoria Napolitano

Sonos Flow runs on Python 3.7 and Flask 1.0.2. It is being deployed using ZEIT's Now service with a Docker container. The deployed version runs on a gunicorn server.

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


# API Documentation

Below is a description of the available endpoints

Base URL: `https://sonos-flow.now.sh`

---

## **Authentication**

### **Login & Authorize Sonos Flow**
#### `GET`: `/auth/login`

Redirects the browser to Sonos's login page to authorize Sonos Flow to access the household. 

--- 

## **Flow Control**

To use any of these endpoints, you MUST authenticate first. Then, setup Flow for the household by accessing the `/flow` endpoint.

### **Setup Flow for Household**
#### `GET`: `/flow`

Sets up the server to handle the household. Have to authorize Sonos Flow prior to calling this endpoint.

Sets up:
* Household
* Groups within household
* Favorites for household


### **Enter Flow**
#### `GET`: `/flow/enter/<string:group>`
#### `GET`: `/flow/enter/<string:group>/<string:favorite>`

Starts playing content for the specified group. The group and favorite parameter should be the name of the group or favorite within the household. 


### **Exit Flow**
#### `GET`: `/flow/exit/<string:group>`

Stops playing content for the specified group. The group parameter should be the name of the group within the household.