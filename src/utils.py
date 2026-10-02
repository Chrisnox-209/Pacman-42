def convert_wall(nb: int) -> dict[str, int] | None:
    if nb == 0:
        return {"N": 1, "S": 1, "E": 1, "W": 1}
    elif nb == 1:
        return {"N": 0, "S": 1, "E": 1, "W": 1}
    elif nb == 2:
        return {"N": 1, "S": 1, "E": 0, "W": 1}
    elif nb == 3:
        return {"N": 0, "S": 1, "E": 0, "W": 1}
    elif nb == 4:
        return {"N": 1, "S": 0, "E": 1, "W": 1}
    elif nb == 5:
        return {"N": 0, "S": 0, "E": 1, "W": 1}
    elif nb == 6:
        return {"N": 1, "S": 0, "E": 0, "W": 1}
    elif nb == 7:
        return {"N": 0, "S": 0, "E": 0, "W": 1}
    elif nb == 8:
        return {"N": 1, "S": 1, "E": 1, "W": 0}
    elif nb == 9:
        return {"N": 0, "S": 1, "E": 1, "W": 0}
    elif nb == 10:
        return {"N": 1, "S": 1, "E": 0, "W": 0}
    elif nb == 11:
        return {"N": 0, "S": 1, "E": 0, "W": 0}
    elif nb == 12:
        return {"N": 1, "S": 0, "E": 1, "W": 0}
    elif nb == 13:
        return {"N": 0, "S": 0, "E": 1, "W": 0}
    elif nb == 14:
        return {"N": 1, "S": 0, "E": 0, "W": 0}
    elif nb == 15:
        return {"N": 0, "S": 0, "E": 0, "W": 0}
    else:
        return None


def mirror_path(path: str) -> str:
    if path == "N":
        return "S"
    if path == "S":
        return "N"
    if path == "E":
        return "W"
    if path == "W":
        return "E"
    return ""
