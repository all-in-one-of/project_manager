import mari


class ClearCache(object):
    def __init__(self):
        mari.history.clear()
        mari.ddi.garbageCollect()