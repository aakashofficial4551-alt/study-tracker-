from flask import Blueprint, render_template
from flask_login import login_required

calendar_bp = Blueprint(
    "calendar",
    __name__,
    url_prefix="/calendar"
)


@calendar_bp.route("/")
@login_required
def home():
    return render_template("calendar/index.html")