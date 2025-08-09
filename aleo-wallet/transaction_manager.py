import time
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
from wallet_core import AleoWalletCore
from aleo_api import AleoBlockchainAPI, AleoWalletAPI

class TransactionManager:
    """
    Manages transaction creation, signing, and submission for the Aleo wallet.
    Also handles transaction history and status tracking.
    """
    
    def __init__(self, wallet_core: AleoWalletCore, blockchain_api: AleoBlockchainAPI = None):
        """
        Initialize the Transaction Manager.
        
        Args:
            wallet_core: The wallet core instance
            blockchain_api: Optional blockchain API instance
        """
        self.wallet_core = wallet_core
        self.blockchain_api = blockchain_api or AleoBlockchainAPI()
        self.wallet_api = AleoWalletAPI(self.blockchain_api)
        
        # Transaction fee settings
        self.default_fee = 0.001  # Default fee in ALEO
        self.min_fee = 0.0001    # Minimum fee in ALEO
        self.fee_per_byte = 0.00001  # Fee per byte of transaction data
        
        # Transaction status codes
        self.STATUS_PENDING = "Pending"
        self.STATUS_CONFIRMED = "Confirmed"
        self.STATUS_FAILED = "Failed"
        
    def create_transaction(self, 
                          account_index: int, 
                          recipient_address: str, 
                          amount: float, 
                          memo: str = "") -> Dict[str, Any]:
        """
        Create a new transaction.
        
        Args:
            account_index: Index of the sender account
            recipient_address: Recipient's address
            amount: Amount to send
            memo: Optional memo/message
            
        Returns:
            Transaction object
        """
        # Validate inputs
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
            
        if not self.wallet_core.validate_address(recipient_address):
            raise ValueError("Invalid recipient address")
            
        # Get the sender account
        account = self.wallet_core.get_account(account_index)
        if not account:
            raise ValueError("Account not found")
            
        # Check if the account has sufficient balance
        balance = self.wallet_core.get_balance(account_index)
        fee = self.calculate_fee(amount, memo)
        
        if balance < amount + fee:
            raise ValueError(f"Insufficient balance. Need {amount + fee} ALEO but have {balance} ALEO")
            
        # Create the transaction object
        transaction = {
            "type": "Sent",
            "sender": account["address"],
            "recipient": recipient_address,
            "amount": amount,
            "fee": fee,
            "memo": memo,
            "timestamp": int(time.time()),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.STATUS_PENDING,
            "transaction_id": "",  # Will be filled after submission
            "block_height": 0      # Will be filled after confirmation
        }
        
        return transaction
    
    def sign_transaction(self, account_index: int, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a transaction with the account's private key.
        
        Args:
            account_index: Index of the signer account
            transaction: Transaction to sign
            
        Returns:
            Signed transaction
        """
        # Get the account
        account = self.wallet_core.get_account(account_index)
        if not account:
            raise ValueError("Account not found")
            
        # In a real implementation, we would use the account's private key to sign the transaction
        # For now, we'll just simulate it
        
        # Add a signature field
        transaction["signature"] = f"sig_{int(time.time())}"
        
        return transaction
    
    def broadcast_transaction(self, account_index: int, transaction: Dict[str, Any]) -> str:
        """
        Broadcast a signed transaction to the network.
        
        Args:
            account_index: Index of the sender account
            transaction: Signed transaction to broadcast
            
        Returns:
            Transaction ID
        """
        # In a real implementation, we would use the blockchain API to broadcast the transaction
        # For now, we'll simulate it
        
        # Generate a transaction ID
        transaction_id = f"at{int(time.time())}"
        
        # Update the transaction with the ID
        transaction["transaction_id"] = transaction_id
        
        # Add the transaction to the account's history
        self.wallet_core.add_transaction(account_index, transaction)
        
        # Start monitoring the transaction status
        self.start_monitoring_transaction(account_index, transaction_id)
        
        return transaction_id
    
    def start_monitoring_transaction(self, account_index: int, transaction_id: str) -> None:
        """
        Start monitoring a transaction for confirmation.
        
        Args:
            account_index: Index of the sender account
            transaction_id: ID of the transaction to monitor
        """
        # In a real implementation, we would start a background task to monitor the transaction
        # For now, we'll simulate it with a delayed confirmation
        
        import threading
        
        def monitor():
            # Wait for a few seconds to simulate network delay
            time.sleep(5)
            
            # Simulate confirmation
            self.update_transaction_status(account_index, transaction_id, self.STATUS_CONFIRMED)
            
            # Simulate adding to a block
            transactions = self.wallet_core.get_transactions(account_index)
            for i, tx in enumerate(transactions):
                if tx.get("transaction_id") == transaction_id:
                    # Get the latest block height
                    try:
                        latest_height = self.blockchain_api.get_latest_height()
                    except:
                        latest_height = 100000  # Fallback value
                        
                    # Update the transaction with the block height
                    tx["block_height"] = latest_height
                    self.wallet_core.accounts[account_index]["transactions"][i] = tx
                    self.wallet_core.save_wallet()
                    break
        
        # Start the monitoring thread
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_transaction_status(self, account_index: int, transaction_id: str, status: str) -> bool:
        """
        Update the status of a transaction.
        
        Args:
            account_index: Index of the account
            transaction_id: ID of the transaction to update
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        transactions = self.wallet_core.get_transactions(account_index)
        for i, tx in enumerate(transactions):
            if tx.get("transaction_id") == transaction_id:
                tx["status"] = status
                self.wallet_core.accounts[account_index]["transactions"][i] = tx
                self.wallet_core.save_wallet()
                return True
        return False
    
    def get_transaction(self, account_index: int, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a transaction by ID.
        
        Args:
            account_index: Index of the account
            transaction_id: ID of the transaction to get
            
        Returns:
            Transaction object or None if not found
        """
        transactions = self.wallet_core.get_transactions(account_index)
        for tx in transactions:
            if tx.get("transaction_id") == transaction_id:
                return tx
        return None
    
    def calculate_fee(self, amount: float, memo: str = "") -> float:
        """
        Calculate the transaction fee based on the amount and memo.
        
        Args:
            amount: Transaction amount
            memo: Optional memo/message
            
        Returns:
            Calculated fee
        """
        # In a real implementation, we would calculate the fee based on the transaction size
        # For now, we'll use a simple formula
        
        # Base fee
        fee = self.default_fee
        
        # Add fee for memo if present
        if memo:
            fee += len(memo) * self.fee_per_byte
            
        # Ensure minimum fee
        fee = max(fee, self.min_fee)
        
        return fee
    
    def receive_transaction(self, account_index: int, sender_address: str, amount: float, transaction_id: str = None) -> Dict[str, Any]:
        """
        Record a received transaction.
        
        Args:
            account_index: Index of the recipient account
            sender_address: Sender's address
            amount: Amount received
            transaction_id: Optional transaction ID
            
        Returns:
            Transaction object
        """
        # Generate a transaction ID if not provided
        if not transaction_id:
            transaction_id = f"at{int(time.time())}"
            
        # Create the transaction object
        transaction = {
            "type": "Received",
            "sender": sender_address,
            "recipient": self.wallet_core.get_account(account_index)["address"],
            "amount": amount,
            "fee": 0,  # No fee for receiving
            "memo": "",
            "timestamp": int(time.time()),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.STATUS_CONFIRMED,
            "transaction_id": transaction_id,
            "block_height": 0  # Will be updated later
        }
        
        # Add the transaction to the account's history
        self.wallet_core.add_transaction(account_index, transaction)
        
        return transaction
    
    def get_transaction_history(self, account_index: int, limit: int = None, filter_type: str = None) -> List[Dict[str, Any]]:
        """
        Get the transaction history for an account.
        
        Args:
            account_index: Index of the account
            limit: Optional limit on the number of transactions to return
            filter_type: Optional filter by transaction type
            
        Returns:
            List of transactions
        """
        return self.wallet_core.get_transactions(account_index, limit, filter_type)
    
    def sync_transactions_with_blockchain(self, account_index: int) -> int:
        """
        Sync the account's transactions with the blockchain.
        
        Args:
            account_index: Index of the account
            
        Returns:
            Number of new transactions found
        """
        # In a real implementation, we would query the blockchain for new transactions
        # For now, we'll simulate it
        
        # Get the account
        account = self.wallet_core.get_account(account_index)
        if not account:
            return 0
            
        # Get the latest block height
        try:
            latest_height = self.blockchain_api.get_latest_height()
        except:
            return 0
            
        # Simulate finding new transactions
        import random
        if random.random() < 0.3:  # 30% chance of finding a new transaction
            # Simulate a received transaction
            amount = random.uniform(0.1, 5.0)
            sender = f"aleo1{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=58))}"
            
            self.receive_transaction(account_index, sender, amount)
            return 1
            
        return 0
    
    def estimate_transaction_time(self, fee: float) -> int:
        """
        Estimate the confirmation time for a transaction based on the fee.
        
        Args:
            fee: Transaction fee
            
        Returns:
            Estimated time in minutes
        """
        # In a real implementation, we would estimate based on network conditions
        # For now, we'll use a simple formula
        
        if fee >= self.default_fee * 2:
            return 1  # 1 minute for high fees
        elif fee >= self.default_fee:
            return 5  # 5 minutes for normal fees
        else:
            return 15  # 15 minutes for low fees
    
    def send_transaction(self, account_index: int, recipient_address: str, amount: float, memo: str = "") -> str:
        """
        Create, sign, and broadcast a transaction in one step.
        
        Args:
            account_index: Index of the sender account
            recipient_address: Recipient's address
            amount: Amount to send
            memo: Optional memo/message
            
        Returns:
            Transaction ID
        """
        # Create the transaction
        transaction = self.create_transaction(account_index, recipient_address, amount, memo)
        
        # Sign the transaction
        signed_transaction = self.sign_transaction(account_index, transaction)
        
        # Broadcast the transaction
        transaction_id = self.broadcast_transaction(account_index, signed_transaction)
        
        return transaction_id


# Example usage
if __name__ == "__main__":
    # Create a wallet core
    wallet_core = AleoWalletCore()
    
    # Generate a test account
    account = wallet_core.generate_account("Test Account")
    
    # Add some initial balance for testing
    wallet_core.accounts[0]["balance"] = 100.0
    
    # Create a transaction manager
    tx_manager = TransactionManager(wallet_core)
    
    # Send a transaction
    try:
        tx_id = tx_manager.send_transaction(0, "aleo1abcdef", 10.0, "Test transaction")
        print(f"Transaction sent with ID: {tx_id}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Get transaction history
    time.sleep(6)  # Wait for the simulated confirmation
    history = tx_manager.get_transaction_history(0)
    print(f"Transaction history: {json.dumps(history, indent=2)}")
    
    # Check balance after transaction
    balance = wallet_core.get_balance(0)
    print(f"Balance after transaction: {balance} ALEO")
