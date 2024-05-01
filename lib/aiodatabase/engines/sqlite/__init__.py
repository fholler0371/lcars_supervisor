import aiosqlite

import aiodatabase
from aiodatabase.statements import single_query, insert_query, multi_query


class DB:
    def __init__(self, name, db):
        self.name = name
        self._db = db

    def connect(self):
        return aiosqlite.connect(self.name) 
    
    async def list_tables(self):
        tables = []
        async with self.connect() as db:
            async with db.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%'") as cursor:
                async for row in cursor:
                    tables.append(row[0])
        return tables
    
    async def describe_table(self, table):
        columns = []
        async with self.connect() as db:
            async with db.execute(f"pragma table_info({table})") as cursor:
                async for row in cursor:
                    columns.append({'id': row[0], 'name': row[1], 'type': row[2]})
                    #ic(row[3])
                    #ic(row[4])
                    #ic(row[5])
        return columns
    
    async def create_table(self, name, fields):
        columns = []
        for _, field in fields.items():
            statement = f'{field.name} {field.type}'
            if field.type == 'INTEGER' and hasattr(field, '_autoincrement') and field._autoincrement:
                statement += ' PRIMARY KEY AUTOINCREMENT'                
            if field._default:
                statement += ' DEFAULT {field._default}'                
            columns.append(statement)
        sql = f"CREATE TABLE {name} ({', '.join(columns)})"
        async with self.connect() as db:
            await db.execute(sql)
            await db.commit()

    async def alter_table_add_column(self, name, field):
        _field = self._db.table(name)._fields[field]
        statement = f'{_field.name} {_field.type}'
        if _field.type == 'INTEGER' and hasattr(_field, '_autoincrement') and _field._autoincrement:
            statement += ' PRIMARY KEY AUTOINCREMENT'  
        if _field._default is not None:
            statement += f" DEFAULT '{_field._default}'"
        sql = f"ALTER TABLE {name} ADD COLUMN {statement}"
        async with self.connect() as db:
            await db.execute(sql)
            await db.commit()

    async def execute(self, table, statement, values):
        fields = '' if statement.fields is None else ', '.join(statement.fields)
        table = table._name
        sql = statement.sql
        sql = sql.replace('{fields}', fields) if '{fields}' in sql else sql 
        sql = sql.replace('{table}', table) if '{table}' in sql else sql
        parameters = None
        if len(statement.values) > 0:
            parameters = []
            for value in statement.values:
                parameters.append(values[value])
            parameters = tuple(parameters)
        async with self.connect() as db:
            if statement.mode == single_query:
                db.row_factory = aiodatabase.Row
                result = await db.execute_fetchall(sql, parameters=parameters)
                if len(result) == 0:
                    return None
                return self.result_to_dict(self._db.table(table)._fields, result[0])
            elif statement.mode == insert_query:
                await db.execute(sql, parameters=parameters)
                await db.commit()
                return None
        return None

    async def execute_all(self, table, statement, values):
        fields = '' if statement.fields is None else ', '.join(statement.fields)
        table = table._name
        sql = statement.sql
        sql = sql.replace('{fields}', fields) if '{fields}' in sql else sql 
        sql = sql.replace('{table}', table) if '{table}' in sql else sql
        async with self.connect() as db:
            if statement.mode == multi_query:
                db.row_factory = aiodatabase.Row
                result = await db.execute_fetchall(sql, parameters=values)
                _fields = self._db.table(table)._fields
                for row in result:
                    yield self.result_to_dict(_fields, row)

    def result_to_dict(self, fields, row):
        out = {}
        for key in row.keys():
            match fields[key].type:
                case 'INTEGER':
                    out[key] = int(row[key])
                case _:
                    out[key] = row[key]
        return out            
