import time

users = {}

def give_trial(user_id):
    users[user_id] = time.time() + 86400  # 24 часа

def has_access(user_id):
    return user_id in users and users[user_id] > time.time()

def give_subscription(user_id):
    users[user_id] = time.time() + 30 * 86400
