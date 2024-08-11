from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from config import TRON_API_KEY, PRIVATE_KEY, SENDER_ADDRESS, USDT_TRC20_CONTRACT

client = Tron(HTTPProvider(api_key=TRON_API_KEY))  # Use mainnet(trongrid) with a single api_key
private_key_tron = PrivateKey(bytes.fromhex(PRIVATE_KEY))

def process_withdrawal(employee_wallet_address: str, amount_in_wei: int):
    contract = client.get_contract(USDT_TRC20_CONTRACT)

    txn = (
        contract.functions.transfer(employee_wallet_address, amount_in_wei)
        .with_owner(SENDER_ADDRESS)
        .fee_limit(20_000_000)
        .build()
        .sign(private_key_tron)
    )
    txn.broadcast().wait()
    return txn.txid
