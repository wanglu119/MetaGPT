import re
import time
import json
import base64

import requests

class NakamaClient():
  def __init__(self, host, port, server_key, use_ssl=False):
    self.host = host
    self.port = port
    self.use_ssl = use_ssl

    protocol = use_ssl and 'https' or 'http'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    self._http_uri = '%s://%s:%d' % (protocol, host, port)
    self._http_session = requests.session()
    self._session = Session(self, server_key)
    self._account = Account(self)

  @property
  def session(self):
      return self._session
  
  @property
  def account(self):
      return self._account

JWT_REG = re.compile('^([A-Za-z0-9-_=]+)\.([A-Za-z0-9-_=]+)\.?([A-Za-z0-9-_.+/=]*)$')

class Session():
    @property
    def expired(self):
        return time.time() > self.expires

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self.set_token(token)

    @property
    def auth_header(self):
        return self._auth_header

    def __init__(self, client, server_key):
        self.client = client
        self.set_basic(server_key)

    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token

    def set_basic(self, server_key):
        self._token = None
        self.refresh_token = None
        self.expires = None
        self.username = None
        self.user_id = None
        self.vars = None

        server_key = '%s:' % server_key

        self._auth_header = {
            'Authorization': 'Basic %s' % base64.b64encode(server_key.encode()).decode()
        }
    
    def set_token(self, token):
        p1, p2, p3 = JWT_REG.match(token).groups()
        assert p1 and p2 and p3, 'JWT is not valid'

        p2 = p2.encode()
        pad = len(p2) % 4
        p2 += b"="*pad  # correct padding
        decoded_token = json.loads(base64.b64decode(p2))

        self._token = token
        self.expires = decoded_token['exp']
        self.username = decoded_token['usn']
        self.user_id = decoded_token['uid']
        self.vars = decoded_token.get('vrs')

        self._auth_header = {
            'Authorization': 'Bearer %s' % token
        }

class Account():

    def __init__(self, client):
        self.client = client

        self._authenticate = Authenticate(client)
        
    @property
    def authenticate(self):
        return self._authenticate
        
class Authenticate():
    # TO DO:
    # update session when auth

    def __init__(self, client):
        self.client = client

    def email(self, email, password,
                    vars=None, create=None, username=None):
        params = {}
        if create is not None:
            params['create'] = create and 'true' or 'false'
        if username is not None:
            params['username'] = username

        body = {
            'email': email,
            'password': password
        }
        if vars is not None:
            body['vars'] = vars

        headers = self.client.session.auth_header

        url_path = self.client._http_uri + '/v2/account/authenticate/email'
        resp = self.client._http_session.post(url_path, params=params,
                                                  headers=headers,
                                                  json=body) 
        return  resp.json()
