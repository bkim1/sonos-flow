from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('flo_control', __name__)

#add routes for Oauth
#logic for communicating with RBpi
#write for raspberry pi communicating to the server. Needs to call the webserver when, and only when,
#it's INRANGE. Make another call when the RBPI is OUTOFRANGE
#'hard-code' for when we're INRANGE of RBPI1, start play 'MR BRIGHT..', when OUTOFRANGE, stop
#RBPI is ONLY going to be communicating to the webserver. RBPI acting as a SWITCH to send out signal
#when it is INRANGE of client device. When it sends out signal, it does NOT know if the other RBPI
#No logic connecting one raspberry pi to another
#assumption based off the fact that we are having the RBPIs placed far enough away from each other