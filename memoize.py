# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import pickle
from pickle import PicklingError
import os 

from google.appengine.api import memcache
import cachepy

memcache = memcache.Client()

ACTIVE_ON_DEV_SERVER = True
      
def memoize(time=60*60*24, ignore_args=[], force_cache=False, version_aware=True):    
    """Decorator to memoize functions using cachepy + memcache.
    
    Optional Decorator Args:
      time - duration before cache is refreshed
      ignore_args - sequence numbers (0, 1, 3...) of decorated funcion args to be ignored 
      force_cache - forces caching on dev_server (useful for APIs, etc.)
      version_aware - ignores cache values from a different app version
    
    Optional Decorated Function Args:
      _force_run - forces caching
    
    Usage:
      
      @memoize(86400) #or memoize()
      def updateAllEntities(key_name, params):
         entity = Model.get_by_key_name(key_name)
         for param in params.items():
            setattr(entity, param.key(), param.value())
            db.put(entity) 
      
    
    """
    def decorator(fxn):
        def wrapper(*args, **kwargs):
            arg_list = []
            for i, arg in enumerate(args):
                try:
                    if not i in ignore_args: 
                        arg_list.append(pickle.dumps(arg))
                except PicklingError:
                    raise UnsupportedArgumentError(arg)
            for kwarg in kwargs.items():
                try:
                    arg_list.append(pickle.dumps(kwarg[1]))
                except PicklingError:
                    raise UnsupportedArgumentError(kwarg)
            key = fxn.__name__ + '(' + ','.join(arg_list) + ')'
            if version_aware:
                key = os.environ['CURRENT_VERSION_ID'] + '/' + key
            #logging.debug('caching key: %s' % key)
            data = cachepy.get(key) or memcache.get(key)
            if Debug(): 
                if not ACTIVE_ON_DEV_SERVER and not force_cache: 
                    return fxn(*args, **kwargs)
            if kwargs.get('_force_run'):
                #logging.debug("forced execution of %s" % fxn.__name__)
                pass
            elif data:
                #logging.debug('cache hit for key: %s' % key)
                if data.__class__ == NoneVal: 
                    data = None
                return data
            data = fxn(*args, **kwargs)
            data_to_save = data
            if data is None:
                data_to_save = NoneVal() 
            cachepy.set(key, data_to_save, time / 24) #cachepy expiry time must be much shorter
            memcache.set(key, data_to_save, time)
            return data
        return wrapper
    return decorator



""" Util Methods """

class UnsupportedArgumentError(Exception):
    ''' An unsupported argument has been passed to Memoize fxn '''
    def __init__(self, value):
        self.arg = value
    def __str__(self):
        return repr(type(self.arg).__name__ + " is not a supported arg type (not pickable)")

def Debug():
    '''return True if script is running in the development envionment'''
    return os.environ['SERVER_SOFTWARE'].startswith('Dev')
    
    
""" Singleton Classes """
    
class NoneVal():
    ''' A replacement for None, so a memoized fxn can return a None val
      without making the Memoize fxn assume that the "None" means there
      isn't a cached value '''
    pass
