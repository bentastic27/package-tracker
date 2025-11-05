from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SelectMultipleField, SubmitField
from flask_bootstrap import Bootstrap5
import datetime
import valkey
import os


app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'darkly'
app.config['SECRET_KEY'] = os.urandom(32)

valid_providers = ['usps', 'ups', 'fedex']


class AddTrackingForm(FlaskForm):
  provider = SelectMultipleField(label="Provider", choices=valid_providers, validators=[validators.DataRequired()])
  tracking_id = StringField(label="Tracking ID", validators=[validators.DataRequired()])
  description = StringField(label="Description", validators=[validators.DataRequired()])
  submit = SubmitField(label="Add Tracking")


def valkey_get_connection(host: str, port: int):
  return valkey.Valkey(host=host, port=port, db=0, decode_responses=True)


def valkey_add_tracking(tracking_id: str, provider: str, description: str):
  r = valkey_get_connection(host='127.0.0.1', port=6379)
  r.hset(name=tracking_id, mapping={'provider': provider, 'description': description, 'last_checked': str(datetime.datetime.now())})
  r.quit()


def valkey_delete_tracking(tracking_id: str):
  r = valkey_get_connection(host='127.0.0.1', port=6379)
  r.delete('tracking_id')
  r.quit()


def valkey_get_all_trackings():
  r = valkey_get_connection(host='127.0.0.1', port=6379)
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

@app.route('/delete/<trackingid>')
def delete(trackingid=None):
  valkey_delete_tracking(tracking_id=trackingid)
  return redirect('/', 302)
