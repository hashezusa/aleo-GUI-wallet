import os
import json
import time
import base64
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from wallet_core import AleoWalletCore

class AddressBookManager:
    """
    Manages the address book functionality for the Aleo wallet.
    Handles storing, retrieving, and managing contact information.
    """
    
    def __init__(self, wallet_core: AleoWalletCore):
        """
        Initialize the Address Book Manager.
        
        Args:
            wallet_core: The wallet core instance
        """
        self.wallet_core = wallet_core
        
    def add_contact(self, account_index: int, name: str, address: str, description: str = "") -> bool:
        """
        Add a new contact to an account's address book.
        
        Args:
            account_index: Index of the account
            name: Name of the contact
            address: Aleo address of the contact
            description: Optional description
            
        Returns:
            True if successful, False otherwise
        """
        # Validate the address
        if not self.wallet_core.validate_address(address):
            raise ValueError("Invalid Aleo address format")
            
        # Create the contact object
        contact = {
            "name": name,
            "address": address,
            "description": description,
            "created_at": int(time.time()),
            "last_used": 0
        }
        
        # Add the contact to the account's contact list
        return self.wallet_core.add_contact(account_index, contact)
    
    def update_contact(self, account_index: int, contact_index: int, updates: Dict[str, Any]) -> bool:
        """
        Update an existing contact.
        
        Args:
            account_index: Index of the account
            contact_index: Index of the contact to update
            updates: Dictionary of values to update
            
        Returns:
            True if successful, False otherwise
        """
        # Get the account
        account = self.wallet_core.get_account(account_index)
        if not account:
            return False
            
        # Get the contacts list
        contacts = account.get("contacts", [])
        
        # Check if the contact exists
        if contact_index < 0 or contact_index >= len(contacts):
            return False
            
        # Update the contact
        for key, value in updates.items():
            # Don't allow updating the address directly
            if key != "address":
                contacts[contact_index][key] = value
                
        # Save the wallet
        self.wallet_core.save_wallet()
        
        return True
    
    def remove_contact(self, account_index: int, contact_index: int) -> bool:
        """
        Remove a contact from the address book.
        
        Args:
            account_index: Index of the account
            contact_index: Index of the contact to remove
            
        Returns:
            True if successful, False otherwise
        """
        return self.wallet_core.remove_contact(account_index, contact_index)
    
    def get_contacts(self, account_index: int) -> List[Dict[str, Any]]:
        """
        Get all contacts for an account.
        
        Args:
            account_index: Index of the account
            
        Returns:
            List of contacts
        """
        return self.wallet_core.get_contacts(account_index)
    
    def get_contact(self, account_index: int, contact_index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific contact by index.
        
        Args:
            account_index: Index of the account
            contact_index: Index of the contact
            
        Returns:
            Contact object or None if not found
        """
        contacts = self.wallet_core.get_contacts(account_index)
        if 0 <= contact_index < len(contacts):
            return contacts[contact_index]
        return None
    
    def get_contact_by_address(self, account_index: int, address: str) -> Optional[Dict[str, Any]]:
        """
        Find a contact by address.
        
        Args:
            account_index: Index of the account
            address: Address to search for
            
        Returns:
            Contact object or None if not found
        """
        contacts = self.wallet_core.get_contacts(account_index)
        for contact in contacts:
            if contact["address"] == address:
                return contact
        return None
    
    def get_contact_by_name(self, account_index: int, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a contact by name.
        
        Args:
            account_index: Index of the account
            name: Name to search for
            
        Returns:
            Contact object or None if not found
        """
        contacts = self.wallet_core.get_contacts(account_index)
        for contact in contacts:
            if contact["name"].lower() == name.lower():
                return contact
        return None
    
    def update_last_used(self, account_index: int, contact_index: int) -> bool:
        """
        Update the last used timestamp for a contact.
        
        Args:
            account_index: Index of the account
            contact_index: Index of the contact
            
        Returns:
            True if successful, False otherwise
        """
        return self.update_contact(account_index, contact_index, {"last_used": int(time.time())})
    
    def search_contacts(self, account_index: int, query: str) -> List[Dict[str, Any]]:
        """
        Search contacts by name or address.
        
        Args:
            account_index: Index of the account
            query: Search query
            
        Returns:
            List of matching contacts
        """
        contacts = self.wallet_core.get_contacts(account_index)
        query = query.lower()
        
        results = []
        for contact in contacts:
            if query in contact["name"].lower() or query in contact["address"].lower():
                results.append(contact)
                
        return results
    
    def import_contacts(self, account_index: int, contacts_data: str) -> int:
        """
        Import contacts from a JSON string.
        
        Args:
            account_index: Index of the account
            contacts_data: JSON string containing contacts
            
        Returns:
            Number of contacts imported
        """
        try:
            contacts = json.loads(contacts_data)
            if not isinstance(contacts, list):
                raise ValueError("Invalid contacts data format")
                
            count = 0
            for contact in contacts:
                if isinstance(contact, dict) and "name" in contact and "address" in contact:
                    if self.add_contact(
                        account_index,
                        contact["name"],
                        contact["address"],
                        contact.get("description", "")
                    ):
                        count += 1
                        
            return count
        except Exception as e:
            print(f"Error importing contacts: {e}")
            return 0
    
    def export_contacts(self, account_index: int) -> str:
        """
        Export contacts as a JSON string.
        
        Args:
            account_index: Index of the account
            
        Returns:
            JSON string containing contacts
        """
        contacts = self.wallet_core.get_contacts(account_index)
        return json.dumps(contacts, indent=2)


class KeyManager:
    """
    Manages cryptographic keys for the Aleo wallet.
    Handles key generation, derivation, and secure storage.
    """
    
    def __init__(self, wallet_core: AleoWalletCore):
        """
        Initialize the Key Manager.
        
        Args:
            wallet_core: The wallet core instance
        """
        self.wallet_core = wallet_core
        
    def generate_new_key_pair(self) -> Dict[str, str]:
        """
        Generate a new Aleo key pair.
        
        Returns:
            Dictionary containing private key, view key, and address
        """
        # In a real implementation, we would use Aleo's SDK to generate these keys
        # For now, we'll simulate it with placeholder values
        
        # Generate a random seed
        import secrets
        seed = secrets.token_bytes(32)
        
        # Derive a private key (this is a placeholder implementation)
        private_key = "APrivateKey1" + base64.b64encode(seed).decode('utf-8')[:52]
        
        # Derive a view key (this is a placeholder implementation)
        view_key_seed = hashlib.sha256(seed).digest()
        view_key = "AViewKey1" + base64.b64encode(view_key_seed).decode('utf-8')[:46]
        
        # Derive an address (this is a placeholder implementation)
        address_seed = hashlib.sha256(view_key_seed).digest()
        address = "aleo1" + base64.b64encode(address_seed).decode('utf-8')[:58]
        
        return {
            "private_key": private_key,
            "view_key": view_key,
            "address": address
        }
    
    def derive_view_key_from_private_key(self, private_key: str) -> str:
        """
        Derive a view key from a private key.
        
        Args:
            private_key: The private key
            
        Returns:
            The derived view key
        """
        # In a real implementation, we would use Aleo's SDK to derive the view key
        # For now, we'll simulate it
        
        # Extract the seed from the private key (this is a placeholder implementation)
        seed_b64 = private_key[len("APrivateKey1"):]
        try:
            seed = base64.b64decode(seed_b64 + "==")  # Add padding if needed
        except:
            seed = hashlib.sha256(private_key.encode()).digest()
        
        # Derive a view key (this is a placeholder implementation)
        view_key_seed = hashlib.sha256(seed).digest()
        view_key = "AViewKey1" + base64.b64encode(view_key_seed).decode('utf-8')[:46]
        
        return view_key
    
    def derive_address_from_view_key(self, view_key: str) -> str:
        """
        Derive an address from a view key.
        
        Args:
            view_key: The view key
            
        Returns:
            The derived address
        """
        # In a real implementation, we would use Aleo's SDK to derive the address
        # For now, we'll simulate it
        
        # Extract the seed from the view key (this is a placeholder implementation)
        seed_b64 = view_key[len("AViewKey1"):]
        try:
            seed = base64.b64decode(seed_b64 + "==")  # Add padding if needed
        except:
            seed = hashlib.sha256(view_key.encode()).digest()
        
        # Derive an address (this is a placeholder implementation)
        address_seed = hashlib.sha256(seed).digest()
        address = "aleo1" + base64.b64encode(address_seed).decode('utf-8')[:58]
        
        return address
    
    def validate_private_key(self, private_key: str) -> bool:
        """
        Validate a private key format.
        
        Args:
            private_key: The private key to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - in a real implementation, we would do more thorough validation
        return private_key.startswith("APrivateKey1") and len(private_key) >= 59
    
    def validate_view_key(self, view_key: str) -> bool:
        """
        Validate a view key format.
        
        Args:
            view_key: The view key to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - in a real implementation, we would do more thorough validation
        return view_key.startswith("AViewKey1") and len(view_key) >= 53
    
    def export_private_key(self, account_index: int, password: str = None) -> str:
        """
        Export a private key, optionally encrypted with a password.
        
        Args:
            account_index: Index of the account
            password: Optional password for encryption
            
        Returns:
            The exported private key
        """
        private_key = self.wallet_core.export_private_key(account_index)
        if not private_key:
            raise ValueError("Account not found")
            
        if password:
            # In a real implementation, we would encrypt the private key with the password
            # For now, we'll just simulate it
            return f"ENCRYPTED:{private_key}"
        else:
            return private_key
    
    def export_view_key(self, account_index: int) -> str:
        """
        Export a view key.
        
        Args:
            account_index: Index of the account
            
        Returns:
            The exported view key
        """
        view_key = self.wallet_core.export_view_key(account_index)
        if not view_key:
            raise ValueError("Account not found")
            
        return view_key
    
    def import_private_key(self, private_key: str, name: str = None, password: str = None) -> Dict[str, Any]:
        """
        Import an account from a private key.
        
        Args:
            private_key: The private key to import
            name: Optional name for the account
            password: Optional password if the private key is encrypted
            
        Returns:
            The imported account
        """
        # Check if the private key is encrypted
        if private_key.startswith("ENCRYPTED:") and password:
            # In a real implementation, we would decrypt the private key with the password
            # For now, we'll just simulate it
            private_key = private_key[len("ENCRYPTED:"):]
            
        # Validate the private key
        if not self.validate_private_key(private_key):
            raise ValueError("Invalid private key format")
            
        # Import the account
        return self.wallet_core.import_account_from_private_key(private_key, name)
    
    def create_backup(self, account_indices: List[int], password: str) -> str:
        """
        Create an encrypted backup of selected accounts.
        
        Args:
            account_indices: Indices of accounts to backup
            password: Password to encrypt the backup
            
        Returns:
            Encrypted backup data
        """
        # Get the accounts to backup
        accounts = []
        for index in account_indices:
            account = self.wallet_core.get_account(index)
            if account:
                accounts.append(account)
                
        if not accounts:
            raise ValueError("No valid accounts selected for backup")
            
        # Create the backup data
        backup_data = {
            "version": "1.0",
            "timestamp": int(time.time()),
            "accounts": accounts
        }
        
        # Convert to JSON
        json_data = json.dumps(backup_data)
        
        # In a real implementation, we would encrypt the data with the password
        # For now, we'll just simulate it
        encrypted_data = f"ENCRYPTED:{json_data}"
        
        return encrypted_data
    
    def restore_from_backup(self, backup_data: str, password: str) -> int:
        """
        Restore accounts from an encrypted backup.
        
        Args:
            backup_data: Encrypted backup data
            password: Password to decrypt the backup
            
        Returns:
            Number of accounts restored
        """
        # Check if the backup data is encrypted
        if not backup_data.startswith("ENCRYPTED:"):
            raise ValueError("Invalid backup data format")
            
        # In a real implementation, we would decrypt the data with the password
        # For now, we'll just simulate it
        json_data = backup_data[len("ENCRYPTED:"):]
        
        try:
            # Parse the backup data
            backup = json.loads(json_data)
            
            # Validate the backup format
            if not isinstance(backup, dict) or "accounts" not in backup or not isinstance(backup["accounts"], list):
                raise ValueError("Invalid backup data format")
                
            # Import each account
            count = 0
            for account_data in backup["accounts"]:
                if "private_key" in account_data:
                    self.wallet_core.import_account_from_private_key(
                        account_data["private_key"],
                        account_data.get("name")
                    )
                    count += 1
                    
            return count
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            raise ValueError(f"Failed to restore from backup: {e}")


# Example usage
if __name__ == "__main__":
    # Create a wallet core
    wallet_core = AleoWalletCore()
    
    # Generate a test account
    account = wallet_core.generate_account("Test Account")
    
    # Create an address book manager
    address_book = AddressBookManager(wallet_core)
    
    # Add some contacts
    address_book.add_contact(0, "Alice", "aleo1alice", "Friend")
    address_book.add_contact(0, "Bob", "aleo1bob", "Colleague")
    
    # Get all contacts
    contacts = address_book.get_contacts(0)
    print(f"Contacts: {json.dumps(contacts, indent=2)}")
    
    # Create a key manager
    key_manager = KeyManager(wallet_core)
    
    # Generate a new key pair
    key_pair = key_manager.generate_new_key_pair()
    print(f"Generated key pair: {json.dumps(key_pair, indent=2)}")
    
    # Export a private key
    private_key = key_manager.export_private_key(0)
    print(f"Exported private key: {private_key}")
    
    # Create a backup
    backup = key_manager.create_backup([0], "password123")
    print(f"Created backup: {backup[:50]}...")
