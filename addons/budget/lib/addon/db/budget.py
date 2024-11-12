from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryInsert

class Category(Table):
    def __init__(self):
        super().__init__('category')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('label'))
        self.add_field(Integer('activ'))
        self.add_field(Integer('days'))
        #
        self.add_statement('get_all', QueryMulti("SELECT {fields} FROM {table} order by label", ['id', 'label', 'activ', 'days']))        

class Budgets(Table):
    def __init__(self):
        super().__init__('budgets')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Integer('category'))
        self.add_field(Text('start'))
        self.add_field(Text('end'))
        self.add_field(Integer('amount'))
        #
        self.add_statement('get_by_category', QueryMulti("SELECT {fields} FROM {table} where category=? order by end", 
                                                         ['id', 'category', 'start', 'end', 'amount'],['category']))        

class Bought(Table):
    def __init__(self):
        super().__init__('bought')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Integer('category'))
        self.add_field(Text('name'))
        self.add_field(Integer('amount'))
        self.add_field(Integer('count'))
        #
        self.add_statement('get_sum', QuerySingle("SELECT sum(amount) as {fields} FROM {table} where category=?", 
                                                         ['amount'],['category']))        
