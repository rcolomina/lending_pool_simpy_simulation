
class TokenWrapper:
    def __init__(self, token):
        self.contract_token = token
        self.address = token.address
        self.name = token.functions.name().call()
        self.decimals = token.functions.decimals().call()
        
    def __str__(self):
        return f"name:{self.name} | address: {self.address} | decimals: {self.decimals}"

    def total_supply(self):
        pass
        
    def get_balance_of_user(self, user, weis=True):
        factor = 10 ** self.decimals if weis else 1
        return self.contract_token.functions.balanceOf(user.address).call() // 10 ** self.decimals
        
    def transfer_from_to(self, origin_user, destiny_user, units_to_transfer):
        print(f"Transfering {units_to_transfer} units of the token '{self.name}'",
              f"from user '{origin_user.name}' to user '{destiny_user.name}'")
        
        amount_to_transfer = units_to_transfer * (10 ** self.decimals)

        tx_hash = self.contract_token.functions.transfer(destiny_user.address,
                                                   amount_to_transfer).transact({'from': origin_user.address})
