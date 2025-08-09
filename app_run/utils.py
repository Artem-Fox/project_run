def check_weight(weight):
    if weight.isdigit():
        if 0 < int(weight) < 900:
            return True
        else:
            return False

    return False
