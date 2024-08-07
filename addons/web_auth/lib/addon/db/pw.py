from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QuerySingle, QueryInsert, QueryUpdate

class Pw(Table):
    def __init__(self):
        super().__init__('pw')
        self.add_field(Integer('id'))
        self.add_field(Text('password'))
        #
        self.add_statement('get_password_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['password'], ['id']))    
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (id, password) VALUES (?, ?)", 
                                                 ['id', 'password']))
        self.add_statement('update', QueryUpdate("UPDATE {table} SET password=? WHERE id=?", 
                                                 ['password', 'id']))

class Otp(Table):
    def __init__(self):
        super().__init__('otp')
        self.add_field(Integer('id'))
        self.add_field(Text('otp'))
        #
        self.add_statement('get', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['otp'], ['id']))    
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (id, otp) VALUES (?, ?)", 
                                                 ['id', 'otp']))
        self.add_statement('update', QueryUpdate("UPDATE {table} SET otp=? WHERE id=?", 
                                                 ['otp', 'id']))
