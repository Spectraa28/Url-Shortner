class InvalidAliasError(Exception):
    """Exception raised when the Alias is invalid"""

    def __init__(self, message="Only Alphabets and Numbers are allowed"):
        self.message = message
        super().__init__(message)


class AlreadyExistsError(Exception):
    """Exception raised when the Alias is already in the database"""

    def __init__(self, message="This url already exists. Try Different One"):
        self.message = message
        super().__init__(message)


class ShortUrlNotFoundError(Exception):
    """Exception raised when the short code doesn't exist in the database"""

    def __init__(self, message="This url doesn't exist. Try different one"):
        self.message = message
        super().__init__(message)


class UrlExpiredError(Exception):
    """Exception raised when the shortcode is expired"""

    def __init__(self, message="This url is expired. Try Different One"):
        self.message = message
        super().__init__(message)
