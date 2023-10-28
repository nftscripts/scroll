RANDOMIZE = True
SLIPPAGE = 0.03
MIN_PAUSE = 10
MAX_PAUSE = 20
RETRIES = 3
PAUSE_BETWEEN_RETRIES = 1
CHECK_GWEI = True
MAX_GWEI = 25
USE_DATABASE = True

deploy_contract = True

dmail = False

# --- Bridges --- #
main_bridge = False
owl_bridge = False
orbiter_bridge = False

# --- Swaps --- #
skydrome_swap = False
punk_swap = False
syncswap_swap = False
specefi_swap = False
wrapper = False

swap_all_to_eth = False
random_dex_swap = False

# --- Liquidity --- #
punk_swap_liquidity = False
punk_swap_liquidity_remove = False

spacefi_liquidity = False
spacefi_liquidity_remove = False

syncswap_liquidity = False
syncswap_liquidity_remove = False

skydrome_liquidity = False
skydrome_liquidity_remove = False

# --- NFT --- #
zerius = False

# --- Withdrawals --- #
okx_withdraw = False  # from okx to wallets
okx_deposit = False  # from wallets to okx


class OkxWithdrawConfig:
    """
    OKX => Wallets

    amount: Union[float, List[float]].
    chain: str. ERC20 - Ethereum.
    """

    amount = [0.001, 0.002]
    chain = 'ERC20'


class WithdrawFromWalletsToOKXConfig:
    """
    Wallets => OKX

    amount: Union[float, List[float]].
    from_chain: str. ETH, ERA, etc.
    withdraw_all: bool. True/False.
    keep_value: Union[float, List[float]]. ETH value to keep on your wallet if withdraw_all = True.
    """
    amount = [0.001, 0.002]
    from_chain = 'ARB'
    withdraw_all = True
    keep_value = [0.005, 0.007]


class MainBridgeConfig:
    """
    action: str. deposit/withdraw.
    amount: Union[float, List[float]]. Value to bridge. You can use float or list. e.g. amount = 0.5 (will bridge 0.5 ETH)
    or amount = [0.5, 0.6] (will randomly take a number between 0.5 and 0.6)

    use_percentage: bool. Use True if you want to use a percentage of the balance instead of numbers.

    bridge_percentage: Union[float, List[float]]. Value as a percentage of balance to bridge.
    You can use float or list. e.g. bridge_percentage = 0.5 (will bridge 50% of your ETH balance)
    or bridge_percentage = [0.5, 0.6] (will randomly take a number between 50% and 60%)

    """
    action = 'withdraw'
    amount = [0.1, 0.2]
    use_percentage = True
    bridge_percentage = [0.5, 0.5]
    claim_eth = False  # True is only if you withdraw from Scroll to ETH (need to wait for ~40 minutes after bridge)


class OrbiterBridgeConfig:
    """
    chains: eth, arb, op, era, base, scroll

    action: deposit/withdraw
    """
    action = 'deposit'

    from_chain = 'ARB'
    to_chain = 'SCROLL'
    amount = [0.05, 0.06]
    use_percentage = False
    bridge_percentage = [0.5, 0.5]


class OwlBridgeConfig:
    """
    """
    action = 'deposit'

    from_chain = 'SCROLL'
    to_chain = 'ARB'
    amount = 0.004
    use_percentage = False
    bridge_percentage = [0.5, 0.5]


class SwapAllTokensConfig:
    tokens_list = ['USDT', 'USDC', 'PUNK']
    to_token = 'ETH'


class RandomDexSwapConfig:
    from_token = 'ETH'
    to_token = ['USDT', 'USDC']
    amount = [0.001, 0.0015]
    num_swaps = 2


class SyncSwapSwapConfig:
    """
    from_token: str.
    to_token: str | list[str]. If to_token = ['USDC', 'USDT'] it will randomly take USDT or USDC.
    """

    from_token = 'ETH'
    to_token = ['USDC', 'USDT']
    amount = 0.001
    use_percentage = False
    swap_percentage = 0.5
    swap_all_balance = True


# --- Swaps --- #
class SkyDromeSwapConfig:
    from_token = 'WETH'
    to_token = 'USDC'
    amount = 0.0024
    use_percentage = False
    swap_percentage = 0.5
    swap_all_balance = False


class SpaceFiSwapConfig:
    from_token = 'ETH'
    to_token = 'USDT'
    amount = 0.002
    use_percentage = False
    swap_percentage = 0.5
    swap_all_balance = True


class PunkSwapConfig:
    from_token = 'USDC'
    to_token = 'ETH'
    amount = [0.0009, 0.0011]
    use_percentage = False
    swap_percentage = 0.1
    swap_all_balance = True


class WrapperConfig:
    """
    action: str. Wrap/Unwrap.
    amount: Union[float, List[float]].
    use_all_balance: bool. True is only for action = Unwrap.
    use_percentage: bool. True/False.
    percentage_to_wrap: Union[List[float], float].
    """

    action = 'unwrap'
    amount = [0.001, 0.002]
    use_all_balance = True
    use_percentage = False
    percentage_to_wrap = [0.1, 0.4]


class PunkSwapLiquidityConfig:
    token = 'USDC'
    token2 = 'USDT'
    amount = [1, 1]
    use_percentage = False
    liquidity_percentage = 0.01


class SpaceFiLiquidityConfig:
    token = 'USDC'
    token2 = 'USDT'
    amount = [1, 1]
    use_percentage = False
    liquidity_percentage = 0.01


class SyncSwapLiquidityConfig:
    token = 'ETH'
    token2 = 'USDC'
    amount = [0.001, 0.001]
    use_percentage = False
    liquidity_percentage = 0.01


class SyncSwapLiquidityRemoveConfig:
    token = 'ETH'
    token2 = 'USDC'
    removing_percentage = 0.5
    remove_all = True


class PunkSwapLiquidityRemoveConfig:
    token = 'USDC'
    token2 = 'USDT'
    removing_percentage = 0.5
    remove_all = True


class SpaceFiLiquidityRemoveConfig:
    token = 'USDC'
    token2 = 'USDT'
    removing_percentage = 0.5
    remove_all = True


class SkyDromeLiquidityConfig:
    token = 'ETH'
    token2 = 'USDC'
    amount = [0.001, 0.001]
    use_percentage = False
    liquidity_percentage = 0.01


class SkyDromeLiquidityRemoveConfig:
    token = 'USDC'
    token2 = 'USDT'
    removing_percentage = 0.5
    remove_all = True


class DmailConfig:
    num_transactions = 1


class ZeruisConfig:
    """
    chain_to_bridge: Union[str, List[str]]: ['ARB', 'OP', 'POLYGON', 'BSC', 'AVAX']
    """
    chain_to_bridge = ['ARB', 'OP', 'POLYGON', 'BSC', 'AVAX']


class DeployerConfig:
    use_0x_bytecode = True
