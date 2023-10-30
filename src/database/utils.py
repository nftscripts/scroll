from asyncio import sleep
import types

from typing import (
    Optional,
    Type,
)

from sqlalchemy.orm import sessionmaker
from loguru import logger

from eth_typing import (
    Address,
    HexStr,
)

from src.database.data.analytics_data import AnalyticData

from src.database.models import (
    LiquidityTransaction,
    LendingTransaction,
    BridgeTransaction,
    DmailTransaction,
    SwapTransaction,
    NFTTransaction,
    Analytics,
    engine,
)


class DataBaseUtils:
    SWAP_ACTION: str = 'swap'
    LIQUIDITY_ACTION: str = 'liquidity'
    MINT_ACTION: str = 'mint'
    BRIDGE_ACTION: str = 'bridge'
    DMAIL_ACTION: str = 'dmail'
    LENDING_ACTION: str = 'lending'

    def __init__(self, action: str) -> None:
        self.__action = action
        self.__session = sessionmaker(bind=engine)()

        if self.__action == self.SWAP_ACTION:
            self.__table_object = SwapTransaction
        elif self.__action == self.LIQUIDITY_ACTION:
            self.__table_object = LiquidityTransaction
        elif self.__action == self.MINT_ACTION:
            self.__table_object = NFTTransaction
        elif self.__action == self.BRIDGE_ACTION:
            self.__table_object = BridgeTransaction
        elif self.__action == self.DMAIL_ACTION:
            self.__table_object = DmailTransaction
        elif self.__action == self.LENDING_ACTION:
            self.__table_object = LendingTransaction
        else:
            raise ValueError()

    def __enter__(self) -> None:
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_value: Optional[BaseException],
                 traceback: Optional[types.TracebackType]) -> None:
        self.__session.close()

    async def add_to_db(self, wallet_address: Address, tx_hash: HexStr, dex_name: str, amount: Optional[float] = None,
                        from_token: Optional[str] = None, to_token: Optional[str] = None) -> None:
        transaction = self.__table_object(
            wallet_address=wallet_address,
            tx_hash=tx_hash,
        )

        if self.__action == self.SWAP_ACTION:
            transaction.dex_name = dex_name
            transaction.from_token = from_token
            transaction.to_token = to_token
            transaction.amount = amount
        elif self.__action == self.LIQUIDITY_ACTION:
            transaction.token = from_token
            transaction.token2 = to_token
            transaction.dex_name = dex_name
            transaction.amount = amount
        elif self.__action == self.MINT_ACTION:
            transaction.nft_name = dex_name
        elif self.__action == self.BRIDGE_ACTION:
            transaction.dex_name = dex_name
            transaction.token = 'ETH'
            transaction.amount = amount
        elif self.__action == self.DMAIL_ACTION:
            transaction.dex_name = dex_name
        elif self.__action == self.LENDING_ACTION:
            transaction.dex_name = dex_name
            transaction.amount = amount

        self.__session.add(transaction)
        self.__session.commit()
        self.__session.close()
        logger.success('✔️ | Successfully added to DataBase')
        await sleep(3)
        logger.debug('🔄 | Updating «analytics» table...')
        await sleep(3)
        self._update_analytics(dex_name, wallet_address)
        logger.success('🆕 | Information successfully updated')

    def _update_analytics(self, dex_name: str, wallet_address: Address) -> None:
        analytic_data = AnalyticData(self.__session, dex_name, wallet_address)
        swap_interactions, liquidity_interactions, bridge_interactions, \
            dmail_interactions, nft_interactions, lending_interactions = analytic_data.interactions_data
        swap_volume, liquidity_volume, bridge_volume, lending_volume = analytic_data.volume_data
        interactions = \
            liquidity_interactions + swap_interactions + bridge_interactions + dmail_interactions + nft_interactions \
            + lending_interactions

        if swap_volume is None:
            swap_volume = 0
        if liquidity_volume is None:
            liquidity_volume = 0
        if bridge_volume is None:
            bridge_volume = 0
        if lending_volume is None:
            lending_volume = 0

        total_volume = swap_volume + liquidity_volume + bridge_volume + lending_volume

        analytics_entry = self.__session.query(Analytics).filter_by(dex_name=dex_name,
                                                                    wallet_address=wallet_address).first()
        if analytics_entry:
            analytics_entry.interactions = interactions
            analytics_entry.total_volume = total_volume
        else:
            unique_id = str(hash(wallet_address) + hash(dex_name))
            analytics_entry = Analytics(id=unique_id, wallet_address=wallet_address, dex_name=dex_name,
                                        interactions=interactions, total_volume=total_volume)
            self.__session.add(analytics_entry)

        self.__session.commit()
