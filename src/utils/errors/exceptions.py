from typing import Any

from config import SLIPPAGE


class CustomError(Exception):
    def __init__(self, error_type: str, error_message: str) -> None:
        self.error = f'{error_type}: {error_message}'
        super().__init__(self.error)


class ErrorHandler:
    def __init__(self, ex: Exception, *args: Any) -> None:
        self.__ex = ex
        self.__name = args[0]

    def handle(self) -> CustomError:
        if 'execution reverted' in str(self.__ex) and 'MainBridge' in str(self.__name):
            error_type = 'NotEnoughMoneyError'
            error_message = 'Not enough money for MainBridge transaction'
        elif 'execution reverted' in str(self.__ex) and 'PunkSwap' in str(self.__name):
            error_type = 'PriceImpactTooHigh'
            error_message = f"Can't execute transaction with slippage {SLIPPAGE * 100}%"

        else:
            error_type = 'Unknown Error'
            error_message = str(self.__ex)

        return CustomError(error_type=error_type, error_message=error_message)
