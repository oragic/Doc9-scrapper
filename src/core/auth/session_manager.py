def cookies_to_dict(cookies):
    return {c["name"]: c["value"] for c in cookies}