from flask import Flask, render_template, request, jsonify

from pymongo import MongoClient

client = MongoClient('###########################')
db = client.timeAttack

#Flask 객체 인스턴스 생성
app = Flask(__name__)

SECRET_KEY = 'salt'

import jwt
import datetime
import hashlib

@app.route('/') # 접속하는 url
def index():
  token_receive = request.cookies.get('mytoken')
  try:
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    return render_template('index.html', email=user_info["id"])
  except jwt.ExpiredSignatureError:
    return render_template('signup.html')
  except jwt.exceptions.DecodeError:
    return render_template('signup.html')

@app.route('/signup')
def go_signup():
  return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup():
  id_receive = request.form['email_give']
  pw_receive = request.form['pw_give']
  pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

  db.user.insert_one({'id': id_receive, 'pw': pw_hash})

  return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def login():
  id_receive = request.form['email_give']
  pw_receive = request.form['pw_give']

  pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

  result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

  # 찾으면 JWT 토큰을 만들어 발급합니다.
  if result is not None:
    # JWT 토큰에는, payload와 시크릿키가 필요합니다.
    # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
    # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
    # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
    payload = {
      'id': id_receive,
      'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    # token을 줍니다.
    return jsonify({'result': 'success', 'token': token})
  # 찾지 못하면
  else:
    return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/api/submit', methode=['POST'])
def submit():
  return


if __name__=="__main__":
  app.run(debug=True)