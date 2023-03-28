
def interval_to_seconds(interval):
    unit = interval[-1]
    value = int(interval[:-1])
    if unit == "m":
        return value * 60
    elif unit == "h":
        return value * 60 * 60
    elif unit == "d":
        return value * 60 * 60 * 24
    else:
        raise ValueError("Invalid interval format")
