import requests
from config import API_KEY, API_BASE


def number_lookup(number: str) -> dict:
    """Look up a mobile number."""
    url = f"{API_BASE}/number"
    params = {"key": API_KEY, "num": number}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()


def aadhar_lookup(aadhar_num: str) -> dict:
    """Look up Aadhar details."""
    url = f"{API_BASE}/aadhar"
    params = {"key": API_KEY, "num": aadhar_num}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()


def freefire_lookup(uid: str) -> dict:
    """Look up Free Fire player info."""
    url = f"{API_BASE}/ff"
    params = {"key": API_KEY, "uid": uid}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()


def bgmi_lookup(uid: str) -> dict:
    """Look up BGMI player info."""
    url = f"{API_BASE}/bgmi"
    params = {"key": API_KEY, "uid": uid}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()


def aadhar_family(aadhar_num: str) -> dict:
    """Look up family members from Aadhar."""
    url = f"{API_BASE}/adharfamily"
    params = {"key": API_KEY, "num": aadhar_num}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()


def snapchat_lookup(username: str) -> dict:
    """Look up Snapchat user info."""
    url = f"{API_BASE}/snap"
    params = {"key": API_KEY, "username": username}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()
