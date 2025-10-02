from web3 import Web3
from django.conf import settings
from config.models import SiteConfig

BSC_RPC = getattr(settings, "BSC_RPC_URL", "https://bsc-dataseed.binance.org/")
w3 = Web3(Web3.HTTPProvider(BSC_RPC))

# ABI خیلی ساده فقط برای name و symbol
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


def get_token_info(token_address: str):
    contract = w3.eth.contract(
        address=w3.to_checksum_address(token_address), abi=ERC20_ABI
    )
    try:
        name = contract.functions.name().call()
    except:
        name = None
    try:
        symbol = contract.functions.symbol().call()
    except:
        symbol = None
    try:
        decimals = contract.functions.decimals().call()
    except:
        decimals = None
    return {"name": name, "symbol": symbol, "decimals": decimals}


def verify_bsc_tx(tx_hash):
    config = SiteConfig.objects.filter().first()
    token_address = config.payment_token_address
    info = get_token_info(token_address=token_address)

    receipt = w3.eth.get_transaction_receipt(tx_hash)

    # event signature برای Transfer(address,address,uint256)
    TRANSFER_EVENT_SIG = w3.keccak(text="Transfer(address,address,uint256)").hex()
    try:
        for log in receipt["logs"]:
            if (
                log["address"].lower() == token_address.lower()
                and log["topics"][0].hex() == TRANSFER_EVENT_SIG
            ):
                sender = "0x" + log["topics"][1].hex()[-40:]
                recipient = "0x" + log["topics"][2].hex()[-40:]
                amount = int(log["data"].hex(), 16)

                return {
                    "ok": True,
                    "symbol": info["symbol"],
                    "from": sender,
                    "to": recipient,
                    "amount": amount / (10 ** info["decimals"]),
                }
    except Exception:
        return {"ok": False}
