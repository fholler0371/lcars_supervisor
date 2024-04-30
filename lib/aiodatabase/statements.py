single_query = 'q'
insert_query = 'i'
multi_query = 'm'

class Statement:
    def __init__(self, sql, fields=None, values=None, mode=single_query):
        self.sql = sql
        self.fields = [] if fields is None else fields
        self.values = [] if values is None else values
        self.mode = mode

QuerySingle = Statement

class QueryInsert(Statement):
    def __init__(self, sql, values=None):
        super().__init__(sql, None, values, insert_query)

class QueryMulti(Statement):
    def __init__(self, sql, fields=None, values=None):
        super().__init__(sql, fields, values, multi_query)