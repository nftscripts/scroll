from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    create_engine,
    Sequence,
    Integer,
    Column,
    String,
    Float,
)

Base = declarative_base()


class BridgeTransaction(Base):
    __tablename__ = 'bridge_transactions'
    id = Column(Integer, Sequence('bridge_transaction_id_seq'), primary_key=True)
    wallet_address = Column(String)
    tx_hash = Column(String)
    dex_name = Column(String)
    token = Column(String)
    amount = Column(Float)


class SwapTransaction(Base):
    __tablename__ = 'swap_transactions'
    id = Column(Integer, Sequence('swap_transaction_id_seq'), primary_key=True)
    wallet_address = Column(String)
    tx_hash = Column(String)
    dex_name = Column(String)
    from_token = Column(String)
    to_token = Column(String)
    amount = Column(Float)


class LiquidityTransaction(Base):
    __tablename__ = 'liquidity_transactions'
    id = Column(Integer, Sequence('liquidity_transaction_id_seq'), primary_key=True)
    wallet_address = Column(String)
    tx_hash = Column(String)
    dex_name = Column(String)
    token = Column(String)
    token2 = Column(String)
    amount = Column(Float)


class NFTTransaction(Base):
    __tablename__ = 'nft_transactions'
    id = Column(Integer, Sequence('nft_transaction_id_seq'), primary_key=True)
    nft_name = Column(String)
    wallet_address = Column(String)
    tx_hash = Column(String)
    amount = Column(Float)


class DmailTransaction(Base):
    __tablename__ = 'dmail_transactions'
    id = Column(Integer, Sequence('dmail_transaction_id_seq'), primary_key=True)
    wallet_address = Column(String)
    tx_hash = Column(String)
    dex_name = Column(String)


class Analytics(Base):
    __tablename__ = 'analytics'
    id = Column(String, primary_key=True)
    wallet_address = Column(String)
    dex_name = Column(String)
    interactions = Column(Integer, default=0)
    total_volume = Column(Float)


engine = create_engine('sqlite:///transactions.db')
Base.metadata.create_all(engine)
