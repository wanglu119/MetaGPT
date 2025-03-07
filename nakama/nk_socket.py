import websocket
import json

class WSRequestHandler():
    def __init__(self):
        # TO DO: add timeouts to requests
        self.cid_count = 0
        self.requests = {}
        self.results = {}

    def get_cid(self):
        if len(self.requests.keys()) == 0:
            self.cid_count = 0
        self.cid_count += 1
        return self.cid_count

    def add_request(self, cid, request):
        res = self.results.get(cid)
        if res is None:
            self.requests[cid] = request
        else:
            request.res = res
            del self.results[cid]

    def handle_result(self, cid, result):
        waiter = self.requests.get(cid)
        if waiter is None:
            self.results[cid] = result
        else:
            waiter.res = result
            del self.requests[cid]
 
def on_error(ws,error):
  print("ws on_error:",error)

def on_close(ws,a,b):
  print('### closed ###')
  print(ws,a,b)

class NakamaSocket():
    @property
    def handlers(self):
        return self._handlers

    @property
    def channel(self):
        return self._channel
    
    @property
    def request_handler(self):
        return self._request_handler

    def __init__(self, client):
        self.client = client
        self._request_handler = WSRequestHandler()
        self._channel = Channel(self)

        self.websocket = None
        self.wsOpen = False

    def on_open(self,ws):
      print("### open ###")
      self.wsOpen = True

      roomname = self.client.session.channelName
      type = 1
      persistence = False
      hidden = False

      self.channel.join(roomname,type, persistence, hidden)

    def on_message(self,ws,message):
      print("on_message:",message)
      jObj = json.loads(message)
      if jObj.get('cid') is not None:
          cid = jObj.pop('cid')
          chid = jObj["channel"]["id"]
          self.channel.channel_id = chid

    def connect(self, loop=None):
        assert self.client.session.token is not None, 'You must set session.token'

        url_path = self.client._http_uri + ('/ws?token=%s' %
                                            self.client.session.token)
        
        url_path = url_path.replace("http","ws")

        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(url_path,
                                    on_message = self.on_message,
                                    on_error = on_error,
                                    on_close = on_close
                                    )

        self.websocket = ws
        ws.on_open = self.on_open

        self.websocket.run_forever()

    def send(self, msg):
        self.websocket.send(msg)
        

class Channel():

    def __init__(self, socket):
        self.ws = socket
        self.rq_handler = socket.request_handler
        self.channel_id =""

    def join(self, target, type, persistence, hidden):
        cid = '%d' % self.rq_handler.get_cid()

        data = {
            'target': target,
            'type': type,
            'persistence': persistence,
            'hidden': hidden
        }

        message = {
            'cid': cid,
            'channel_join': data
        }
        self.ws.send(json.dumps(message))

    def send_message(self,content):
        cid = '%d' % self.rq_handler.get_cid()

        content = json.dumps(content)
        data = {
            'channel_id': self.channel_id,
            'content': content
        }

        message = {
            'cid': cid,
            'channel_message_send': data
        }
        s = json.dumps(message)
        self.ws.send(s)