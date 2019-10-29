from flask import Flask,redirect, url_for, request,session,jsonify
from datetime import timedelta
import uuid
from threading import Timer
import os
import random
import logging

WIN_WALL_COUNT = 500

app = Flask(__name__)
app.config['SECRET_KEY']=os.urandom(24)
game_data=[]

# sub-routine for room status update operation per sencond 
#
# return:
#        None
#
# sub-call:
#        skip, for room not start;
#        close_room, for room expire time;
#        grow_apples, for grow a new apple in map
def proc_room_1s():
   logging.debug('BEGIN preocess room')
   for room in game_data:
      start_time = room.get('started')
      if start_time == None:
         continue
      print(start_time)
      print(len(room['map']['walls'])-328)
      if start_time<=0:
         logging.debug('room not started, player: ' + str(room['player']))
         continue

      if start_time == 600:
         logging.debug('room game over, player: ' + str(room['player']))
         close_room(room)
      elif len(room['map']['walls']) > WIN_WALL_COUNT + 328:
         logging.debug('room game finish, player: ' + str(room['player']))
         close_room(room)
      else:
         logging.debug('room run normally, player: ' + str(room['player']))
         grow_apples(room)
         logging.debug('all apples: ' + str(room['map']['apples']))
         room['started'] = start_time + 1

   Timer(1,proc_room_1s).start()
   logging.debug('END preocess room')

# function for check whether the new movements of one shake have eated an apple
#
# return:
#        True, for the user's snake has eaten;
#        False, for not
#
# sub-call:
#        None
def check_eat(room,user):
   if room['map']['apples'].count(user['snake']['head']) == 1:
      room['map']['apples'] = [apple for apple in room['map']['apples'] if not apple == user['snake']['head']]
      user['snake']['len'] += 1
      return True
   else:
      return False

# function for check whether the new movements of one snake have crashed the wall or other snakes
#
# return:
#        True, for the snake died
#        False, for the snake still be alive
#
# sub-call:
#        None
def check_crash(room,user):
   if room['map']['walls'].count(user['snake']['head']) == 1:
      user['snake']['len'] = -1
   
   for other_player in room['player']:
      if other_player['snake']['len'] > 0 and other_player['snake']['body'].count(user['snake']['head']) == 1:
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

# generate the init wall around the whole map
#
# return:
#        None
#
# sub-call:
#        None
def init_wall(room):
   column_start, column_end = 17, 112 
   row = 70
   
   for x in range(column_start, column_end):
      pos = {}
      pos['x'] = x
      pos['y'] = 0
      room['map']['walls'].append(pos)

   for x in range(column_start, column_end):
      pos = {}
      pos['x'] = x
      pos['y'] = row-1
      room['map']['walls'].append(pos)

   for y in range(1, row):
      pos = {}
      pos['x'] = column_start
      pos['y'] = y
      room['map']['walls'].append(pos)

   for y in range(1, row):
      pos = {}
      pos['x'] = column_end-1
      pos['y'] = y
      room['map']['walls'].append(pos)


# grow new apples in game map
#
# return:
#        None
#
# sub-call:
#        randint, for generate position of new apple
def grow_apples(room):
   if len(room['map']['apples']) > 30:
      return

   while(1):
      x = random.randint(18,111)
      y = random.randint(1,69)

      if room['map']['walls'].count({'x':x,'y':y}) > 0:
         continue

      for player in room['player']:
         if player['snake']['body'].count({'x':x,'y':y}) > 0:
            continue

      room['map']['apples'].append({'x':x,'y':y})
      break
   return

# close game room actually operation
#
# return:
#        None
#
# sub-call:
#        None
def close_room_exe(room):
   logging.info('room closed, player: ' + str(room['player']))
   room.clear()
   return

# close game room pre operation
#
# return:
#        None
#
# sub-call:
#        Timer, for exec the actually operation 10 senconds later
def close_room(room):
   room['started'] = -1
   Timer(10,close_room_exe,(room,)).start()

# start a new room for no rooms can join
#
# return:
#        room_index, for the room that the caller has joined or created in room list
#
# sub-call:
#        init_wall, for generate the walls around the game map
def start_room(user):
   room = {}
   room['num_player'] = 1
   room['started'] = 0
   room['player'] = [user]
   room['map']={}
   room['map']['apples']=[]
   room['map']['walls']=[]
   init_wall(room)

   for i in range(len(game_data)):
      if game_data[i] == 'empty':
         game_data[i] = room
         room_index = i
         logging.info("new room create, index: " + str(room_index))
         return room_index

   game_data.append(room)
   room_index = game_data.index(room)
   logging.info("new room create, index: " + str(room_index))
   return room_index

# join a room
#
# return:
#        None
#
# sub-call:
#        None
def join_room(room,user):
   room['num_player'] = room['num_player']+1
   if room['num_player'] == 4:
      logging.info("one room start game")
      room['started'] = 1
   room['player'].append(user)

