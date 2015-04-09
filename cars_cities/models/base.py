from django.db import connections


class BaseModel(object):
    DB = 'default'
    
    def execute_query(self, query, args=[], db=None):
        if not db:
            db = self.DB
        cursor = connections[db].cursor()
        cursor.execute(query, args)
        result = cursor.fetchall()
        cursor.close()
        return result
    