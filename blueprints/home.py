from flask import Blueprint, redirect, url_for, request, render_template, session

bp = Blueprint("home",__name__,url_prefix="/")

@bp.route("/")
def home():
    return "I am home"

@bp.route('/dashboard')
def dashboard():
   return render_template('dashboard.html',session=session) #render template automatically looks for dir named templates and loads respective files from it