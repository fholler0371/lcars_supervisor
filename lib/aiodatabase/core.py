from aiodatabase.helper import async_property
from aiodatabase.exceptions import FunctionNotFoundException
from aiodatabase.tables import Table, TableVersion

import aiodatabase.engines.sqlite as sqlite


class DB:
    def __init__(self, name, use_version=True):
        self.engine = None
        self._tables_in_db = []
        self._tables = {}
        self._use_version = use_version
        self._version = None
        if name.startswith('sqlite://'):
            self.engine = sqlite.DB(name[10:], self)
        else:
            raise NameError('unknown database engine')
        
    @async_property    
    async def tables(self):
        if len(self._tables_in_db) == 0:
            func = self._get_function('list_tables')
            self._tables_in_db = await func()
        return self._tables_in_db
    
    @property
    def version(self):
        return self._version

    def connect(self):
        return self.engine.connect()

    def add_table(self, table: Table):
        self._tables[table.name] = table
        table.set_parnet_db(self)

    def table(self, name):
        return self._tables[name]

    async def setup(self):
        if self._use_version:
            self.add_table(TableVersion())
        for _, table in self._tables.items():
            await table.setup()
        if self._use_version:
            res = await self.table('version').exec('get_version')
            if res and 'version' in res:
                self._version = res['version']
            if self._version is None:
                await self.table('version').exec('insert_version')
                self._version = 1

    def _get_function(self, func_name):
        if self.engine is not None and hasattr(self.engine, func_name):
            return getattr(self.engine, func_name)
        else:
            raise FunctionNotFoundException(func_name)
        
