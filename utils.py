import redis as rd
import json
import os

def ping(redis: rd.Redis):
  success = 0
  try:
      redis.ping()
      success = 1
  except (rd.exceptions.AuthenticationError, rd.exceptions.ConnectionError) as err:
      pass
  return success

class RedisConnectionError(Exception):
    pass

class RedisDB(dict):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True):
      self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses)
      super().__init__()
      self._name = name
      self._key = key if key else name
      self._var = self._load()
      atexit.register(self.__del)
      self.ping_success = ping(self._redis)
      if not self.ping_success:
          raise RedisConnectionError("Unable to connect to Redis. Use Replit as backup.")

  def __getitem__(self, key):
      return self._var[key]

  def __setitem__(self, key, value):
      self._var[key] = value

  def __repr__(self):
      return self._var.__repr__()

  def __enter__(self) -> dict:
      return self._load()

  def __exit__(self, exc_type, exc_value, exc_traceback):
      self._save()

  def __contains__(self, item):
      return item in self._var

  def _load(self):
      if self._key not in self._redis.keys():
          self._redis.hset(self._name, self._name, "{}")
      self._var = json.loads(self._redis.hget(self._name, self._key))
      return self._var

  def _save(self):
      if self._var != json.loads(self._redis.hget(self._name, self._key)):
          self._redis.hset(self._name, self._key, json.dumps(self._var))

  def __del(self):
      if self.ping_success:
          self._save()

class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]
    
class RedisManager(metaclass = Singleton):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True):
    self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses)
    self._name = name
    self._key = key if key else name
  
  def __enter__(self) -> dict:
    if self._key not in self._redis.keys():
      self._redis.hset(self._name, self._name, "{}")
    self._var = json.loads(self._redis.hget(self._name, self._key))
    return self._var
  
  def __exit__(self, exc_type, exc_value, exc_traceback):
    if self._var != json.loads(self._redis.hget(self._name, self._key)):
      self._redis.hset(self._name, self._key, json.dumps(self._var))