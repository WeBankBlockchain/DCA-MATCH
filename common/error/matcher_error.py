class MatcherError(ValueError):
    def __init__(self, **kargs):
        self.code = kargs['code']
        self.message = kargs['message']

