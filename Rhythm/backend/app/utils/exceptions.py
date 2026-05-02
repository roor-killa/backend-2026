class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InsufficientFundsError(Exception):
    def __init__(self, needed: float, available: float):
        super().__init__(f"Insufficient funds. Need {needed}, have {available}")
        self.needed = needed
        self.available = available


class UserNotFoundError(Exception):
    pass


class InvalidQuantityError(Exception):
    pass


class InsufficientShieldsError(Exception):
    pass