# join game by joining a room or creating a new room
def join_game(user):
   for room in game_data:
      if room.get('started') == 0:
         if room.get('num_player') < 4:
            join_room(room,user)
            return game_data.index(room)
   else:
      room_index = start_room(user)
      return room_index

def check_player(session):
   if session.get('uuid') == None:
      logging.warn('player not join server')
      return 'clierr'
   elif session.get('room') == None:
      logging.warn('player not join room, uuid: ' + str(session['uuid']))
      return 'clierr'
   elif session['room'] > len(game_data):
      logging.critical('room index higher than list, uuid: ' + str(session['uuid'])+',room_index: ' + str(session['room']))
      return 'inerr'
   else:
      return 'fine'

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/sync',methods = ['POST'])
def sync_world():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]

   sync_data={}

   if room != None: 
      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]
      user['score'] = request.json['data']['score']

      logging.info('player score updated, uuid: ' + str(session['uuid'])+', score: ' + str(user['score']))
      logging.debug('all player: ' + str(room['player']))
   else:
      return 'inerr'

   game_status={}
   if room != None: 
      game_status['time'] = room['started']
      logging.info('player get simple status, uuid: ' + str(session['uuid']))
      logging.debug('status data: ' + str(game_status))
      sync_data['game_status']=game_status
   else:
      return 'inerr'

   scores=[]
   if room != None:
      logging.info('try to get score data, uuid: ' + str(session['uuid']))
      logging.debug('all player data: ' + str(room['player']))

      for user in room['player']:
         scores.append({'uuid':user['uuid'],
                        'score':user['score']})

      logging.debug('return data: ' + str(scores))
      sync_data['scores']=scores
   else:
      logging.warn('player not join room, uuid: ' + str(session['uuid']))
      return 'inerr'

   snakes=[]
   if room != None:
      logging.info('try to get snakes data, uuid: ' + str(session['uuid']))
      logging.debug('all player data: ' + str(room['player']))

      for user in room['player']:
         snakes.append({'uuid':user['uuid'],
                        'body':user['snake']['body'],
                        'len':user['snake']['len'],
                        'head':user['snake']['head']})

      logging.debug('return data: ' + str(snakes))  
      sync_data['snakes']=snakes

   wall_data=[]
   if room != None:
      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]

      logging.info('try to get wall data, uuid: ' + str(session['uuid']))
      logging.debug('all wall: ' + str(room['map']['walls']))

      if user['un_get_wall_count'] > 0:
         un_get_wall = room['map']['walls'][-user['un_get_wall_count']:]
         for wall in un_get_wall:
            user['un_get_wall_count'] -= 1
            wall_data.append({'x':wall['x'],'y':wall['y']})

         logging.debug('return data: ' + str(wall_data))
         sync_data['wall_data']=wall_data
      else:
         sync_data['wall_data']='empty'
   else:
      logging.warn('player not join room, uuid: ' + str(session['uuid']))
      return 'inerr'

   if room != None:

      logging.info('try to get apple data, uuid: ' + str(session['uuid']))
      logging.debug('all apples: ' + str(room['map']['apples']))

      if len(room['map']['apples']) == 0:
         sync_data['apples']='empty'
      else:
         sync_data['apples']=room['map']['apples']
   else:
      return 'inerr'

   return jsonify({'res':'success','data':sync_data})
   

@app.route('/join/<name>')
def reg_user(name):
   session['uuid'] = uuid.uuid1()
   user = {'uuid':session['uuid'],'name':name,'score':0,'un_get_wall_count':0,'un_get_apple_count':0,'snake':{'body':[],'len':0,'head':{}}}
   room = join_game(user)
   session['room'] = room 
   logging.info('new player join server, uuid: ' + str(user['uuid'])+', name: ' + str(user['name']))
   logging.info('room index: ' + str(room))
   return str(session['uuid'])

@app.route('/update/score',methods = ['POST'])
def update_score():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]
   if room != None: 
      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]
      user['score'] = request.json['data']['score']

      logging.info('player score updated, uuid: ' + str(session['uuid'])+', score: ' + str(user['score']))
      logging.debug('all player: ' + str(room['player']))

      return 'success'
   else:
      return 'inerr'

@app.route('/update/snake',methods = ['POST'])
def update_snake():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]
   if room != None: 
      snake_body = request.json['body']
      snake_head = request.json['head']
      snake_len = request.json['len']

      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]
      user['snake']['body'] = snake_body
      user['snake']['head'] = snake_head
      user['snake']['len'] = snake_len

      logging.info('player snake moved, uuid: ' + str(session['uuid']))
      logging.debug('snakes: ' + str(user['snake']))
      logging.debug('all wall: ' + str(room['map']['walls']))

      if check_crash(room,user):
         logging.info('user snake died, uuid: ' + str(session['uuid']))
         return 'die'
      elif check_eat(room,user):
         logging.info('user snake eats apple, uuid: ' + str(session['uuid']))
         return 'eat'
      else:
         return 'success'
   else:
      return 'inerr'
   
