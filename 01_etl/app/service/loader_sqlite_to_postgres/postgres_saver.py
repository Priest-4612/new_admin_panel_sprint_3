from dataclasses import astuple

from psycopg2.extras import execute_values


class PostgresSaver(object):
    def __init__(self, connection):
        self._connection = connection

    def save_data(self, table_data, table, save_rows_size=100):
        if not table_data:
            return
        fields_template = (', ').join(table_data[0].__annotations__.keys())
        fields_template = fields_template.replace('created_at', 'created')
        fields_template = fields_template.replace('updated_at', 'modified')
        tuple_data = [astuple(row) for row in table_data]
        query = """INSERT INTO {tablename} ({fields})
                   VALUES %s
                   ON CONFLICT (id) DO NOTHING;""".format(
            tablename='content.{table}'.format(table=table),
            fields=fields_template,
        )
        execute_values(
            self._connection.cursor(),
            query,
            tuple_data,
            page_size=save_rows_size,
        )
        self._connection.commit()
