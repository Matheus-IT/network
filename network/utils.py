def doesThisUserLikeThisPost(user, post):
    for like in post['likes']:
        if user.id == like['liker_id']:
            return True
    return False