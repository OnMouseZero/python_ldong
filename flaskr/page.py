#coding=utf-8
from flask import (
                    Blueprint, flash, g, redirect, render_template, request, url_for
                                )
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db
import math

page = Blueprint('page', __name__)


