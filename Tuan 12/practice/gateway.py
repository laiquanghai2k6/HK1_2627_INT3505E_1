import hashlib

from handlers import v1_create_order, v2_create_order

V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}


def route_to_v2(account, cohort, v2_percent):
    if cohort.lower() in V2_COHORTS:
        return True
    if account in V2_FORCE_ACCOUNTS:
        return True

    digest = hashlib.md5(account.encode("utf-8"), usedforsecurity=False)
    bucket = int(digest.hexdigest(), 16) % 100
    return bucket < v2_percent


def dispatch(body, cohort, v2_percent):
    if route_to_v2(body["account_id"], cohort, v2_percent):
        return "v2", v2_create_order(body)
    return "v1", v1_create_order(body)

