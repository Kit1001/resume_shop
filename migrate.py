import sqlite3

import patterns.creational


def synchronize():
    models = patterns.creational.Model.get_models()
    connect = sqlite3.connect('db.sqlite')
    cursor = connect.cursor()

    for model, cls in models.items():
        command = f"CREATE TABLE IF NOT EXISTS {model.lower()} ({','.join(cls.fields()[1:])})"
        cursor.execute(command)

    command = f"CREATE TABLE IF NOT EXISTS session (session_id INTEGER UNIQUE)"
    cursor.execute(command)

    command = f"CREATE TABLE IF NOT EXISTS  notifications (user_pk INTEGER, text, is_read BOOLEAN)"
    cursor.execute(command)

    command = 'CREATE TABLE IF NOT EXISTS carts (cart JSON)'
    cursor.execute(command)

    connect.commit()


synchronize()
