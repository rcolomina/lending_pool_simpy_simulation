from web3 import Web3
import json

from helpers import print_receipt

# initialize drivers
rpc = 'http://127.0.0.1:8545'
w3 = Web3(Web3.HTTPProvider(rpc))

## add token to the contract
def add_supported_token(token_address,
                        contract_instance,
                        dummy_price_feed="0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec"): ## FAKE address

    tx_hash = contract_instance.functions.addSupportedToken(token_address,
                                                            dummy_price_feed).transact()
    print_receipt(tx_hash, "addSupportedToken")

## build contract object from its abi
def get_contract_instance(path, address):
    #print(path)
    with open(path) as f:
        abi = json.load(f)
        abi = abi["abi"]
        return w3.eth.contract(address=address, abi=abi)


class SetupContracts:
    def __init__(self, owner=None, rpc_url = 'http://127.0.0.1:8545'):
        self.owner = owner

        print(">> SETUP CONTRACTS")
        self.path_to_artifact_contracts = "../artifacts/contracts"

        self.coins = [("ERC20Dai","dai"),
                      ("ERC20RubenCoin","ruben_coin"),
                      ("ERC20AlmanakCoin","almanak_coin")]
                                    
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        assert self.w3.is_connected()
        
        info = self.w3.eth.get_block('latest')
        
        print(f" Latest block timestamp {info['timestamp']}")
        print(f" Latest block number {info['number']}")

        self.path_to_contract_address = "../"

    def _unpause_contract(self,contract_lending_pool):
        ### unpause the contract
        if self.owner is not None:
            tx_hash = contract_lending_pool.functions.setPaused(2).transact({'from':self.owner.address})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        else:
            print("WARNING! unpausing was not doe due to contract's owner was not set")
            
        
    def contract(self, unpause=True):     
        ## Read from file deployed contract address
        contract_lending_pool = None
        with open(self.path_to_contract_address+"deployed_contract_address.txt","r") as f:
            contact_address = f.read()
            #print("Latest Lending Pool Contract Address Deployed:",contact_address)
            path=f"{self.path_to_artifact_contracts}/LendingPool.sol/LendingPool.json"
            contract_lending_pool = get_contract_instance(path,contact_address)

        if unpause:
            self._unpause_contract(contract_lending_pool)

        return contract_lending_pool

    def tokens(self, add_to_contract = True):
        tokens = []    
        for c in self.coins:
            p1, p2 = c[0], c[1]
            contract_token = None

            target_file = self.path_to_contract_address + f"deployed_token_address_{p2}.txt"
            
            with open(target_file,"r") as f:
                token_address = f.read()
                path=f"{self.path_to_artifact_contracts}/mocks/{p1}.sol/{p1}.json"
                contract_token = get_contract_instance(path,token_address)

                if add_to_contract:
                    try:
                        add_supported_token(token_address,self.contract())
                    except Exception as e:
                        print(f"{e} \n This error can be safely ignored")
                    
                tokens.append(contract_token)
                
        return tokens
