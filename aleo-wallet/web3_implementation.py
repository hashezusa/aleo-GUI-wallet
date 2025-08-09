import json
import requests
import threading
import time
from typing import Dict, Any, List, Optional, Callable

class AleoWeb3Provider:
    """
    Web3 provider for Aleo blockchain integration.
    Handles RPC connections, transaction signing, and dApp interactions.
    """
    
    def __init__(self, rpc_endpoint: str = "https://api.aleo.network/v1"):
        """
        Initialize the Web3 provider with the specified RPC endpoint.
        
        Args:
            rpc_endpoint: The URL of the Aleo RPC endpoint
        """
        self.rpc_endpoint = rpc_endpoint
        self.connected = False
        self.request_id = 1
        self.connected_dapps = {}
        self.permissions = {}
        self.event_listeners = {}
        self.connection_status_callbacks = []
        
        # Start connection monitoring
        self._start_connection_monitor()
    
    def _start_connection_monitor(self):
        """Start a background thread to monitor the RPC connection."""
        def monitor():
            while True:
                try:
                    # Check connection by getting latest height
                    response = self.call_method("latest/height", [])
                    if response and "result" in response:
                        if not self.connected:
                            self.connected = True
                            self._notify_connection_status(True)
                    else:
                        if self.connected:
                            self.connected = False
                            self._notify_connection_status(False)
                except Exception:
                    if self.connected:
                        self.connected = False
                        self._notify_connection_status(False)
                
                # Sleep for 30 seconds before checking again
                time.sleep(30)
        
        # Start the monitor thread
        threading.Thread(target=monitor, daemon=True).start()
    
    def _notify_connection_status(self, status: bool):
        """Notify all registered callbacks about connection status changes."""
        for callback in self.connection_status_callbacks:
            try:
                callback(status)
            except Exception as e:
                print(f"Error in connection status callback: {e}")
    
    def register_connection_callback(self, callback: Callable[[bool], None]):
        """
        Register a callback to be notified of connection status changes.
        
        Args:
            callback: Function to call with boolean connection status
        """
        self.connection_status_callbacks.append(callback)
    
    def set_rpc_endpoint(self, endpoint: str) -> bool:
        """
        Change the RPC endpoint.
        
        Args:
            endpoint: New RPC endpoint URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            old_endpoint = self.rpc_endpoint
            self.rpc_endpoint = endpoint
            
            # Test the connection
            response = self.call_method("latest/height", [])
            if response and "result" in response:
                return True
            else:
                # Revert to old endpoint if the new one doesn't work
                self.rpc_endpoint = old_endpoint
                return False
        except Exception:
            # Revert to old endpoint on error
            self.rpc_endpoint = old_endpoint
            return False
    
    def call_method(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """
        Call an RPC method on the Aleo blockchain.
        
        Args:
            method: The RPC method name
            params: List of parameters for the method
            
        Returns:
            Dict containing the response from the RPC endpoint
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params
            }
            self.request_id += 1
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.rpc_endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"HTTP error: {response.text}"
                    }
                }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def get_latest_height(self) -> int:
        """
        Get the latest block height from the blockchain.
        
        Returns:
            int: The latest block height, or -1 on error
        """
        response = self.call_method("latest/height", [])
        if response and "result" in response:
            return response["result"]
        return -1
    
    def get_latest_block(self) -> Dict[str, Any]:
        """
        Get the latest block details.
        
        Returns:
            Dict containing the latest block information
        """
        response = self.call_method("latest/block", [])
        if response and "result" in response:
            return response["result"]
        return {}
    
    def get_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Get details of a specific transaction.
        
        Args:
            tx_id: The transaction ID
            
        Returns:
            Dict containing transaction details
        """
        response = self.call_method("transaction", [tx_id])
        if response and "result" in response:
            return response["result"]
        return {}
    
    def get_transactions_for_address(self, address: str, start_height: int, end_height: int) -> List[str]:
        """
        Get public transactions for a specific address within a block range.
        
        Args:
            address: The Aleo address
            start_height: Starting block height
            end_height: Ending block height
            
        Returns:
            List of transaction IDs
        """
        response = self.call_method("getPublicTransactionsForAddress", [address, start_height, end_height])
        if response and "result" in response:
            return response["result"]
        return []
    
    def get_program(self, program_id: str) -> str:
        """
        Get the source code of a program.
        
        Args:
            program_id: The program ID
            
        Returns:
            String containing the program source code
        """
        response = self.call_method("program", [program_id])
        if response and "result" in response:
            return response["result"]
        return ""
    
    def get_mapping_value(self, program_id: str, mapping_name: str, key: str) -> Any:
        """
        Get the value of a mapping at a specific key.
        
        Args:
            program_id: The program ID
            mapping_name: The name of the mapping
            key: The key to look up
            
        Returns:
            The value at the specified key
        """
        response = self.call_method("getMappingValue", [program_id, mapping_name, key])
        if response and "result" in response:
            return response["result"]
        return None
    
    def get_public_nfts_for_address(self, address: str) -> List[Dict[str, Any]]:
        """
        Get public NFTs associated with an address.
        
        Args:
            address: The Aleo address
            
        Returns:
            List of NFT details
        """
        response = self.call_method("getPublicNFTsForAddress", [address])
        if response and "result" in response:
            return response["result"]
        return []
    
    def get_token_programs_for_address(self, address: str) -> List[str]:
        """
        Get token programs an address has interacted with.
        
        Args:
            address: The Aleo address
            
        Returns:
            List of token program IDs
        """
        response = self.call_method("getPublicTokenProgramsForAddress", [address])
        if response and "result" in response:
            return response["result"]
        return []
    
    def generate_transaction(self, authorization: Dict[str, Any], inputs: List[Any]) -> str:
        """
        Generate a transaction by delegating proof generation.
        
        Args:
            authorization: Authorization data
            inputs: Transaction inputs
            
        Returns:
            Transaction ID or error message
        """
        response = self.call_method("generateTransaction", [authorization, inputs])
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            return f"Error: {response['error']['message']}"
        return "Unknown error generating transaction"
    
    # dApp connection management
    
    def connect_dapp(self, dapp_url: str, dapp_name: str, requested_permissions: List[str]) -> Dict[str, Any]:
        """
        Handle a connection request from a dApp.
        
        Args:
            dapp_url: The URL of the dApp
            dapp_name: The name of the dApp
            requested_permissions: List of permissions requested by the dApp
            
        Returns:
            Dict with connection status and details
        """
        # Generate a unique connection ID
        import uuid
        connection_id = str(uuid.uuid4())
        
        # Store connection information
        self.connected_dapps[connection_id] = {
            "url": dapp_url,
            "name": dapp_name,
            "connected_at": time.time(),
            "last_active": time.time()
        }
        
        # Store granted permissions (all requested permissions are granted for now)
        # In a real implementation, this would involve user confirmation
        self.permissions[connection_id] = requested_permissions
        
        return {
            "success": True,
            "connection_id": connection_id,
            "granted_permissions": requested_permissions
        }
    
    def disconnect_dapp(self, connection_id: str) -> bool:
        """
        Disconnect a dApp.
        
        Args:
            connection_id: The connection ID to disconnect
            
        Returns:
            bool: True if successful, False otherwise
        """
        if connection_id in self.connected_dapps:
            del self.connected_dapps[connection_id]
            
        if connection_id in self.permissions:
            del self.permissions[connection_id]
            
        return True
    
    def check_permission(self, connection_id: str, permission: str) -> bool:
        """
        Check if a dApp has a specific permission.
        
        Args:
            connection_id: The connection ID
            permission: The permission to check
            
        Returns:
            bool: True if the dApp has the permission, False otherwise
        """
        if connection_id not in self.permissions:
            return False
            
        return permission in self.permissions[connection_id]
    
    def handle_dapp_request(self, connection_id: str, request_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request from a connected dApp.
        
        Args:
            connection_id: The connection ID
            request_type: The type of request
            request_data: The request data
            
        Returns:
            Dict with the response
        """
        # Check if the dApp is connected
        if connection_id not in self.connected_dapps:
            return {
                "success": False,
                "error": "Not connected"
            }
            
        # Update last active timestamp
        self.connected_dapps[connection_id]["last_active"] = time.time()
        
        # Handle different request types
        if request_type == "get_accounts":
            # Check permission
            if not self.check_permission(connection_id, "view_accounts"):
                return {
                    "success": False,
                    "error": "Permission denied"
                }
                
            # This would return actual accounts in a real implementation
            return {
                "success": True,
                "accounts": ["aleo1..."]
            }
            
        elif request_type == "sign_transaction":
            # Check permission
            if not self.check_permission(connection_id, "sign_transactions"):
                return {
                    "success": False,
                    "error": "Permission denied"
                }
                
            # This would handle actual transaction signing in a real implementation
            # For now, just return a mock response
            return {
                "success": True,
                "transaction_id": "at1..."
            }
            
        else:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type}"
            }
    
    # Event subscription
    
    def subscribe_to_event(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Subscribe to blockchain events.
        
        Args:
            event_type: The type of event to subscribe to
            callback: Function to call when the event occurs
            
        Returns:
            Subscription ID
        """
        import uuid
        subscription_id = str(uuid.uuid4())
        
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = {}
            
        self.event_listeners[event_type][subscription_id] = callback
        
        return subscription_id
    
    def unsubscribe_from_event(self, event_type: str, subscription_id: str) -> bool:
        """
        Unsubscribe from blockchain events.
        
        Args:
            event_type: The type of event
            subscription_id: The subscription ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if event_type in self.event_listeners and subscription_id in self.event_listeners[event_type]:
            del self.event_listeners[event_type][subscription_id]
            return True
            
        return False
    
    def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: The type of event
            event_data: The event data
        """
        if event_type not in self.event_listeners:
            return
            
        for callback in self.event_listeners[event_type].values():
            try:
                callback(event_data)
            except Exception as e:
                print(f"Error in event callback: {e}")


class Web3Tab:
    """
    Web3 tab for the Aleo wallet GUI.
    Provides UI for Web3 settings and dApp connections.
    """
    
    def __init__(self, parent, web3_provider):
        """
        Initialize the Web3 tab.
        
        Args:
            parent: The parent frame
            web3_provider: The Web3 provider instance
        """
        import tkinter as tk
        from tkinter import ttk
        
        self.parent = parent
        self.web3_provider = web3_provider
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Create the content
        self.create_content()
        
        # Register for connection status updates
        self.web3_provider.register_connection_callback(self.update_connection_status)
    
    def create_content(self):
        """Create the tab content."""
        import tkinter as tk
        from tkinter import ttk
        
        # Connection settings section
        settings_frame = ttk.LabelFrame(self.frame, text="Connection Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # RPC endpoint
        endpoint_label = ttk.Label(settings_frame, text="RPC Endpoint:")
        endpoint_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.endpoint_var = tk.StringVar(value=self.web3_provider.rpc_endpoint)
        self.endpoint_entry = ttk.Entry(settings_frame, textvariable=self.endpoint_var, width=50)
        self.endpoint_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Connect button
        self.connect_button = ttk.Button(settings_frame, text="Connect", command=self.connect_to_endpoint)
        self.connect_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Connection status
        status_frame = ttk.Frame(settings_frame)
        status_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=10, pady=10)
        
        status_label = ttk.Label(status_frame, text="Status:")
        status_label.pack(side=tk.LEFT)
        
        self.status_value = ttk.Label(status_frame, text="Disconnected")
        self.status_value.pack(side=tk.LEFT, padx=5)
        
        # Network information
        info_frame = ttk.LabelFrame(self.frame, text="Network Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Block height
        height_label = ttk.Label(info_frame, text="Latest Block:")
        height_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.height_value = ttk.Label(info_frame, text="Unknown")
        self.height_value.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Update button
        update_button = ttk.Button(info_frame, text="Update", command=self.update_network_info)
        update_button.grid(row=0, column=2, padx=10, pady=5)
        
        # Connected dApps section
        dapps_frame = ttk.LabelFrame(self.frame, text="Connected dApps")
        dapps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for dApps
        self.dapps_tree = ttk.Treeview(dapps_frame, columns=("name", "url", "connected", "permissions"), show="headings")
        self.dapps_tree.heading("name", text="Name")
        self.dapps_tree.heading("url", text="URL")
        self.dapps_tree.heading("connected", text="Connected Since")
        self.dapps_tree.heading("permissions", text="Permissions")
        
        self.dapps_tree.column("name", width=150)
        self.dapps_tree.column("url", width=200)
        self.dapps_tree.column("connected", width=150)
        self.dapps_tree.column("permissions", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(dapps_frame, orient=tk.VERTICAL, command=self.dapps_tree.yview)
        self.dapps_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dapps_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons for dApp management
        button_frame = ttk.Frame(dapps_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        disconnect_button = ttk.Button(button_frame, text="Disconnect Selected", command=self.disconnect_selected_dapp)
        disconnect_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Refresh List", command=self.refresh_dapps_list)
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def connect_to_endpoint(self):
        """Connect to the specified RPC endpoint."""
        endpoint = self.endpoint_var.get()
        if not endpoint:
            self.show_error("Please enter an RPC endpoint URL")
            return
            
        # Update the button state
        self.connect_button.config(state="disabled")
        self.status_value.config(text="Connecting...")
        
        # Schedule the connection attempt
        self.parent.after(100, lambda: self._do_connect(endpoint))
    
    def _do_connect(self, endpoint):
        """Perform the actual connection attempt."""
        success = self.web3_provider.set_rpc_endpoint(endpoint)
        
        if success:
            self.status_value.config(text="Connected")
            self.update_network_info()
        else:
            self.status_value.config(text="Connection Failed")
            self.show_error("Failed to connect to the specified endpoint")
            
        # Re-enable the button
        self.connect_button.config(state="normal")
    
    def update_connection_status(self, connected):
        """Update the connection status display."""
        if connected:
            self.status_value.config(text="Connected")
        else:
            self.status_value.config(text="Disconnected")
    
    def update_network_info(self):
        """Update the network information display."""
        # Get the latest block height
        height = self.web3_provider.get_latest_height()
        if height >= 0:
            self.height_value.config(text=str(height))
        else:
            self.height_value.config(text="Unknown")
    
    def refresh_dapps_list(self):
        """Refresh the list of connected dApps."""
        # Clear the existing entries
        self.dapps_tree.delete(*self.dapps_tree.get_children())
        
        # Add the connected dApps
        import datetime
        for connection_id, dapp in self.web3_provider.connected_dapps.items():
            # Format the connected time
            connected_time = datetime.datetime.fromtimestamp(dapp["connected_at"]).strftime("%Y-%m-%d %H:%M:%S")
            
            # Get the permissions
            permissions = ", ".join(self.web3_provider.permissions.get(connection_id, []))
            
            # Add to the tree
            self.dapps_tree.insert("", tk.END, values=(
                dapp["name"],
                dapp["url"],
                connected_time,
                permissions
            ))
    
    def disconnect_selected_dapp(self):
        """Disconnect the selected dApp."""
        # Get the selected item
        selection = self.dapps_tree.selection()
        if not selection:
            self.show_error("Please select a dApp to disconnect")
            return
            
        # Get the connection ID
        item = selection[0]
        values = self.dapps_tree.item(item, "values")
        dapp_name = values[0]
        dapp_url = values[1]
        
        # Find the connection ID
        connection_id = None
        for cid, dapp in self.web3_provider.connected_dapps.items():
            if dapp["name"] == dapp_name and dapp["url"] == dapp_url:
                connection_id = cid
                break
                
        if not connection_id:
            self.show_error("Could not find the connection ID")
            return
            
        # Disconnect the dApp
        success = self.web3_provider.disconnect_dapp(connection_id)
        if success:
            # Remove from the tree
            self.dapps_tree.delete(item)
        else:
            self.show_error("Failed to disconnect the dApp")
    
    def show_error(self, message):
        """Show an error message."""
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", message)


# Integration with the main wallet GUI
def integrate_web3(wallet_gui):
    """
    Integrate Web3 functionality into the wallet GUI.
    
    Args:
        wallet_gui: The wallet GUI instance
    """
    # Create the Web3 provider
    web3_provider = AleoWeb3Provider(wallet_gui.rpc_entry.get() if hasattr(wallet_gui, "rpc_entry") else "https://api.aleo.network/v1")
    
    # Create the Web3 tab
    web3_tab = Web3Tab(wallet_gui.notebook, web3_provider)
    
    # Add the tab to the notebook
    wallet_gui.notebook.add(web3_tab.frame, text="Web3")
    
    # Store the Web3 provider in the wallet GUI for access from other components
    wallet_gui.web3_provider = web3_provider
    
    # Add Web3 connection status to the footer
    web3_status = ttk.Label(wallet_gui.main_frame.winfo_children()[2], text="Web3: Disconnected", style="Footer.TLabel")
    web3_status.pack(side=tk.LEFT, padx=10, pady=5)
    
    # Update the Web3 status when the connection status changes
    def update_web3_status(connected):
        web3_status.config(text=f"Web3: {'Connected' if connected else 'Disconnected'}")
    
    web3_provider.register_connection_callback(update_web3_status)
    
    return web3_provider
