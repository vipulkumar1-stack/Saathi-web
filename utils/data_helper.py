import random
import string
import os
from config.config import LEAD_DATA, MOVE_TO_LOGIN_DATA, MOVE_TO_SANCTION_DATA, MOVE_TO_DISBURSE_DATA, ADD_TEAMMATE_DATA, ADD_SOURCING_PARTNER_DATA, CHECK_OFFERS_DATA, ROLE_DATA

_FIRST_NAMES = ["Arjun", "Rahul", "Priya", "Amit", "Neha", "Vikram", "Sunita", "Rohit", "Kavya", "Arun"]
_LAST_NAMES  = ["Sharma", "Gupta", "Singh", "Kumar", "Verma", "Patel", "Nair", "Joshi", "Mehta", "Rao"]


def generate_mobile() -> str:
    prefix = random.choice(["6", "7", "8", "9"])
    rest = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return prefix + rest


def generate_id(length: int = 8) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def generate_login_id() -> str:
    """Login ID for Move-to-Login must match the bank's LAN format, fetched
    live via the get_lan_format API for ICICI Bank (the bank hardcoded in
    MOVE_TO_LOGIN_DATA): 4 alphanumeric + 4 letters + 10 letters, e.g.
    'A1B2abcdabcdefghij'. A plain random alphanumeric string is rejected with
    "Invalid Login ID format"."""
    part1 = "".join(random.choices(string.ascii_letters + string.digits, k=4))
    part2 = "".join(random.choices(string.ascii_letters, k=4))
    part3 = "".join(random.choices(string.ascii_letters, k=10))
    return part1 + part2 + part3


def generate_lead_data() -> dict:
    return {
        **LEAD_DATA,
        "first_name": os.getenv("LEAD_FIRST_NAME") or random.choice(_FIRST_NAMES),
        "last_name":  os.getenv("LEAD_LAST_NAME")  or random.choice(_LAST_NAMES),
        "mobile":     generate_mobile(),
    }


def generate_login_data() -> dict:
    """Return MOVE_TO_LOGIN_DATA with a fresh login ID."""
    return {**MOVE_TO_LOGIN_DATA, "login_id": generate_login_id()}


def generate_sanction_id() -> str:
    """Sanction ID must match the bank's LAN format, same rule as Login ID
    (fetched live via get_lan_format for ICICI Bank, the bank hardcoded in
    MOVE_TO_SANCTION_DATA): 4 alphanumeric + 4 letters + 10 letters, e.g.
    'A1B2abcdabcdefghij'. Confirmed live on 2026-08-18: a plain random
    alphanumeric string (the previous generate_id() default) is rejected with
    "Invalid Sanction ID format. Please check and try again."""
    return generate_login_id()


def generate_sanction_data() -> dict:
    """Return MOVE_TO_SANCTION_DATA with a fresh, LAN-format sanction ID."""
    return {**MOVE_TO_SANCTION_DATA, "sanction_id": generate_sanction_id()}


def generate_disburse_data() -> dict:
    """Return MOVE_TO_DISBURSE_DATA with a fresh disbursed ID."""
    return {**MOVE_TO_DISBURSE_DATA, "disbursed_id": generate_id()}


def generate_email() -> str:
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@testmail.com"


def generate_teammate_data() -> dict:
    """Return ADD_TEAMMATE_DATA with a fresh random name and mobile."""
    return {
        **ADD_TEAMMATE_DATA,
        "full_name": os.getenv("TEAMMATE_FULL_NAME") or f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}",
        "mobile":    generate_mobile(),
    }


def generate_role_data() -> dict:
    """Return ROLE_DATA with a unique role name to prevent name-conflict errors on each run."""
    return {
        **ROLE_DATA,
        "name": os.getenv("ROLE_NAME") or f"Role_{generate_id(6)}",
    }


def generate_check_offers_data() -> dict:
    """Return CHECK_OFFERS_DATA for the per-lead Loan Offer Calculator.
    The redesigned tool runs against an existing lead and creates no new lead,
    so no random personal details are needed — the data is returned as-is."""
    return {**CHECK_OFFERS_DATA}


def generate_sourcing_partner_data() -> dict:
    """Return ADD_SOURCING_PARTNER_DATA with a fresh random name, mobile, and email."""
    return {
        **ADD_SOURCING_PARTNER_DATA,
        "full_name": os.getenv("SOURCING_PARTNER_FULL_NAME") or f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}",
        "mobile":    generate_mobile(),
        "email":     generate_email(),
    }
