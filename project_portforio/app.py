"""
実行環境設定
ターミナル上で
  export FLASK_APP=app
  export FLASK_ENV=development
  flask run
の三つを実行してください。
その後、ユーザー登録を行なってログインしてください
"""


from flask import Flask
from flask import render_template,request,redirect
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


###書籍登録用のテーブル###
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(80),  nullable=False)
    created_at = db.Column(db.DateTime,nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
######

###ログイン用のテーブル###
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12),  nullable=False)
######

###コメントテーブル###
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(140), nullable=False)
######

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

####################トップ画面#######################
@app.route('/')
def top():
    return render_template('top.html')



###################################################


################## ユーザー登録 #####################
@app.route('/signup',methods=['GET','POST'])
def singup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User(username=username,password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')
####################################################


################　ログイン　ログアウト　################
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password,password):
            login_user(user)
            return redirect('/main')

    else:
        return render_template('login.html')


@app.route('/login')
@login_required
def logout():
    logout_user()
    return redirect('/login')
####################################################


###################　メインページ　####################
@app.route('/main',methods=['GET','POST'])
@login_required
def main():
    if request.method == 'GET':
        posts = Post.query.all()
        comment = Comment.query.all()
        return render_template('main.html',posts=posts,comment=comment)

#########################天気##########################
@app.route('/weather')
@login_required
def weather():
    import requests
    from  dotenv import load_dotenv
    load_dotenv('.env')
        
    cities = ['Tokyo','Osaka','Nagoya','Naha','Sapporo',]
    jsondatas  = []
    for city in cities:
        APIkey=os.environ.get('APIKEY')
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIkey}&lang=ja&units=metric'
        jsondata = requests.get(url).json()
        jsondatas.append(jsondata)
    
    return render_template('weather.html',jsondatas=jsondatas)
#######################################################
#######################################################


##############　新規登録　編集　削除　#####################
@app.route('/create',methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        
        post = Post(title=title,body=body)

        db.session.add(post)
        db.session.commit()
        return redirect('/main')
    
    else:
        return render_template('create.html')


@app.route('/<int:id>/update',methods=['GET','POST'])
@login_required
def update(id):
    post = Post.query.get(id)

    if request.method == 'GET':
        return render_template('update.html',post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        
    
        db.session.commit()
        return redirect('/main')


@app.route('/<int:id>/delete',methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/main')
#####################################################


#####################################################
@app.route('/<int:id>/comment',methods=['GET','POST'])
@login_required
def comment(id):
    post = Post.query.get(id)
    

    if request.method == 'GET':
        return render_template('comment.html',post=post)

    else:
        comment = request.form.get('comment')

        comment = Comment(comment=comment)

        db.session.add(comment)
        db.session.commit()
        return redirect('/main')
########################################################