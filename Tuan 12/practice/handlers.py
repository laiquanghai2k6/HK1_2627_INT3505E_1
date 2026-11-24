from uuid import uuid4


def _new_order(account_id):
    return {"order_id": str(uuid4()), "account_id": account_id}


def v1_create_order(body):
    return _new_order(body["account_id"])


def v2_create_order(body):
    return {**_new_order(body["account_id"]), "status": "created"}
