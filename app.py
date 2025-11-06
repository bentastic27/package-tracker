from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, SelectField
from flask_bootstrap import Bootstrap5
import datetime
import valkey
import os
# import requests


app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'darkly'
app.config['SECRET_KEY'] = os.urandom(32)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

valid_providers = ['usps', 'ups', 'fedex']

valkey_host = os.environ.get("VALKEY_HOST", "127.0.0.1")
valkey_port = int(os.environ.get("VALKEY_PORT", "6379"))


class AddTrackingForm(FlaskForm):
  provider = SelectField(label="Provider", choices=valid_providers, validators=[validators.DataRequired()])
  tracking_id = StringField(label="Tracking ID", validators=[validators.DataRequired()])
  description = StringField(label="Description", validators=[validators.DataRequired()])
  submit = SubmitField(label="Add Tracking")

## TODO: get this rippin once I get the usps api
# def usps_get_token():
#   return requests.post(
#     url="https://apis.usps.com/oauth2/v3/token",
#     data={
#       "client_id": os.environ.get("USPS_KEY"),
#       "client_secret": os.environ.get("USPS_SECRET"),
#       "grant_type": "client_credentials",
#       "scope": "tracking"
#     }
#   ).json()['access_token']


# def usps_get_tracking(tracking_id, token):
#   return requests.post(
#     url="https://apis.usps.com/tracking/v3r2/tracking",
#     headers={
#       "accept": "application/json",
#       "authorization": "Bearer " + token
#     },
#     data={
#       "trackingNumber": tracking_id
#     }
#   ).json()


def valkey_get_connection(host: str, port: int):
  return valkey.Valkey(host=host, port=port, db=0, decode_responses=True)


def valkey_add_tracking(tracking_id: str, provider: str, description: str):
  r = valkey_get_connection(host=valkey_host, port=valkey_port)
  r.hset(name=tracking_id, mapping={'provider': provider, 'description': description, 'last_checked': str(datetime.datetime.now)})
  r.quit()


def valkey_delete_tracking(tracking_id: str):
  r = valkey_get_connection(host=valkey_host, port=valkey_port)
  r.delete(tracking_id)
  r.quit()


def valkey_get_all_trackings():
  r = valkey_get_connection(host=valkey_host, port=valkey_port)
  trackings = []
  for key in r.keys():
    t = r.hgetall(key)
    t['id'] = key
    trackings.append(t)
  r.quit()
  return trackings


@app.route("/")
def index():
  return render_template('index.html', trackings=valkey_get_all_trackings())

@app.route('/add', methods=['GET', 'POST'])
def add():
  form = AddTrackingForm(request.form)
  if request.method == 'POST' and form.validate():
    tracking_id = request.form['tracking_id']
    provider = request.form['provider']
    description = request.form['description']

    valkey_add_tracking(tracking_id, provider, description)

    flash('Tracking Added')
    return redirect('/', 302)
    
  return render_template('add.html', form=form)

@app.route('/delete/<tracking_id>')
def delete(tracking_id=None):
  valkey_delete_tracking(tracking_id=tracking_id)
  return redirect('/', 302)