@app.route('/update/wall',methods = ['POST'])
def update_wall():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]
   if room != None: 
      wall = request.json['wall']
      if room['map']['walls'].count({'x':wall['x'],'y':wall['y']}) == 0:

         room['map']['walls'].append({'x':wall['x'],'y':wall['y']})
         if room['map']['apples'].count({'x':wall['x'],'y':wall['y']}) > 0:
            room['map']['apples'].remove({'x':wall['x'],'y':wall['y']})

         logging.info('wall placed, uuid: ' + str(session['uuid'])+',x: ' + str(wall['x'])+',y: ' + str(wall['y']))
         logging.debug('all wall: ' + str(room['map']['walls']))

         if room['map']['walls'].count({'x':wall['x'],'y':wall['y']}) == 1:
            for user in room['player']:
               user['un_get_wall_count'] += 1
         else:
            return 'clierr'
            
         return 'success'
      else:
         return 'clierr'
   else:
      return 'inerr'

@app.route('/get/status')
def get_status():
   res = check_player(session)
   if res != 'fine':
      return res
   game_status={}
   room = game_data[session.get('room')]
   if room != None: 
      game_status['time'] = room['started']
      logging.info('player get simple status, uuid: ' + str(session['uuid']))
      logging.debug('status data: ' + str(game_status))
      return jsonify(game_status)
   else:
      return 'inerr'

@app.route('/debug')
def debug():
   logging.debug(str(game_data))
   return jsonify(game_data)

@app.route('/get/statusfull')
def get_status_f():
   res = check_player(session)
   if res != 'fine':
      return res
   game_status={}
   room = game_data[session.get('room')]
   if room != None: 
      game_status['time'] = room['started']
      game_status['player'] = []
      for user in room['player']:
         game_status['player'].append({'uuid':user['uuid'],
                        'name':user['name']})

      logging.warning(str(game_status['player']))
      logging.info('player get fullly status, uuid: ' + str(session['uuid']))
      logging.debug('status data: ' + str(game_status))
      return jsonify(game_status)
   else:
      return 'inerr'

@app.route('/get/snakes')
def get_snakes():
   res = check_player(session)
   if res != 'fine':
      return res
   snakes=[]
   room = game_data[session.get('room')]
   if room != None:

      logging.info('try to get snakes data, uuid: ' + str(session['uuid']))
      logging.debug('all player data: ' + str(room['player']))

      for user in room['player']:
         snakes.append({'uuid':user['uuid'],
                        'body':user['snake']['body'],
                        'len':user['snake']['len'],
                        'head':user['snake']['head']})

      logging.debug('return data: ' + str(snakes))  
      return jsonify(snakes)
   else:
      return 'inerr'

@app.route('/get/scores')
def get_scores():
   res = check_player(session)
   if res != 'fine':
      return res
   scores=[]
   room = game_data[session.get('room')]
   if room != None:

      logging.info('try to get score data, uuid: ' + str(session['uuid']))
      logging.debug('all player data: ' + str(room['player']))

      for user in room['player']:
         scores.append({'uuid':user['uuid'],
                        'score':user['score']})

      logging.debug('return data: ' + str(scores))
      return jsonify(scores)
   else:
      logging.warn('player not join room, uuid: ' + str(session['uuid']))
      return 'inerr'

@app.route('/get/walls')
def get_walls():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]
   if room != None:
      wall_data=[]
      user = [user for user in room['player'] if user['uuid'] == session['uuid']][0]

      logging.info('try to get wall data, uuid: ' + str(session['uuid']))
      logging.debug('all wall: ' + str(room['map']['walls']))

      if user['un_get_wall_count'] > 0:
         un_get_wall = room['map']['walls'][-user['un_get_wall_count']:]
         for wall in un_get_wall:
            user['un_get_wall_count'] -= 1
            wall_data.append({'x':wall['x'],'y':wall['y']})

         logging.debug('return data: ' + str(wall_data))
         return jsonify(wall_data)
      else:
         return 'empty'
   else:
      logging.warn('player not join room, uuid: ' + str(session['uuid']))
      return 'inerr'

@app.route('/get/apples')
def get_apples():
   res = check_player(session)
   if res != 'fine':
      return res
   room = game_data[session.get('room')]
   if room != None:

      logging.info('try to get apple data, uuid: ' + str(session['uuid']))
      logging.debug('all apples: ' + str(room['map']['apples']))

      return jsonify(room['map']['apples'])
   else:
      return 'inerr'

if __name__ == '__main__':
   logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.WARNING)
   Timer(1,proc_room_1s).start()
   try:
      app.run(debug=False)
   except:
      pass
   