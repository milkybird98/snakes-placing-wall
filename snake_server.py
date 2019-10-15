from flask import Flask,redirect, url_for, request,session,jsonify
from datetime import timedelta
import uuid
from threading import Timer
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY']=os.urandom(24)
room_list=[]

def proc_room_1s():
   for room in room_list:
      if room['started']<=0:
         return
      room['started'] = room['started']+1
      if room['started'] > 600:
         close_room(room)
      else:
         grow_apples(room)
   Timer(1,proc_room_1s).start()


def close_room_exe(room):
   room.clear()
   room = None

def check_eat(room,user):
   if room['map']['apples'].count(user['snake']['head']) == 1:
      room['map']['apples'] = [apple for apple in room['map']['apples'] if not apple == user['snake']['head']]
      user['snake']['len'] += 1
      return True
   else:
      return False

def check_crash(room,user):
   if room['map']['walls'].count(user['snake']['head']) == 1:
      user['snake']['len'] = -1
   
   for other_player in user['player']:
      if other_player['snake']['body'].count(user['snake']['head']) == 1:
         user['snake']['len'] = -1
         break         
            
   for node in user['snake']['body']:
      if room['map']['walls'].count(node) == 1:
         user['snake']['len'] = -1
         break

   if user['snake']['len'] == -1:
      if room['map']['walls'].count(user['snake']['head']) == 0:
         room['map']['apples'].append(user['snake']['head'])
      for node in user['snake']['body']:
         if room['map']['walls'].count(node) == 0:
            room['map']['apples'].append(node)
      return True
   else:
      return False
   
def grow_apples(room):
   while(1):
      x = random.randint(0,99)
      y = random.randint(0,99)
      if room['map']['walls'].count({'x':x,'y':y}) == 0:
         for player in room['player']:
            if player['snake']['body'].count({'x':x,'y':y}) > 0:
               continue
         room['map']['apples'].append({'x':x,'y':y})
         break
      continue
   return

def close_room(room):
   room['started'] = 0
   Timer(10,close_room_exe).start()

def start_room(user):
   room = {}
   room['num_player'] = 1
   room['started'] = 0
   room['player'] = [user]
   room['map']={}
   room['map']['apples']=[]
   room['map']['walls']=[]
   room_list.append(room)
   room_index = room_list.index(room)
   return room_index

def join_room(room,user):
   room['num_player'] = room['num_player']+1
   if room['num_player'] == 8:
      room['started'] == 1
   room['players'].append(user)

def join_game(user):
   for room in room_list:
      if room.get('started') == 0:
         if room.get('num_player') < 8:
            join_room(room,user)
            return room_list.index(room)
   else:
      room_index = start_room(user)
      return room_index

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/join/<name>')
def reg_user(name):
   session['uuid'] = uuid.uuid1()
   user = {'uuid':session['uuid'],'name':name,'score':0,'un_get_wall_count':0,'snake':{'body':[],'len':3,'head':{}}}
   room = join_game(user)
   session['room'] = room 
   return 'uuid'

@app.route('/updaye/score',method = ['POST'])
def update_score():
   room = room_list[session.get('room')]
   if room != None: 
      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]
      user['score'] = eval(request.form['data'])['score']
      return 'success'
   else:
      return 'over'

@app.route('/update/snake',methods = ['POST'])
def update_snake():
   room = room_list[session.get('room')]
   if room != None: 
      snake_body = eval(request.form['body'])
      snake_head = eval(request.form['head'])

      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]
      user['snake']['body'] = snake_body
      user['snake']['head'] = snake_head

      if check_crash(room,user):
         return 'die'
      elif check_eat(room,user):
         return 'eat'
      else:
         return 'success'
   else:
      return 'over'
   
@app.route('/update/wall',methods = ['POST'])
def update_wall():
   room = room_list[session.get('room')]
   if room != None: 
      wall = eval(request.form['wall'])
      room['map']['walls'].append({'x':wall['x'],'y':wall['y']})
      room['map']['apples'].remove({'x':wall['x'],'y':wall['y']})
      for user in room['player']:
         user['un_get_wall_count'] += 1
      return 'success'
   else:
      return 'over'

@app.route('/get/status')
def get_status():
   game_status={}
   room = room_list[session.get('room')]
   if room != None: 
      game_status['time'] = room['started']
      return jsonify(game_status)
   else:
      return 'over'

@app.route('/get/statusfull')
def get_status_f():
   game_status={}
   room = room_list[session.get('room')]
   if room != None: 
      game_status['time'] = room['started']
      game_status['player'] = []
      for user in room['player']:
         game_status['player'].append({'uuid':user['uuid'],
                        'name':user['name']})
      return jsonify(game_status)
   else:
      return 'over'

@app.route('/get/snakes')
def get_snakes():
   snakes=[]
   room = room_list[session.get('room')]
   if room != None:
      for user in room['players']:
         snakes.append({'uuid':user['uuid'],
                        'body':user['snake']['body'],
                        'len':user['snake']['len'],
                        'head':user['snake']['head']})
      return jsonify(snakes)
   else:
      return 'over'

@app.route('/get/scores')
def get_scores():
   scores=[]
   room = room_list[session.get('room')]
   if room != None:
      for user in room['player']:
         scores.append({'uuid':user['uuid'],
                        'score':user['score']})
      return jsonify(scores)
   else:
      return 'over'

@app.route('/get/walls')
def get_walls():
   room = room_list[session.get('room')]
   if room != None:
      wall_data=[]
      user = [user for user in room['player'] if user['uuid'] == session['uuid']]
      if user['un_get_wall_count'] > 0:
         un_get_wall = room['map']['walls'][user['un_get_wall_count']:]
         for wall in un_get_wall:
            user['un_get_wall_count'] -= 1
            wall_data.append({'x':wall['x'],'y':wall['y']})
         return jsonify(wall_data)
      else:
         return 'empty'
   else:
       return 'over'

@app.route('/get/apples')
def get_apples():
   room = room_list[session.get('room')]
   print(room)
   if room != None:
      return jsonify(room['map']['apples'])
   else:
      return 'over'

if __name__ == '__main__':
   Timer(1,proc_room_1s).start()
   app.run(debug=True)
   