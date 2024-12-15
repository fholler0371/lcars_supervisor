from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text, Float
from aiodatabase.statements import QueryMulti, QuerySingle, QueryUpdate, QueryDelete, QueryInsert

class Vital(Table):
    def __init__(self):
        super().__init__('vital')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Integer('date'))
        self.add_field(Text('type'))
        self.add_field(Float('value'))
        #
        self.add_statement('get_last_by_type', QuerySingle("SELECT {fields} FROM {table} WHERE type=? ORDER BY date DESC", 
                                                           ['value'], ['type']))
        self.add_statement('get_history', QueryMulti("SELECT {fields} FROM {table} WHERE type=? and date>? ORDER BY date DESC", 
                                                           ['value', 'date'], ['type', 'date']))
        self.add_statement('get_avg', QuerySingle("SELECT avg(value) as {fields} FROM {table} WHERE date>? and type='gewicht' ORDER BY date DESC", 
                                                           ['value'], ['date']))

class Daily(Table):
    def __init__(self):
        super().__init__('daily')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Text('type'))
        self.add_field(Float('value'))
        #
        self.add_statement('get_by_date_and_type', QuerySingle("SELECT avg(value) as {fields} FROM {table} WHERE date<=? and date>=? and type=? ORDER BY date DESC", 
                                                           ['value'], ['date_max', 'date_min', 'type']))
        self.add_statement('get_history', QueryMulti("SELECT {fields} FROM {table} WHERE type=? and date>? ORDER BY date DESC", 
                                                           ['value', 'date'], ['type', 'date']))
        self.add_statement('get_avg', QuerySingle("SELECT avg(value) as {fields} FROM {table} WHERE date>? and type='gewicht' ORDER BY date DESC", 
                                                           ['value'], ['date']))

class Sleep(Table):
    def __init__(self):
        super().__init__('sleep')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Integer('start'))
        self.add_field(Integer('end'))
        self.add_field(Text('type'))
        self.add_field(Float('value'))
        #
        self.add_statement('get_last_by_type', QuerySingle("SELECT {fields} FROM {table} WHERE type=? ORDER BY date DESC", 
                                                           ['value'], ['type']))
