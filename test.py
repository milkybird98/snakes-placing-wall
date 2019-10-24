

@app.route('/',methods = ['POST'])
def exp():
  res = check(session)
  if res != 'success':
    return 'error'
  
  data = request.json.get['data']
  if data != None:
    res = do_something_with_data(data,session)
  else:
    return 'error'

  if res['state'] == 'success':
    session['somearg']=res['data']['somearg']
    return 'done'
  else:
    return 'error'