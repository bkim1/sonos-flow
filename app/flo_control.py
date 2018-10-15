from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('flo_control', __name__)

