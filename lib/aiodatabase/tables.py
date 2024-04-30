from aiodatabase.fields import Integer
from aiodatabase.statements import QuerySingle, QueryInsert

from icecream import ic


class Table:
    def __init__(self, name):
        self._db = None
        self._name = name
        self._fields = {}
        self._statements = {}

    @property
    def name(self):
        return self._name

    def set_parnet_db(self, db):
        self._db = db

    def add_field(self, field):
        self._fields[field.name] = field

    def add_statement(self, label, statement):
        self._statements[label] = statement
    
    async def exec(self, statement, values=None):
        func = self._db._get_function('execute')
        return await func(self, self._statements[statement], values)

    async def exec_iter(self, statement, values=None):
        func = self._db._get_function('execute_all')
        async for row in func(self, self._statements[statement], values):
            yield row

    async def setup(self):
        if self._name in await self._db.tables:
            func = self._db._get_function('describe_table')
            columns = await func(self._name)
            columns_name = [d['name'] for d in columns]
            for field_name, field in self._fields.items():
                if field_name not in columns_name:
                    func = self._db._get_function('alter_table_add_column')
                    await func(self._name, field_name)
        else:
            func = self._db._get_function('create_table')
            await func(self.name, self._fields)
 
class TableVersion(Table):
    def __init__(self):
        super().__init__('version')
        self.add_field(Integer('version'))
        self.add_statement('get_version', QuerySingle("SELECT {fields} FROM {table}", ['version']))        
        self.add_statement('insert_version', QueryInsert("INSERT INTO {table} (version) VALUES ('1')"))