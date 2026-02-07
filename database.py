import time

USERS = {}

TRIAL_SECONDS = 86400  # 1 day
SUB_SECONDS = 2592000  # 30 days

def give_trial(user_id):
    if user_id not in USERS:
        USERS[user_id] = time.time() + TRIAL_SECONDS

def has_access(user_id):
    return user_id in USERS and USERS[user_id] > time.time()

def give_subscription(user_id):
    USERS[user_id] = time.time() + SUB_SECONDS
