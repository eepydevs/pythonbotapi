import redis as rd
import atexit
import json
import os

class JsonFile(object):
  __data: Dict[Any, Any]
  def __init__(self, filename):
      self.filename = filename
      self.__data = {}
      self.load()

  def __enter__(self):
      return self.__data

  def __exit__(self, exc_type, exc_val, exc_tb):
      self.save()

  def __contains__(self, item):
      return item in self.__data

  def load(self):
      try:
          with open(self.filename, 'r') as f:
              self.__data = json.load(f)
      except (FileNotFoundError, json.decoder.JSONDecodeError):
          with open(self.filename, 'w') as f:
              json.dump({}, f)

  def save(self):
      with open(self.filename, "w") as f:
          json.dump(self.__data, f, indent = 4)

  @property
  def data(self):
      return self.__data

  @data.setter
  def data(self, value):
      self.__data = value

class RedisDB(dict):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True):
      self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses)
      super().__init__()
      self._backup = JsonFile("backup.json")
      self._name = name
      self._key = key if key else name
      self._var = self._load(True)
      atexit.register(self.__del)
      self._redis.close()

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

  def _load(self, backup = False):
      if self._key not in self._redis.keys():
          self._redis.hset(self._name, self._name, "{}")
      self._var = json.loads(self._redis.hget(self._name, self._key))
      if backup:
          if self._var != self._backup.data and self._backup.data:
              self._var = self._backup.data
              self._backup.data = {}
              self._backup.save()
      return self._var

  def _save(self):
      try:
          if self._var != json.loads(self._redis.hget(self._name, self._key)):
              self._redis.hset(self._name, self._key, json.dumps(self._var))
      except:
          self._backup.data = self._var
          self._backup.save()

  def __del(self):
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

db = RedisDB(host = os.environ["REDISHOST"], port = os.environ["REDISPORT"], password = os.environ["REDISPASSWORD"], client_name = os.environ["REDISUSER"])