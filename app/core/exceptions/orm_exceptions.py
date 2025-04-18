class ForeignKeyViolationException(Exception):
    pass


class UniqueConstraintViolationException(Exception):
    pass


class NoEntityFoundException(Exception):
    pass
