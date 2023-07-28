import flask
from flask import Flask, render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from UserLogin import UserLogin, downloadkeys, getallblacklist,getallkeys,setkehwid,startsub,deletekey,addbanhwid
from flask_restful import Api, Resource
import time
import datetime
import asyncio
from tortoise import Tortoise
from models import User, Key, BlackList
from forms import LoginForm, RegisterForm
import os
import secrets
from flask import g
from pathlib import Path


app = Flask(__name__)
api = Api()
app.config['UPLOAD_FOLDER'] = 'keys'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'db.sqlite3')))
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # перенаправление если не авторизован

DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

def time_sub_days(get_time):
    time_now = int(time.time())
    middle_time = int(get_time) - time_now
    if middle_time <= 0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_time))
        return dt


def days_to_seconds(days):
    return days * 24 * 60 * 60

class MyApi(Resource):
    def get(self, inkey, hwid):
        if inkey == "" or inkey == 0:
            return {"status": "error_key"}
        else:
            blacklist = getallblacklist()
            if hwid in blacklist:
                return {"status": "banned"}
            allkeys = getallkeys()
            for key in allkeys:
                if str(inkey) == str(key['key']):
                    if str(key['hwid']) == "0" or str(key['hwid']) == "" or str(key['hwid']) is None:
                        print(str(key['key']))
                        timesub = key['key_life']
                        time_sub = int(time.time()) + days_to_seconds(timesub)
                        setkehwid(hwid, str(key['id']))
                        startsub(time_sub,str(key['id']))
                        return {"status": "success"}
                    elif str(key['hwid']) == str(hwid):
                        if int(key['end_work']) > int(time.time()):
                            return {"status": "subscribe"}
                        else:
                            deletekey(key['id'])
                            print('delete')
                            return {"status": "subscribe_is_end"}
                    else: 
                        return {"status": "error_key"}
                
      
                       
class banitze(Resource):
     def get(self, hwid):
        if hwid == "" or hwid == 0:
            return {"status": "error_key"}
        else:
            blacklist = getallblacklist()
            if hwid in blacklist:
                return {"status": "already_banned"}
            else:
                addbanhwid(hwid)
                return {"status": "success"}
            
            
api.add_resource(MyApi, "/api/main/<string:inkey>/<string:hwid>")
api.add_resource(banitze, "/api/blacklist/<string:hwid>")
api.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    a = UserLogin().fromDB(user_id)
    print(f"a: {a}")
    return a

@login_required
@app.route('/keypanel')
async def index():
    user = current_user.get_user()
    keylist = await Key.allkeys(user)
    countkeys = await Key.activekeys(user)
    return render_template('index.html', keylist=keylist, allcount=len(keylist), activekeys=countkeys, user=user)

async def add_key_func(game, days, count, user):
    now = datetime.datetime.now()
    tt = now.strftime("%d-%m-%Y%H-%M")
    file_name = tt+".txt"
    with open(f"keys/{file_name}", 'a') as f_in:
        for num in range(count):
            key = secrets.token_hex(nbytes=18)
            f_in.write(key+"\n")
            await Key.get_or_create(key=key, game=game, key_life=days,end_work=0,hwid='',is_active=0,owner=str(user['username']))
    f_in.close()
    return file_name

@app.route('/addkey', methods=["POST", "GET"])
@login_required
async def addkey():
    user = current_user.get_user()
    if request.method == "POST":
        if len(request.form['gamelist']) != 0 and len(request.form['count']) != 0 and len(request.form['days']) > 0:
            lol = await add_key_func(str(request.form['gamelist']), int(request.form['days']), int(request.form['count']),user)
            print(f"lol: {lol}")
            return flask.send_from_directory("keys", lol, as_attachment=True)
    return render_template("addkey.html", user=user)


@app.route('/resethwid', methods=["POST", "GET"])
@login_required
async def resethwid():
    if request.method == "POST":
        if len(request.form['keykey'])!= 0:
            key = await Key.get_or_none(key=request.form['keykey'])
            if key.can_reset == 1:
                key.can_reset = 0
                await key.save()
                flash("Successful reset", 'success')
            else:
                flash("you can only 1 reset", 'error')
    return render_template("hwidreset.html")

@app.route('/')
@login_required
async def indexmain():
    return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
async def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = await User.get_or_none(username=form.username.data)
        if user and user.password == form.password.data:
            userlogin = UserLogin().create(user)
            id = userlogin.get_id()
            print(f"id: {id}")
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for('index'))
        flash("error login or password", 'error')
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You exit from account", "success")
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
async def register():
    ...

async def on_startup():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()
    print('DB CONNECT')
    app.run(host='127.0.0.1', port=8000, debug=True) #from waitress import serve #serve(app, host="45.130.43.135", port=1337)

async def on_shutdown():
    await Tortoise.close_connections()
    print('CLOSED')

if __name__ == '__main__':
    app.secret_key = 'pa1nz0redpapa1337'
    try:
        asyncio.run(on_startup())
    except KeyboardInterrupt:
        asyncio.run(on_shutdown())
        raise SystemExit(0)
