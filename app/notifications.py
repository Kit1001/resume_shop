import patterns.creational as model
from patterns.system_architecture import dm


def retrieve(user_pk: str) -> list:
    dm.cursor.execute('SELECT rowid, * FROM notifications WHERE user_pk=?', (user_pk,))
    return dm.cursor.fetchall()


def retrieve_unread_number(user_pk: str) -> list:
    dm.cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_pk=? AND is_read=0', (user_pk,))
    return dm.cursor.fetchone()


def mark_as_read(pk: str) -> bool:
    dm.cursor.execute(f"UPDATE notifications SET is_read=1 WHERE rowid=?", (pk,))
    dm.connect.commit()
    return True


def delete_one(pk: str) -> bool:
    dm.cursor.execute(f"DELETE FROM notifications WHERE rowid=?", (pk,))
    dm.connect.commit()
    return True


def notify_all_via_site(text):
    users = model.Model.list(model_name='User')
    users = [user.pk for user in users]
    for user in users:
        dm.cursor.execute('INSERT INTO notifications VALUES(?, ?, 0)', (user, text,))

    dm.connect.commit()
    return True
