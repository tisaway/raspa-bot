from connect import connect

conn = connect()
cur = conn.cursor()

def db_user_exist(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = '%s'" % user_id)
    result = cur.fetchone()
    if result is None:
        return False
    return True

def db_group_exist(group_name):
    group_name = group_name.upper()
    cur.execute("SELECT * FROM groups WHERE group_name = '%s'" % group_name)
    result = cur.fetchone()
    if result is None:
        return False
    return True

def db_insert_new_user(user_id, user_group):
    cur.execute("INSERT INTO users VALUES ('%s', '%s')" % (user_id, user_group))
    conn.commit()
    
# Получает id группы (у каждой группы есть свой id в системе вуза)
def db_get_user_group_id(user_id):
    cur.execute("SELECT g.group_id FROM groups g JOIN users u ON u.user_group = g.group_name AND u.user_id = '%s'" % user_id)
    result = cur.fetchone()
    return result[0]

def db_get_user_group(user_id):
    cur.execute("SELECT user_group FROM users WHERE user_id = '%s'" % user_id)
    result = cur.fetchone()
    return result[0]

def db_set_user_group(user_id, user_group):
    cur.execute("UPDATE users SET user_group = '%s' WHERE user_id = '%s'" % (user_group, user_id))
    conn.commit()

def db_delete_user(user_id):
    cur.execute("DELETE FROM users WHERE user_id='%s'" % user_id)
    conn.commit()

def db_insert_new_group(group_name, group_id):
    cur.execute("INSERT INTO groups VALUES ('%s', '%s') ON CONFLICT (group_name) DO UPDATE SET group_id = '%s'" % (group_name, group_id, group_id))
    conn.commit()