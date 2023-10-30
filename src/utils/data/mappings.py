from src.utils.runner import *

module_handlers = {
    'main_bridge': process_main_bridge,
    'owl_bridge': process_owl_bridge,
    'orbiter_bridge': process_orbiter_bridge,
    'skydrome_swap': process_skydrome_swap,
    'skydrome_liquidity': process_skydrome_liquidity,
    'skydrome_liquidity_remove': process_skydrome_liquidity_remove,
    'specefi_swap': process_spacefi_swap,
    'spacefi_liquidity': process_spacefi_liquidity,
    'spacefi_liquidity_remove': process_spacefi_liquidity_remove,
    'punk_swap': process_punk_swap,
    'punk_swap_liquidity': process_punk_swap_liquidity,
    'punk_swap_liquidity_remove': process_punk_swap_liquidity_remove,
    'syncswap_swap': process_sync_swap_swap,
    'syncswap_liquidity': process_sync_swap_liquidity,
    'syncswap_liquidity_remove': process_sync_swap_liquidity_remove,
    'swap_all_to_eth': process_swap_all_to_eth,
    'random_dex_swap': process_random_dex_swap,
    'wrapper': process_wrapper,
    'okx_withdraw': process_okx_withdrawal,
    'okx_deposit': process_okx_deposit,
    'dmail': process_dmail,
    'zerius': process_zerius_mint_bridge,
    'deploy_contract': process_deploy,
    'layerbank_deposit': process_layerbank_deposit,
    'layerbank_withdraw': process_layerbank_withdraw
}
