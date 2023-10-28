import json

from solcx import (
    compile_standard,
    install_solc,
)


def compile_contract() -> str:
    install_solc('0.8.0')
    with open('src/modules/deploy/contract/contract.sol', 'r') as file:
        contract = file.read()

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"contract.sol": {"content": contract}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.0",
    )

    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)


def get_bytecode() -> str:
    with open('compiled_code.json', 'r') as file:
        compiled_sol = json.load(file)

    bytecode = compiled_sol["contracts"]["contract.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]
    return bytecode


def get_abi() -> str:
    with open('compiled_code.json', 'r') as file:
        compiled_sol = json.load(file)

    abi = json.loads(
        compiled_sol["contracts"]["contract.sol"]["SimpleStorage"]["metadata"]
    )["output"]["abi"]
    return abi
