from src.User import User
from src.Session import Session
from src.Group import Group
from flask import Blueprint, redirect, url_for, request, render_template, session

bp = Blueprint("api_dialogs",__name__,url_prefix="/api/dialogs")

@bp.route("/api_keys")
def api_keys():
    groups = Group.get_groups()
    return render_template("/dialogs/api_keys.html", session=session, groups=groups)