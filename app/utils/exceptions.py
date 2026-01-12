class ConflictError(Exception):
    pass

class CheckConstraintError(Exception):
    pass

class EmptyPayloadError(Exception):
    pass

class NotFoundError(Exception):
    pass