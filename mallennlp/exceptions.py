class Error(Exception):
    pass


class NotInProjectError(Error):
    def __init__(self):
        super().__init__(
            "You are not in a project directory or you're Project.toml config file is missing"
        )


class CudaUnavailableError(Error):
    pass


class InvalidPageParametersError(Error):
    pass


class NotPermittedError(Error):
    pass
