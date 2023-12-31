class Chain:
    def __init__(self, chain_id: int, rpc: str, scan: str) -> None:
        self.chain_id = chain_id
        self.rpc = rpc
        self.scan = scan


ETH = Chain(
    chain_id=1,
    rpc='https://rpc.ankr.com/eth',
    scan='https://etherscan.io/tx'
)

BASE = Chain(
    chain_id=8453,
    rpc='https://base.blockpi.network/v1/rpc/public',
    scan='https://basescan.org//tx'
)

ARB = Chain(
    chain_id=42161,
    rpc='https://arb1.arbitrum.io/rpc',
    scan='https://arbiscan.io/tx'
)

ERA = Chain(
    chain_id=324,
    rpc='https://1rpc.io/zksync2-era',
    scan='https://explorer.zksync.io/tx'
)

SCROLL = Chain(
    chain_id=534352,
    rpc='https://rpc.scroll.io',
    scan='https://blockscout.scroll.io/tx'
)

chain_mapping = {
    'base': BASE,
    'eth': ETH,
    'era': ERA,
    'arb': ARB,
    'scroll': SCROLL
}
