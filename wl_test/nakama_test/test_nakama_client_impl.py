import time
import threading

from nakama.nk_client import NakamaClient
from nakama.nk_socket import NakamaSocket

def main(): 
  client = NakamaClient('192.168.0.201', 7350, 'defaultkey')
  resp = client.account.authenticate.email("testPython@tusen.ai","password")
  client.session.token = resp["token"]
  
  sock = NakamaSocket(client=client)
  def send():
      while True:
        if not sock.wsOpen:
            time.sleep(1)
        chan = sock.channel
        chan.send_message({"python":"python nakama"})
        time.sleep(1)
  t = threading.Thread(target=send)
  t.start()
  sock.connect()

if __name__ == '__main__':
  main()

