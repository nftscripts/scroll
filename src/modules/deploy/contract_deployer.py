from src.utils.user.account import Account

from src.modules.deploy.utils.data_exctract import (
    get_bytecode,
    get_abi,
    compile_contract,
)


class Deployer(Account):
    def __init__(self, private_key: str, use_0x_bytecode: bool):
        self.use_0x_bytecode = use_0x_bytecode
        super().__init__(private_key)

    def __repr__(self) -> str:
        return f'Deploying contract for address [{self.account_address}]'

    def deploy(self) -> None:
        if not self.use_0x_bytecode:
            compile_contract()
            abi = get_abi()
            bytecode = get_bytecode()
        else:
            abi = self.load_abi('deploy')
            bytecode = '0x'

        contract = self.web3.eth.contract(
            abi=abi,
            bytecode=bytecode
        )

        tx = contract.constructor().build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            'gasPrice': 0,
            'gas': 0
        })
        tx.update({'gasPrice': self.web3.eth.gas_price})
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully deployed contract for address [{self.account_address}] | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )
