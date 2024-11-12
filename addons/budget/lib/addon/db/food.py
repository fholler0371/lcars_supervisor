from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryInsert

class Bought(Table):
    def __init__(self):
        super().__init__('bought')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Text('name'))
        self.add_field(Integer('amount'))
        self.add_field(Integer('count'))
        #
        self.add_statement('get_sum', QuerySingle("SELECT sum(amount) as {fields} FROM {table}", 
                                                         ['amount']))        
