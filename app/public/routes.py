
import logging

from flask import render_template, redirect, url_for
from flask_login import login_required
from app.auth.decorators import  not_initial_status


#from app.models import Post, Comment
from . import public_bp
from .forms import CommentForm

logger = logging.getLogger(__name__)


@public_bp.route("/")
@login_required
@not_initial_status
def index():
    return redirect(url_for("consultas.consulta_productos"))
    #return render_template("public/index.html")
