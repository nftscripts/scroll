from typing import Optional
from sqlalchemy import func

from src.database.models import (
    LiquidityTransaction,
    NFTTransaction,
    SwapTransaction,
    BridgeTransaction,
    DmailTransaction
)


class AnalyticData:
    def __init__(self, session, dex_name: str, wallet_address: str) -> None:
        self.session = session
        self.dex_name = dex_name
        self.wallet_address = wallet_address

    @property
    def interactions_data(self) -> tuple[Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]]:
        with self.session:
            liquidity_result = self.session.query(func.count().label('interactions')).filter(
                LiquidityTransaction.dex_name == self.dex_name,
                LiquidityTransaction.wallet_address == self.wallet_address
            ).first()
            swap_result = self.session.query(func.count().label('interactions')).filter(
                SwapTransaction.dex_name == self.dex_name,
                SwapTransaction.wallet_address == self.wallet_address
            ).first()
            bridge_result = self.session.query(func.count().label('interactions')).filter(
                BridgeTransaction.dex_name == self.dex_name,
                BridgeTransaction.wallet_address == self.wallet_address
            ).first()
            dmail_result = self.session.query(func.count().label('interactions')).filter(
                DmailTransaction.wallet_address == self.wallet_address
            ).first()
            nft_result = self.session.query(func.count().label('interactions')).filter(
                NFTTransaction.nft_name == self.dex_name,
                NFTTransaction.wallet_address == self.wallet_address
            ).first()
            return swap_result[0], liquidity_result[0], bridge_result[0], dmail_result[0], nft_result[0]

    @property
    def volume_data(self) -> tuple[Optional[int], Optional[int], Optional[int]]:
        with self.session:
            swap_volume = self.session.query(func.sum(SwapTransaction.amount).label('total_volume')).filter(
                SwapTransaction.dex_name == self.dex_name,
                SwapTransaction.wallet_address == self.wallet_address
            ).first()
            liquidity_volume = self.session.query(func.sum(LiquidityTransaction.amount).label('total_volume')).filter(
                LiquidityTransaction.dex_name == self.dex_name,
                LiquidityTransaction.wallet_address == self.wallet_address
            ).first()
            bridge_volume = self.session.query(func.sum(BridgeTransaction.amount).label('total_volume')).filter(
                BridgeTransaction.dex_name == self.dex_name,
                BridgeTransaction.wallet_address == self.wallet_address
            ).first()
            return swap_volume[0], liquidity_volume[0], bridge_volume[0]
