from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryUpdate, QueryDelete, QueryInsert

class Apps(Table):
    def __init__(self):
        super().__init__('apps')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('token'))
        self.add_field(Text('app'))
        self.add_field(Text('icon'))
        self.add_field(Text('label'))
        #
        self.add_statement('add', QueryInsert("INSERT INTO {table} (token, app, icon, label) VALUES (?, ?, ?, ?)", 
                                              ['token', 'app', 'icon', 'label']))        
        self.add_statement('get_token_by_app', QuerySingle("SELECT {fields} FROM {table} WHERE app=?", 
                                                         ['token'], ['app']))        
        self.add_statement('get_id_by_token', QuerySingle("SELECT {fields} FROM {table} WHERE token=?", 
                                                          ['id'], ['token']))        
        self.add_statement('get_all', QueryMulti("SELECT {fields} FROM {table}", ['id', 'icon', 'label'])) 
    
class Message(Table):
    def __init__(self):
        super().__init__('message')
        self.add_field(Integer('app'))
        self.add_field(Text('type'))
        self.add_field(Text('text'))
        self.add_field(Text('md5'))
        self.add_field(Integer('timestamp'))
        #
        self.add_statement('get_timestamp_by_md5', QuerySingle("SELECT {fields} FROM {table} WHERE md5=?", ['timestamp'], ['md5'])) 
        self.add_statement('add', QueryInsert("INSERT INTO {table} (app, type, text, md5, timestamp) VALUES (?, ?, ?, ?, ?)", 
                                              ['app', 'type', 'text', 'md5', 'timestamp']))   
        self.add_statement('get_all', QueryMulti("SELECT {fields} FROM {table} ORDER BY timestamp DESC", ['app', 'type', 'text', 'md5', 'timestamp'])) 
        self.add_statement('delete', QueryDelete("DELETE FROM {table} WHERE md5=?", ['md5'])) 
     
    
    
