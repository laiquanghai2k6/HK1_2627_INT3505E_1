USERS = {
    42: {
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "van.nguyen@example.com",
    },
}


def get_user(uid):
    return USERS.get(uid)
