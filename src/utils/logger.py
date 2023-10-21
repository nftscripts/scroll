import loguru


class Logger:
    def __init__(self, logger: loguru.logger) -> None:
        self.__logger = logger

    def info(self, __message: str, *args: object, **kwargs: object) -> None:
        self.__logger.info(f'{__message}', *args, **kwargs)

    def debug(self, __message: str, *args: object, **kwargs: object) -> None:
        self.__logger.debug(f'{__message}', *args, **kwargs)

    def error(self, __message: str, *args: object, **kwargs: object) -> None:
        self.__logger.error(f'{__message}', *args, **kwargs)

    def success(self, __message: str, *args: object, **kwargs: object) -> None:
        self.__logger.success(f'{__message}', *args, **kwargs)

    def warning(self, __message: str, *args: object, **kwargs: object) -> None:
        self.__logger.warning(f'{__message}', *args, **kwargs)
