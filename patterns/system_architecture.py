import sqlite3


# Сделал универсальный датамаппер, но не успел адаптировать весь фреймворк к нему, не работает аутентификация
# Unity of work так же не успел реализовать


class DataMapper:

    def __init__(self):
        self.db_name = 'db.sqlite'
        self.connect = sqlite3.connect(self.db_name)
        self.cursor = self.connect.cursor()

    def list(self, model_name):
        self.cursor.execute(f"PRAGMA table_info({model_name})")
        result_fields = [items[1] for items in self.cursor.fetchall()]
        result_fields = ['pk', *result_fields]
        self.cursor.execute(f"SELECT rowid, * FROM {model_name}")
        results = []
        for result in self.cursor.fetchall():
            results.append(dict(zip(result_fields, result)))
        return results

    def retrieve(self, model_name: str, pk: str) -> dict:
        self.cursor.execute(f"PRAGMA table_info({model_name})")
        result_fields = [items[1] for items in self.cursor.fetchall()]
        result_fields = ['pk', *result_fields]

        self.cursor.execute(f"SELECT rowid, * FROM {model_name} WHERE rowid=?", (pk,))
        result = self.cursor.fetchone()
        result = dict(zip(result_fields, result)) if result else {}
        return result

    def create(self, model_name: str, new_data):
        pk = new_data.get('rowid')
        if pk is None:
            command = f"INSERT INTO {model_name} VALUES({','.join('?' * len(new_data))})"
            self.cursor.execute(command, tuple(new_data.values()))
            self.connect.commit()
            self.cursor.execute("SELECT last_insert_rowid()")
            new_data['pk'] = str(self.cursor.fetchone()[0])
        else:
            keys = ', '.join(new_data.keys())
            command = f"INSERT OR REPLACE INTO {model_name} ({keys}) VALUES({','.join('?' * len(new_data))})"
            self.cursor.execute(command, tuple(new_data.values()))
            self.connect.commit()
        return new_data

    def update(self, model_name: str, pk: str, new_data: dict):
        assignments = [f'{key}={value}' for key, value in new_data.items()]
        assignments = ', '.join(assignments)
        command = f"UPDATE {model_name} SET {assignments} WHERE rowid=?"
        self.cursor.execute(command, (pk,))
        self.connect.commit()
        return True

    def delete(self, model_name: str, pk: str):
        self.cursor.execute(f"DELETE FROM {model_name} WHERE rowid=?", (pk,))
        self.connect.commit()
        return True

    def __del__(self):
        self.connect.close()


dm = DataMapper()
