from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QuerySingle, QueryInsert, QueryUpdate

class Users(Table):
    def __init__(self):
        super().__init__('users')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('user_id'))
        self.add_field(Text('name'))
        self.add_field(Text('roles'))
        self.add_field(Text('roles_sec'))
        self.add_field(Text('apps'))
        self.add_field(Text('apps_sec'))
        self.add_field(Text('label'))
        #
        self.add_statement('get_user_by_name', QuerySingle("SELECT {fields} FROM {table} WHERE name=?", ['id', 'user_id'], ['name']))        
        self.add_statement('get_user_by_user_id', QuerySingle("SELECT {fields} FROM {table} WHERE user_id=?", ['id', 'user_id'], ['user_id']))        
        self.add_statement('get_id_by_user_id', QuerySingle("SELECT {fields} FROM {table} WHERE user_id=?", ['id'], ['user_id']))        
        self.add_statement('get_name_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['name'], ['id']))        
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (user_id, name) VALUES (?, ?)", 
                                                 ['user_id', 'name']))
        self.add_statement('update_roles_by_user_id', QueryUpdate("UPDATE {table} SET roles=?, roles_sec=? WHERE user_id=?", ['roles', 'roles_sec', 'user_id']))        
        self.add_statement('get_role_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['roles'], ['id']))        
        self.add_statement('get_role_sec_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['roles_sec'], ['id']))        
        self.add_statement('update_apps_by_user_id', QueryUpdate("UPDATE {table} SET apps=?, apps_sec=? WHERE user_id=?", ['apps', 'apps_sec', 'user_id']))        
        self.add_statement('get_app_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['apps'], ['id']))        
        self.add_statement('get_app_sec_by_id', QuerySingle("SELECT {fields} FROM {table} WHERE id=?", ['apps_sec'], ['id']))        
