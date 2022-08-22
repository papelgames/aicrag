
import logging

from flask import abort, render_template, redirect, url_for, request, current_app
from flask_login import current_user

#from app.models import Post, Comment
from . import public_bp
from .forms import CommentForm

logger = logging.getLogger(__name__)


@public_bp.route("/")
def index():
   
    return render_template("public/index.html")
