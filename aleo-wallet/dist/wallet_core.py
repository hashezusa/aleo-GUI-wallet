import os
import json
import time
import hashlib
import base64
import secrets
from typing import Dict, Any, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AleoWalletCore:
    """
    Core functionality for the Aleo wallet, handling account management,
    encryption, and storage.
    """
    
    def __init__(self, wallet_file: str = "aleo_wallet.dat"):
        """
        Initialize the Aleo Wallet Core.
        
        Args:
            wallet_file: Path to the wallet data file
        """
        self.wallet_file = wallet_file
        self.accounts = []
        self.is_encrypted = False
        self.encryption_key = None
        
        # Load wallet if it exists
        self.load_wallet()
    
    def generate_account(self, name: str = None) -> Dict[str, Any]:
        """
        Generate a new Aleo account.
        
        Args:
            name: Optional name for the account
            
        Returns:
            A dictionary containing the account details
        """
        # In a real implementation, we would use Aleo's SDK to generate these keys
        # For now, we'll simulate it with placeholder values
        
        # Generate a random seed
        seed = secrets.token_bytes(32)
        
        # Derive a private key (this is a placeholder implementation)
        private_key = "APrivateKey1" + base64.b64encode(seed).decode('utf-8')[:52]
        
        # Derive a view key (this is a placeholder implementation)
        view_key_seed = hashlib.sha256(seed).digest()
        view_key = "AViewKey1" + base64.b64encode(view_key_seed).decode('utf-8')[:46]
        
        # Derive an address (this is a placeholder implementation)
        address_seed = hashlib.sha256(view_key_seed).digest()
        address = "aleo1" + base64.b64encode(address_seed).decode('utf-8')[:58]
        
        # Create the account object
        account = {
            "name": name or f"Account {len(self.accounts) + 1}",
            "private_key": private_key,
            "view_key": view_key,
            "address": address,
            "created_at": int(time.time()),
            "balance": 0.0,
            "transactions": [],
            "contacts": []
        }
        
        # Add the account to our list
        self.accounts.append(account)
        
        # Save the wallet
        self.save_wallet()
        
        return account
    
    def import_account_from_private_key(self, private_key: str, name: str = None) -> Dict[str, Any]:
        """
        Import an account from a private key.
        
        Args:
            private_key: The private key to import
            name: Optional name for the account
            
        Returns:
            A dictionary containing the account details
        """
        # Validate the private key format
        if not private_key.startswith("APrivateKey1"):
            raise ValueError("Invalid private key format. Must start with 'APrivateKey1'.")
        
        # In a real implementation, we would derive the view key and address from the private key
        # For now, we'll simulate it with placeholder values
        
        # Extract the seed from the private key (this is a placeholder implementation)
        seed_b64 = private_key[len("APrivateKey1"):]
        try:
            seed = base64.b64decode(seed_b64 + "==")  # Add padding if needed
        except:
            seed = hashlib.sha256(private_key.encode()).digest()
        
        # Derive a view key (this is a placeholder implementation)
        view_key_seed = hashlib.sha256(seed).digest()
        view_key = "AViewKey1" + base64.b64encode(view_key_seed).decode('utf-8')[:46]
        
        # Derive an address (this is a placeholder implementation)
        address_seed = hashlib.sha256(view_key_seed).digest()
        address = "aleo1" + base64.b64encode(address_seed).decode('utf-8')[:58]
        
        # Create the account object
        account = {
            "name": name or f"Imported Account {len(self.accounts) + 1}",
            "private_key": private_key,
            "view_key": view_key,
            "address": address,
            "created_at": int(time.time()),
            "balance": 0.0,
            "transactions": [],
            "contacts": []
        }
        
        # Add the account to our list
        self.accounts.append(account)
        
        # Save the wallet
        self.save_wallet()
        
        return account
    
    def get_account(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get an account by index.
        
        Args:
            index: The index of the account to get
            
        Returns:
            The account dictionary or None if not found
        """
        if 0 <= index < len(self.accounts):
            return self.accounts[index]
        return None
    
    def get_account_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get an account by address.
        
        Args:
            address: The address of the account to get
            
        Returns:
            The account dictionary or None if not found
        """
        for account in self.accounts:
            if account["address"] == address:
                return account
        return None
    
    def update_account(self, index: int, updates: Dict[str, Any]) -> bool:
        """
        Update an account with new values.
        
        Args:
            index: The index of the account to update
            updates: Dictionary of values to update
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.accounts):
            # Don't allow updating private key or address directly
            safe_updates = {k: v for k, v in updates.items() 
                          if k not in ["private_key", "address"]}
            
            self.accounts[index].update(safe_updates)
            self.save_wallet()
            return True
        return False
    
    def delete_account(self, index: int) -> bool:
        """
        Delete an account by index.
        
        Args:
            index: The index of the account to delete
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.accounts):
            del self.accounts[index]
            self.save_wallet()
            return True
        return False
    
    def add_transaction(self, account_index: int, transaction: Dict[str, Any]) -> bool:
        """
        Add a transaction to an account's history.
        
        Args:
            account_index: The index of the account
            transaction: The transaction details
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= account_index < len(self.accounts):
            # Add timestamp if not present
            if "timestamp" not in transaction:
                transaction["timestamp"] = int(time.time())
            
            # Add the transaction to the account's history
            self.accounts[account_index]["transactions"].insert(0, transaction)
            
            # Update the account balance
            if transaction["type"] == "Sent":
                self.accounts[account_index]["balance"] -= (transaction["amount"] + transaction.get("fee", 0))
            elif transaction["type"] == "Received":
                self.accounts[account_index]["balance"] += transaction["amount"]
            
            self.save_wallet()
            return True
        return False
    
    def add_contact(self, account_index: int, contact: Dict[str, Any]) -> bool:
        """
        Add a contact to an account's contact list.
        
        Args:
            account_index: The index of the account
            contact: The contact details
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= account_index < len(self.accounts):
            # Validate the contact address
            if not contact.get("address", "").startswith("aleo1"):
                return False
            
            # Add the contact to the account's contact list
            self.accounts[account_index]["contacts"].append(contact)
            
            self.save_wallet()
            return True
        return False
    
    def remove_contact(self, account_index: int, contact_index: int) -> bool:
        """
        Remove a contact from an account's contact list.
        
        Args:
            account_index: The index of the account
            contact_index: The index of the contact to remove
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= account_index < len(self.accounts):
            contacts = self.accounts[account_index].get("contacts", [])
            if 0 <= contact_index < len(contacts):
                del contacts[contact_index]
                self.save_wallet()
                return True
        return False
    
    def encrypt_wallet(self, password: str) -> bool:
        """
        Encrypt the wallet with a password.
        
        Args:
            password: The password to encrypt with
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate a salt
            salt = os.urandom(16)
            
            # Derive a key from the password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Create a Fernet cipher
            cipher = Fernet(key)
            
            # Store the encryption key and salt
            self.encryption_key = key
            self.salt = salt
            self.is_encrypted = True
            
            # Save the wallet (which will now be encrypted)
            self.save_wallet()
            
            return True
        except Exception as e:
            print(f"Error encrypting wallet: {e}")
            return False
    
    def decrypt_wallet(self, password: str) -> bool:
        """
        Decrypt the wallet with a password.
        
        Args:
            password: The password to decrypt with
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the encrypted wallet data
            if not os.path.exists(self.wallet_file):
                return False
            
            with open(self.wallet_file, "rb") as f:
                encrypted_data = f.read()
            
            # Extract the salt and encrypted content
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # Derive the key from the password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Create a Fernet cipher
            cipher = Fernet(key)
            
            # Decrypt the data
            decrypted_data = cipher.decrypt(encrypted_content)
            wallet_data = json.loads(decrypted_data.decode())
            
            # Update the wallet state
            self.accounts = wallet_data.get("accounts", [])
            self.encryption_key = key
            self.salt = salt
            self.is_encrypted = True
            
            return True
        except Exception as e:
            print(f"Error decrypting wallet: {e}")
            return False
    
    def disable_encryption(self) -> bool:
        """
        Disable encryption for the wallet.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_encrypted:
            return True
        
        try:
            self.is_encrypted = False
            self.encryption_key = None
            self.salt = None
            
            # Save the wallet (which will now be unencrypted)
            self.save_wallet()
            
            return True
        except Exception as e:
            print(f"Error disabling encryption: {e}")
            return False
    
    def save_wallet(self) -> bool:
        """
        Save the wallet to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare the wallet data
            wallet_data = {
                "accounts": self.accounts,
                "version": "1.0"
            }
            
            # Convert to JSON
            json_data = json.dumps(wallet_data)
            
            # Encrypt if necessary
            if self.is_encrypted and self.encryption_key:
                cipher = Fernet(self.encryption_key)
                encrypted_data = cipher.encrypt(json_data.encode())
                
                # Write the salt and encrypted data
                with open(self.wallet_file, "wb") as f:
                    f.write(self.salt)
                    f.write(encrypted_data)
            else:
                # Write unencrypted data
                with open(self.wallet_file, "w") as f:
                    f.write(json_data)
            
            return True
        except Exception as e:
            print(f"Error saving wallet: {e}")
            return False
    
    def load_wallet(self) -> bool:
        """
        Load the wallet from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.wallet_file):
                return False
            
            # Check if the file is encrypted
            with open(self.wallet_file, "rb") as f:
                data = f.read()
            
            try:
                # Try to parse as JSON (unencrypted)
                wallet_data = json.loads(data.decode())
                self.accounts = wallet_data.get("accounts", [])
                self.is_encrypted = False
                return True
            except:
                # File is likely encrypted
                self.is_encrypted = True
                # We'll need the password to decrypt it
                return False
            
        except Exception as e:
            print(f"Error loading wallet: {e}")
            return False
    
    def backup_wallet(self, backup_path: str) -> bool:
        """
        Backup the wallet to a file.
        
        Args:
            backup_path: The path to save the backup to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If the wallet is encrypted, we need to save it in its encrypted form
            if self.is_encrypted and self.encryption_key:
                # Just copy the encrypted file
                with open(self.wallet_file, "rb") as src, open(backup_path, "wb") as dst:
                    dst.write(src.read())
            else:
                # Prepare the wallet data
                wallet_data = {
                    "accounts": self.accounts,
                    "version": "1.0"
                }
                
                # Convert to JSON and save
                with open(backup_path, "w") as f:
                    json.dump(wallet_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error backing up wallet: {e}")
            return False
    
    def restore_wallet(self, backup_path: str, password: str = None) -> bool:
        """
        Restore the wallet from a backup file.
        
        Args:
            backup_path: The path to the backup file
            password: Optional password if the backup is encrypted
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            # Read the backup file
            with open(backup_path, "rb") as f:
                data = f.read()
            
            try:
                # Try to parse as JSON (unencrypted)
                wallet_data = json.loads(data.decode())
                self.accounts = wallet_data.get("accounts", [])
                self.is_encrypted = False
                self.save_wallet()
                return True
            except:
                # File is likely encrypted
                if not password:
                    return False
                
                # Extract the salt and encrypted content
                salt = data[:16]
                encrypted_content = data[16:]
                
                # Derive the key from the password
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
                
                # Create a Fernet cipher
                cipher = Fernet(key)
                
                # Decrypt the data
                decrypted_data = cipher.decrypt(encrypted_content)
                wallet_data = json.loads(decrypted_data.decode())
                
                # Update the wallet state
                self.accounts = wallet_data.get("accounts", [])
                self.encryption_key = key
                self.salt = salt
                self.is_encrypted = True
                
                # Save the wallet
                self.save_wallet()
                
                return True
            
        except Exception as e:
            print(f"Error restoring wallet: {e}")
            return False
    
    def export_private_key(self, account_index: int) -> Optional[str]:
        """
        Export the private key for an account.
        
        Args:
            account_index: The index of the account
            
        Returns:
            The private key or None if not found
        """
        if 0 <= account_index < len(self.accounts):
            return self.accounts[account_index]["private_key"]
        return None
    
    def export_view_key(self, account_index: int) -> Optional[str]:
        """
        Export the view key for an account.
        
        Args:
            account_index: The index of the account
            
        Returns:
            The view key or None if not found
        """
        if 0 <= account_index < len(self.accounts):
            return self.accounts[account_index]["view_key"]
        return None
    
    def get_balance(self, account_index: int) -> float:
        """
        Get the balance for an account.
        
        Args:
            account_index: The index of the account
            
        Returns:
            The account balance
        """
        if 0 <= account_index < len(self.accounts):
            return self.accounts[account_index].get("balance", 0.0)
        return 0.0
    
    def get_transactions(self, account_index: int, limit: int = None, filter_type: str = None) -> List[Dict[str, Any]]:
        """
        Get transactions for an account.
        
        Args:
            account_index: The index of the account
            limit: Optional limit on the number of transactions to return
            filter_type: Optional filter by transaction type
            
        Returns:
            A list of transactions
        """
        if 0 <= account_index < len(self.accounts):
            transactions = self.accounts[account_index].get("transactions", [])
            
            # Apply filter if specified
            if filter_type:
                transactions = [tx for tx in transactions if tx.get("type") == filter_type]
            
            # Apply limit if specified
            if limit is not None:
                transactions = transactions[:limit]
            
            return transactions
        return []
    
    def get_contacts(self, account_index: int) -> List[Dict[str, Any]]:
        """
        Get contacts for an account.
        
        Args:
            account_index: The index of the account
            
        Returns:
            A list of contacts
        """
        if 0 <= account_index < len(self.accounts):
            return self.accounts[account_index].get("contacts", [])
        return []
    
    def validate_address(self, address: str) -> bool:
        """
        Validate an Aleo address format.
        
        Args:
            address: The address to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - in a real implementation, we would do more thorough validation
        return address.startswith("aleo1") and len(address) >= 60


# Example usage
if __name__ == "__main__":
    # Create a new wallet
    wallet = AleoWalletCore()
    
    # Generate a new account
    account = wallet.generate_account("My First Account")
    print(f"Generated account: {account['address']}")
    
    # Add a transaction
    wallet.add_transaction(0, {
        "type": "Received",
        "address": "aleo1abc...",
        "amount": 10.0,
        "timestamp": int(time.time()),
        "status": "Confirmed"
    })
    
    # Get the balance
    balance = wallet.get_balance(0)
    print(f"Balance: {balance} ALEO")
    
    # Get transactions
    transactions = wallet.get_transactions(0)
    print(f"Transactions: {len(transactions)}")
    
    # Encrypt the wallet
    wallet.encrypt_wallet("my_secure_password")
    print("Wallet encrypted")
    
    # Save and reload
    wallet.save_wallet()
    new_wallet = AleoWalletCore()
    if new_wallet.is_encrypted:
        success = new_wallet.decrypt_wallet("my_secure_password")
        print(f"Decryption successful: {success}")
        if success:
            print(f"Loaded account: {new_wallet.accounts[0]['address']}")
