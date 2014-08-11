# memoize decorator (for Google App Engine)
Decorator to memoize functions results using Google App Engine current instance memory (cachepy) and memcache.
Support any pickable arguments and function returns.

Optional Decorator Args:

* time - duration before cache is refreshed
* ignore_args - sequence numbers (0, 1, 3...) of decorated funcion args to be ignored 
* force_cache - forces caching on dev_server (useful for APIs, etc.)
* version_aware - ignores cache values from a different app version
    
Optional Decorated Function Args:

* _force_run - forces caching

Usage:  

    @memoize(86400) #or memoize()
    def updateAllEntities(key_name, params):
        entity = Model.get_by_key_name(key_name)
        for param in params.items():
            setattr(entity, param.key(), param.value())
        db.put(entity) 

