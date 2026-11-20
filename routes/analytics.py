from flask import Blueprint, redirect, url_for

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


@analytics_bp.route("/")
def home():
    return redirect(url_for("subject.subjects"))
