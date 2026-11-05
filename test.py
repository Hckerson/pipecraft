try:
    print(1 / 0)
except:
    raise RuntimeError("Something bad happened")