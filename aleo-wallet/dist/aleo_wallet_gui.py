import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import os
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

# This would be replaced with actual API implementation
from aleo_api import AleoBlockchainAPI, AleoWalletAPI

class AleoWalletGUI:
    """
    A GUI wallet for the Aleo blockchain with the same visual identity as the mining software.
    """
    
    # Color scheme matching the mining software
    COLORS = {
        "deep_blue": "#1E3A8A",
        "teal": "#0D9488",
        "gold": "#F59E0B",
        "dark_gray": "#1F2937",
        "light_gray": "#F3F4F6",
        "white": "#FFFFFF",
        "success_green": "#10B981",
        "warning_amber": "#F59E0B",
        "error_red": "#EF4444"
    }
    
    def __init__(self, root):
        """
        Initialize the Aleo Wallet GUI.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Aleo Wallet")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set dark mode as default
        self.dark_mode = True
        
        # Initialize API clients
        self.blockchain_api = AleoBlockchainAPI()
        self.wallet_api = AleoWalletAPI(self.blockchain_api)
        
        # Initialize account data
        self.accounts = []
        self.current_account_index = -1
        self.aleo_price = 0.0
        
        # Create UI elements
        self.setup_ui()
        
        # Start background tasks
        self.start_background_tasks()
        
        # Load saved accounts if available
        self.load_accounts()
        
    def setup_ui(self):
        """Set up the user interface components."""
        # Configure style
        self.configure_style()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        self.create_header()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_frame.grid_columnconfigure(1, weight=1)  # Content
        self.main_frame.grid_rowconfigure(0, weight=0)     # Header
        self.main_frame.grid_rowconfigure(1, weight=1)     # Content
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_send_tab()
        self.create_receive_tab()
        self.create_transactions_tab()
        self.create_settings_tab()
        
        # Create footer
        self.create_footer()
        
    def configure_style(self):
        """Configure the ttk styles for the application."""
        self.style = ttk.Style()
        
        # Apply dark mode or light mode
        self.update_theme()
        
        # Configure common styles
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        self.style.configure("Address.TLabel", font=("Courier", 10))
        self.style.configure("Balance.TLabel", font=("Arial", 24, "bold"))
        
    def update_theme(self):
        """Update the theme based on dark/light mode preference."""
        if self.dark_mode:
            # Dark mode
            bg_color = self.COLORS["dark_gray"]
            fg_color = self.COLORS["white"]
            accent_color = self.COLORS["teal"]
            self.root.configure(bg=bg_color)
            
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("Content.TFrame", background=bg_color)
            self.style.configure("Sidebar.TFrame", background=self.COLORS["deep_blue"])
            self.style.configure("Header.TFrame", background=self.COLORS["deep_blue"])
            self.style.configure("Footer.TFrame", background=self.COLORS["deep_blue"])
            
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("Header.TLabel", background=self.COLORS["deep_blue"], foreground=fg_color)
            self.style.configure("Footer.TLabel", background=self.COLORS["deep_blue"], foreground=fg_color)
            self.style.configure("Sidebar.TLabel", background=self.COLORS["deep_blue"], foreground=fg_color)
            
            self.style.configure("TButton", background=accent_color, foreground=fg_color)
            self.style.map("TButton", 
                          background=[("active", self.COLORS["deep_blue"])],
                          foreground=[("active", self.COLORS["white"])])
            
            self.style.configure("TNotebook", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color, padding=[10, 5])
            self.style.map("TNotebook.Tab",
                          background=[("selected", accent_color)],
                          foreground=[("selected", self.COLORS["white"])])
            
            self.style.configure("Treeview", 
                               background=bg_color, 
                               foreground=fg_color, 
                               fieldbackground=bg_color)
            self.style.map("Treeview",
                         background=[("selected", accent_color)],
                         foreground=[("selected", self.COLORS["white"])])
            
        else:
            # Light mode
            bg_color = self.COLORS["light_gray"]
            fg_color = self.COLORS["dark_gray"]
            accent_color = self.COLORS["teal"]
            self.root.configure(bg=bg_color)
            
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("Content.TFrame", background=bg_color)
            self.style.configure("Sidebar.TFrame", background=self.COLORS["deep_blue"])
            self.style.configure("Header.TFrame", background=self.COLORS["deep_blue"])
            self.style.configure("Footer.TFrame", background=self.COLORS["deep_blue"])
            
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("Header.TLabel", background=self.COLORS["deep_blue"], foreground=self.COLORS["white"])
            self.style.configure("Footer.TLabel", background=self.COLORS["deep_blue"], foreground=self.COLORS["white"])
            self.style.configure("Sidebar.TLabel", background=self.COLORS["deep_blue"], foreground=self.COLORS["white"])
            
            self.style.configure("TButton", background=accent_color, foreground=self.COLORS["white"])
            self.style.map("TButton", 
                          background=[("active", self.COLORS["deep_blue"])],
                          foreground=[("active", self.COLORS["white"])])
            
            self.style.configure("TNotebook", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color, padding=[10, 5])
            self.style.map("TNotebook.Tab",
                          background=[("selected", accent_color)],
                          foreground=[("selected", self.COLORS["white"])])
            
            self.style.configure("Treeview", 
                               background=self.COLORS["white"], 
                               foreground=fg_color, 
                               fieldbackground=self.COLORS["white"])
            self.style.map("Treeview",
                         background=[("selected", accent_color)],
                         foreground=[("selected", self.COLORS["white"])])
    
    def create_header(self):
        """Create the header with logo and title."""
        header_frame = ttk.Frame(self.main_frame, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Logo (placeholder - would be replaced with actual logo)
        logo_text = "⛏ ALEO"
        logo_label = ttk.Label(header_frame, text=logo_text, style="Header.TLabel", font=("Arial", 18, "bold"))
        logo_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(header_frame, text="Wallet", style="Header.TLabel", font=("Arial", 18))
        title_label.pack(side=tk.LEFT, padx=0, pady=10)
        
        # Aleo price display
        self.price_frame = ttk.Frame(header_frame, style="Header.TFrame")
        self.price_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.price_label = ttk.Label(self.price_frame, text="ALEO: $0.00", style="Header.TLabel")
        self.price_label.pack(side=tk.RIGHT)
        
    def create_sidebar(self):
        """Create the sidebar with account selection and balance."""
        sidebar_frame = ttk.Frame(self.main_frame, style="Sidebar.TFrame", width=200)
        sidebar_frame.grid(row=1, column=0, sticky="ns")
        sidebar_frame.pack_propagate(False)
        
        # Account selection
        account_label = ttk.Label(sidebar_frame, text="ACCOUNTS", style="Sidebar.TLabel", font=("Arial", 12, "bold"))
        account_label.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        self.account_listbox = tk.Listbox(sidebar_frame, bg=self.COLORS["deep_blue"], fg=self.COLORS["white"],
                                         selectbackground=self.COLORS["teal"], selectforeground=self.COLORS["white"],
                                         font=("Arial", 10), height=10, borderwidth=0, highlightthickness=0)
        self.account_listbox.pack(fill=tk.X, padx=10, pady=5)
        self.account_listbox.bind("<<ListboxSelect>>", self.on_account_selected)
        
        # Account actions
        account_actions_frame = ttk.Frame(sidebar_frame, style="Sidebar.TFrame")
        account_actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        create_btn = ttk.Button(account_actions_frame, text="New", command=self.create_new_account)
        create_btn.pack(side=tk.LEFT, padx=2)
        
        import_btn = ttk.Button(account_actions_frame, text="Import", command=self.import_account)
        import_btn.pack(side=tk.LEFT, padx=2)
        
        # Balance display
        balance_frame = ttk.Frame(sidebar_frame, style="Sidebar.TFrame")
        balance_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        balance_label = ttk.Label(balance_frame, text="BALANCE", style="Sidebar.TLabel", font=("Arial", 12, "bold"))
        balance_label.pack(anchor=tk.W)
        
        self.balance_value = ttk.Label(balance_frame, text="0.00 ALEO", style="Sidebar.TLabel", font=("Arial", 16, "bold"))
        self.balance_value.pack(anchor=tk.W, pady=(5, 0))
        
        # Sidebar footer with attribution
        attribution_frame = ttk.Frame(sidebar_frame, style="Sidebar.TFrame")
        attribution_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        created_by = ttk.Label(attribution_frame, text="Created by", style="Sidebar.TLabel", font=("Arial", 8))
        created_by.pack(anchor=tk.W)
        
        creator = ttk.Label(attribution_frame, text="Magnafic0 Unchained", style="Sidebar.TLabel", font=("Arial", 9, "bold"))
        creator.pack(anchor=tk.W)
        
        powered_by = ttk.Label(attribution_frame, text="Powered by", style="Sidebar.TLabel", font=("Arial", 8))
        powered_by.pack(anchor=tk.W, pady=(10, 0))
        
        engine = ttk.Label(attribution_frame, text="CryptoNebula", style="Sidebar.TLabel", font=("Arial", 9, "bold"))
        engine.pack(anchor=tk.W)
        
    def create_dashboard_tab(self):
        """Create the dashboard tab with overview and charts."""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Account overview
        overview_frame = ttk.LabelFrame(dashboard_frame, text="Account Overview")
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Address display
        address_label = ttk.Label(overview_frame, text="Address:")
        address_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.address_value = ttk.Label(overview_frame, text="No account selected", style="Address.TLabel")
        self.address_value.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        copy_btn = ttk.Button(overview_frame, text="Copy", command=self.copy_address_to_clipboard)
        copy_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # View key display (truncated for security)
        view_key_label = ttk.Label(overview_frame, text="View Key:")
        view_key_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.view_key_value = ttk.Label(overview_frame, text="••••••••••••••••••••••••••••••••")
        self.view_key_value.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        view_btn = ttk.Button(overview_frame, text="View", command=self.toggle_view_key)
        view_btn.grid(row=1, column=2, padx=10, pady=5)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for recent transactions
        self.activity_tree = ttk.Treeview(activity_frame, columns=("date", "type", "amount", "status"), show="headings")
        self.activity_tree.heading("date", text="Date")
        self.activity_tree.heading("type", text="Type")
        self.activity_tree.heading("amount", text="Amount")
        self.activity_tree.heading("status", text="Status")
        
        self.activity_tree.column("date", width=150)
        self.activity_tree.column("type", width=100)
        self.activity_tree.column("amount", width=100)
        self.activity_tree.column("status", width=100)
        
        self.activity_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Price chart
        chart_frame = ttk.LabelFrame(dashboard_frame, text="ALEO Price (24h)")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a figure for the chart
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty chart
        self.update_price_chart([0], [0])
        
    def create_send_tab(self):
        """Create the send tab for sending transactions."""
        send_frame = ttk.Frame(self.notebook)
        self.notebook.add(send_frame, text="Send")
        
        # Form for sending
        form_frame = ttk.Frame(send_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Recipient address
        recipient_label = ttk.Label(form_frame, text="Recipient Address:")
        recipient_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.recipient_entry = ttk.Entry(form_frame, width=50)
        self.recipient_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Amount
        amount_label = ttk.Label(form_frame, text="Amount (ALEO):")
        amount_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.amount_entry = ttk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Fee
        fee_label = ttk.Label(form_frame, text="Transaction Fee:")
        fee_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.fee_value = ttk.Label(form_frame, text="0.001 ALEO (estimated)")
        self.fee_value.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Total
        total_label = ttk.Label(form_frame, text="Total Amount:")
        total_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.total_value = ttk.Label(form_frame, text="0.001 ALEO")
        self.total_value.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Update total when amount changes
        self.amount_entry.bind("<KeyRelease>", self.update_send_total)
        
        # Send button
        send_btn = ttk.Button(form_frame, text="Send Transaction", command=self.send_transaction)
        send_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
    def create_receive_tab(self):
        """Create the receive tab for receiving funds."""
        receive_frame = ttk.Frame(self.notebook)
        self.notebook.add(receive_frame, text="Receive")
        
        # Account address display
        address_frame = ttk.Frame(receive_frame)
        address_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(address_frame, text="Your Aleo Address", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Address display
        self.receive_address = ttk.Label(address_frame, text="No account selected", style="Address.TLabel")
        self.receive_address.pack(pady=10)
        
        # QR code placeholder (would be replaced with actual QR code)
        qr_frame = ttk.Frame(address_frame, width=200, height=200, style="Content.TFrame")
        qr_frame.pack(pady=20)
        qr_frame.pack_propagate(False)
        
        qr_placeholder = ttk.Label(qr_frame, text="QR Code\nPlaceholder")
        qr_placeholder.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Copy button
        copy_btn = ttk.Button(address_frame, text="Copy Address", command=self.copy_address_to_clipboard)
        copy_btn.pack(pady=10)
        
    def create_transactions_tab(self):
        """Create the transactions tab for viewing transaction history."""
        transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(transactions_frame, text="Transactions")
        
        # Filters
        filter_frame = ttk.Frame(transactions_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        filter_label = ttk.Label(filter_frame, text="Filter:")
        filter_label.pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="All")
        filter_all = ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, value="All", command=self.filter_transactions)
        filter_all.pack(side=tk.LEFT, padx=5)
        
        filter_sent = ttk.Radiobutton(filter_frame, text="Sent", variable=self.filter_var, value="Sent", command=self.filter_transactions)
        filter_sent.pack(side=tk.LEFT, padx=5)
        
        filter_received = ttk.Radiobutton(filter_frame, text="Received", variable=self.filter_var, value="Received", command=self.filter_transactions)
        filter_received.pack(side=tk.LEFT, padx=5)
        
        # Transaction list
        self.tx_tree = ttk.Treeview(transactions_frame, columns=("date", "type", "address", "amount", "status"), show="headings")
        self.tx_tree.heading("date", text="Date")
        self.tx_tree.heading("type", text="Type")
        self.tx_tree.heading("address", text="Address")
        self.tx_tree.heading("amount", text="Amount")
        self.tx_tree.heading("status", text="Status")
        
        self.tx_tree.column("date", width=150)
        self.tx_tree.column("type", width=80)
        self.tx_tree.column("address", width=250)
        self.tx_tree.column("amount", width=100)
        self.tx_tree.column("status", width=100)
        
        self.tx_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.tx_tree.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor=tk.NE)
        self.tx_tree.configure(yscrollcommand=scrollbar.set)
        
        # Double-click to view transaction details
        self.tx_tree.bind("<Double-1>", self.view_transaction_details)
        
    def create_settings_tab(self):
        """Create the settings tab for wallet configuration."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # General settings
        general_frame = ttk.LabelFrame(settings_frame, text="General Settings")
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme toggle
        theme_frame = ttk.Frame(general_frame)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        theme_label = ttk.Label(theme_frame, text="Theme:")
        theme_label.pack(side=tk.LEFT, padx=5)
        
        self.theme_var = tk.StringVar(value="Dark" if self.dark_mode else "Light")
        theme_dark = ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="Dark", command=self.toggle_theme)
        theme_dark.pack(side=tk.LEFT, padx=5)
        
        theme_light = ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="Light", command=self.toggle_theme)
        theme_light.pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh toggle
        refresh_frame = ttk.Frame(general_frame)
        refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_label = ttk.Label(refresh_frame, text="Auto-refresh:")
        refresh_label.pack(side=tk.LEFT, padx=5)
        
        self.refresh_var = tk.BooleanVar(value=True)
        refresh_check = ttk.Checkbutton(refresh_frame, text="Enable", variable=self.refresh_var)
        refresh_check.pack(side=tk.LEFT, padx=5)
        
        # Security settings
        security_frame = ttk.LabelFrame(settings_frame, text="Security Settings")
        security_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Password protection
        password_frame = ttk.Frame(security_frame)
        password_frame.pack(fill=tk.X, padx=10, pady=5)
        
        password_label = ttk.Label(password_frame, text="Password Protection:")
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_var = tk.BooleanVar(value=False)
        password_check = ttk.Checkbutton(password_frame, text="Enable", variable=self.password_var, command=self.toggle_password_protection)
        password_check.pack(side=tk.LEFT, padx=5)
        
        # Backup wallet
        backup_frame = ttk.Frame(security_frame)
        backup_frame.pack(fill=tk.X, padx=10, pady=5)
        
        backup_btn = ttk.Button(backup_frame, text="Backup Wallet", command=self.backup_wallet)
        backup_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # About section
        about_frame = ttk.LabelFrame(settings_frame, text="About")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text = "Aleo Wallet\nVersion 1.0\n\nCreated by Magnafic0 Unchained\nPowered by CryptoNebula\n\nThe first GUI wallet for Aleo blockchain."
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.CENTER)
        about_label.pack(padx=20, pady=20)
        
    def create_footer(self):
        """Create the footer with status information."""
        footer_frame = ttk.Frame(self.main_frame, style="Footer.TFrame")
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Network status
        self.network_status = ttk.Label(footer_frame, text="Network: Connected", style="Footer.TLabel")
        self.network_status.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Block height
        self.block_height = ttk.Label(footer_frame, text="Block: 0", style="Footer.TLabel")
        self.block_height.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Version
        version_label = ttk.Label(footer_frame, text="v1.0", style="Footer.TLabel")
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
    def start_background_tasks(self):
        """Start background tasks for updating data."""
        # Update blockchain data
        self.update_blockchain_data()
        
        # Update price data
        self.update_price_data()
        
    def update_blockchain_data(self):
        """Update blockchain data in the background."""
        def update():
            while True:
                try:
                    # Get latest block height
                    height = self.blockchain_api.get_latest_height()
                    self.root.after(0, lambda: self.block_height.config(text=f"Block: {height}"))
                    
                    # Update account balance if an account is selected
                    if self.current_account_index >= 0:
                        self.update_account_balance()
                        self.update_transaction_history()
                        
                    # Update network status
                    self.root.after(0, lambda: self.network_status.config(text="Network: Connected"))
                except Exception as e:
                    print(f"Error updating blockchain data: {e}")
                    self.root.after(0, lambda: self.network_status.config(text="Network: Disconnected"))
                
                # Sleep for 30 seconds
                time.sleep(30)
        
        # Start the update thread
        threading.Thread(target=update, daemon=True).start()
        
    def update_price_data(self):
        """Update price data in the background."""
        def update():
            # Simulated price data points (would be replaced with actual API calls)
            times = []
            prices = []
            current_price = 0.25  # Starting price
            
            while True:
                try:
                    # Simulate price changes (would be replaced with actual API calls)
                    import random
                    price_change = random.uniform(-0.01, 0.01)
                    current_price = max(0.01, current_price + price_change)
                    
                    # Update price label
                    self.root.after(0, lambda p=current_price: self.price_label.config(text=f"ALEO: ${p:.2f}"))
                    self.aleo_price = current_price
                    
                    # Update price chart data
                    times.append(len(times))
                    prices.append(current_price)
                    
                    # Keep only the last 24 data points (simulating 24 hours)
                    if len(times) > 24:
                        times = times[-24:]
                        prices = prices[-24:]
                    
                    # Update the chart
                    self.root.after(0, lambda t=times.copy(), p=prices.copy(): self.update_price_chart(t, p))
                    
                except Exception as e:
                    print(f"Error updating price data: {e}")
                
                # Sleep for 60 seconds
                time.sleep(60)
        
        # Start the update thread
        threading.Thread(target=update, daemon=True).start()
        
    def update_price_chart(self, times, prices):
        """Update the price chart with new data."""
        self.ax.clear()
        if len(times) > 1:  # Only plot if we have at least 2 data points
            self.ax.plot(times, prices, color=self.COLORS["teal"])
            self.ax.fill_between(times, 0, prices, color=self.COLORS["teal"], alpha=0.2)
        
        # Set background color based on theme
        if self.dark_mode:
            self.fig.patch.set_facecolor(self.COLORS["dark_gray"])
            self.ax.set_facecolor(self.COLORS["dark_gray"])
            text_color = self.COLORS["white"]
        else:
            self.fig.patch.set_facecolor(self.COLORS["light_gray"])
            self.ax.set_facecolor(self.COLORS["light_gray"])
            text_color = self.COLORS["dark_gray"]
        
        # Set text color for labels
        self.ax.tick_params(axis='x', colors=text_color)
        self.ax.tick_params(axis='y', colors=text_color)
        
        # Remove spines
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # Draw the canvas
        self.canvas.draw()
        
    def load_accounts(self):
        """Load saved accounts from file."""
        try:
            if os.path.exists("aleo_accounts.json"):
                with open("aleo_accounts.json", "r") as f:
                    self.accounts = json.load(f)
                
                # Update the account listbox
                self.update_account_listbox()
                
                # Select the first account if available
                if self.accounts:
                    self.account_listbox.selection_set(0)
                    self.on_account_selected(None)
        except Exception as e:
            print(f"Error loading accounts: {e}")
            messagebox.showerror("Error", f"Failed to load accounts: {e}")
            
    def save_accounts(self):
        """Save accounts to file."""
        try:
            # In a real implementation, we would encrypt the private keys
            with open("aleo_accounts.json", "w") as f:
                json.dump(self.accounts, f)
        except Exception as e:
            print(f"Error saving accounts: {e}")
            messagebox.showerror("Error", f"Failed to save accounts: {e}")
            
    def update_account_listbox(self):
        """Update the account listbox with current accounts."""
        self.account_listbox.delete(0, tk.END)
        for account in self.accounts:
            name = account.get("name", "Account")
            self.account_listbox.insert(tk.END, name)
            
    def on_account_selected(self, event):
        """Handle account selection from the listbox."""
        selection = self.account_listbox.curselection()
        if selection:
            self.current_account_index = selection[0]
            self.update_account_display()
            self.update_account_balance()
            self.update_transaction_history()
        
    def update_account_display(self):
        """Update the display with the selected account information."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            account = self.accounts[self.current_account_index]
            
            # Update address displays
            address = account.get("address", "")
            self.address_value.config(text=address)
            self.receive_address.config(text=address)
            
            # Update view key display (masked)
            view_key = account.get("view_key", "")
            masked_view_key = "•" * len(view_key)
            self.view_key_value.config(text=masked_view_key)
            
    def update_account_balance(self):
        """Update the account balance display."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            account = self.accounts[self.current_account_index]
            
            # In a real implementation, we would query the blockchain for the balance
            # For now, we'll use a simulated balance
            balance = account.get("balance", 0.0)
            self.balance_value.config(text=f"{balance:.2f} ALEO")
            
    def update_transaction_history(self):
        """Update the transaction history displays."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            account = self.accounts[self.current_account_index]
            
            # Clear existing entries
            self.activity_tree.delete(*self.activity_tree.get_children())
            self.tx_tree.delete(*self.tx_tree.get_children())
            
            # In a real implementation, we would query the blockchain for transactions
            # For now, we'll use simulated transactions
            transactions = account.get("transactions", [])
            
            # Add transactions to the activity tree (dashboard)
            for i, tx in enumerate(transactions[:5]):  # Show only the 5 most recent
                self.activity_tree.insert("", tk.END, values=(
                    tx.get("date", ""),
                    tx.get("type", ""),
                    f"{tx.get('amount', 0.0):.2f} ALEO",
                    tx.get("status", "")
                ))
                
            # Add transactions to the transactions tree
            for i, tx in enumerate(transactions):
                self.tx_tree.insert("", tk.END, values=(
                    tx.get("date", ""),
                    tx.get("type", ""),
                    tx.get("address", ""),
                    f"{tx.get('amount', 0.0):.2f} ALEO",
                    tx.get("status", "")
                ))
                
    def filter_transactions(self):
        """Filter transactions based on the selected filter."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            account = self.accounts[self.current_account_index]
            
            # Clear existing entries
            self.tx_tree.delete(*self.tx_tree.get_children())
            
            # Get all transactions
            transactions = account.get("transactions", [])
            
            # Apply filter
            filter_value = self.filter_var.get()
            if filter_value == "All":
                filtered_transactions = transactions
            else:
                filtered_transactions = [tx for tx in transactions if tx.get("type", "") == filter_value]
                
            # Add filtered transactions to the tree
            for i, tx in enumerate(filtered_transactions):
                self.tx_tree.insert("", tk.END, values=(
                    tx.get("date", ""),
                    tx.get("type", ""),
                    tx.get("address", ""),
                    f"{tx.get('amount', 0.0):.2f} ALEO",
                    tx.get("status", "")
                ))
                
    def create_new_account(self):
        """Create a new Aleo account."""
        try:
            # Generate a new account
            account = self.wallet_api.generate_account()
            
            # Add a name for the account
            name = simpledialog.askstring("Account Name", "Enter a name for the new account:")
            if not name:
                name = f"Account {len(self.accounts) + 1}"
                
            # Add the account to our list with additional metadata
            self.accounts.append({
                "name": name,
                "private_key": account["private_key"],
                "view_key": account["view_key"],
                "address": account["address"],
                "balance": 0.0,
                "transactions": []
            })
            
            # Update the account listbox
            self.update_account_listbox()
            
            # Select the new account
            self.account_listbox.selection_set(len(self.accounts) - 1)
            self.on_account_selected(None)
            
            # Save the accounts
            self.save_accounts()
            
            messagebox.showinfo("Success", f"New account '{name}' created successfully!")
            
        except Exception as e:
            print(f"Error creating account: {e}")
            messagebox.showerror("Error", f"Failed to create account: {e}")
            
    def import_account(self):
        """Import an existing Aleo account from private key."""
        try:
            # Ask for the private key
            private_key = simpledialog.askstring("Import Account", "Enter the private key:", show="*")
            if not private_key:
                return
                
            # Validate the private key format
            if not private_key.startswith("APrivateKey1"):
                messagebox.showerror("Error", "Invalid private key format. Must start with 'APrivateKey1'.")
                return
                
            # Import the account
            account = self.wallet_api.import_account_from_private_key(private_key)
            
            # Add a name for the account
            name = simpledialog.askstring("Account Name", "Enter a name for the imported account:")
            if not name:
                name = f"Imported Account {len(self.accounts) + 1}"
                
            # Add the account to our list with additional metadata
            self.accounts.append({
                "name": name,
                "private_key": account["private_key"],
                "view_key": account["view_key"],
                "address": account["address"],
                "balance": 0.0,
                "transactions": []
            })
            
            # Update the account listbox
            self.update_account_listbox()
            
            # Select the new account
            self.account_listbox.selection_set(len(self.accounts) - 1)
            self.on_account_selected(None)
            
            # Save the accounts
            self.save_accounts()
            
            messagebox.showinfo("Success", f"Account '{name}' imported successfully!")
            
        except Exception as e:
            print(f"Error importing account: {e}")
            messagebox.showerror("Error", f"Failed to import account: {e}")
            
    def copy_address_to_clipboard(self):
        """Copy the current account address to clipboard."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            address = self.accounts[self.current_account_index].get("address", "")
            self.root.clipboard_clear()
            self.root.clipboard_append(address)
            messagebox.showinfo("Copied", "Address copied to clipboard!")
            
    def toggle_view_key(self):
        """Toggle between showing the masked and unmasked view key."""
        if self.current_account_index >= 0 and self.current_account_index < len(self.accounts):
            view_key = self.accounts[self.current_account_index].get("view_key", "")
            current_text = self.view_key_value.cget("text")
            
            if "•" in current_text:
                # Show the actual view key
                self.view_key_value.config(text=view_key)
            else:
                # Mask the view key
                masked_view_key = "•" * len(view_key)
                self.view_key_value.config(text=masked_view_key)
                
    def update_send_total(self, event=None):
        """Update the total amount when the send amount changes."""
        try:
            amount = float(self.amount_entry.get() or 0)
            fee = 0.001  # Fixed fee for simplicity
            total = amount + fee
            self.total_value.config(text=f"{total:.3f} ALEO")
        except ValueError:
            self.total_value.config(text="Invalid amount")
            
    def send_transaction(self):
        """Send a transaction to the specified address."""
        if self.current_account_index < 0:
            messagebox.showerror("Error", "No account selected!")
            return
            
        try:
            # Get the recipient address and amount
            recipient = self.recipient_entry.get().strip()
            amount_str = self.amount_entry.get().strip()
            
            # Validate inputs
            if not recipient:
                messagebox.showerror("Error", "Recipient address is required!")
                return
                
            if not recipient.startswith("aleo1"):
                messagebox.showerror("Error", "Invalid recipient address format. Must start with 'aleo1'.")
                return
                
            if not amount_str:
                messagebox.showerror("Error", "Amount is required!")
                return
                
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than zero!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
                
            # Get the current account
            account = self.accounts[self.current_account_index]
            
            # Check if the account has sufficient balance
            balance = account.get("balance", 0.0)
            fee = 0.001  # Fixed fee for simplicity
            total = amount + fee
            
            if balance < total:
                messagebox.showerror("Error", f"Insufficient balance! Need {total:.3f} ALEO but have {balance:.3f} ALEO.")
                return
                
            # Confirm the transaction
            confirm = messagebox.askyesno("Confirm Transaction", 
                                        f"Send {amount:.3f} ALEO to {recipient}?\n\n"
                                        f"Fee: {fee:.3f} ALEO\n"
                                        f"Total: {total:.3f} ALEO")
            
            if not confirm:
                return
                
            # In a real implementation, we would create and broadcast the transaction
            # For now, we'll simulate it
            
            # Update the account balance
            account["balance"] -= total
            
            # Add the transaction to the account's transaction history
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            account["transactions"].insert(0, {
                "date": now,
                "type": "Sent",
                "address": recipient,
                "amount": amount,
                "fee": fee,
                "status": "Confirmed"
            })
            
            # Save the accounts
            self.save_accounts()
            
            # Update the UI
            self.update_account_balance()
            self.update_transaction_history()
            
            # Clear the form
            self.recipient_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Transaction sent successfully!\n\nAmount: {amount:.3f} ALEO\nRecipient: {recipient}")
            
        except Exception as e:
            print(f"Error sending transaction: {e}")
            messagebox.showerror("Error", f"Failed to send transaction: {e}")
            
    def view_transaction_details(self, event):
        """View details of a selected transaction."""
        selection = self.tx_tree.selection()
        if not selection:
            return
            
        # Get the selected transaction
        item = self.tx_tree.item(selection[0])
        values = item["values"]
        
        # Display transaction details
        details = f"Date: {values[0]}\n"
        details += f"Type: {values[1]}\n"
        details += f"Address: {values[2]}\n"
        details += f"Amount: {values[3]}\n"
        details += f"Status: {values[4]}\n"
        
        messagebox.showinfo("Transaction Details", details)
        
    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.dark_mode = self.theme_var.get() == "Dark"
        self.update_theme()
        
    def toggle_password_protection(self):
        """Toggle password protection for the wallet."""
        if self.password_var.get():
            # Ask for a new password
            password = simpledialog.askstring("Set Password", "Enter a new password:", show="*")
            if not password:
                self.password_var.set(False)
                return
                
            # Confirm the password
            confirm = simpledialog.askstring("Confirm Password", "Confirm your password:", show="*")
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match!")
                self.password_var.set(False)
                return
                
            # In a real implementation, we would hash and store the password
            messagebox.showinfo("Success", "Password protection enabled!")
        else:
            messagebox.showinfo("Success", "Password protection disabled!")
            
    def backup_wallet(self):
        """Backup the wallet to a file."""
        try:
            # In a real implementation, we would encrypt the wallet data
            backup_data = json.dumps(self.accounts, indent=2)
            
            # Ask for a file location
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Wallet Backup"
            )
            
            if not file_path:
                return
                
            # Write the backup data to the file
            with open(file_path, "w") as f:
                f.write(backup_data)
                
            messagebox.showinfo("Success", f"Wallet backed up successfully to {file_path}!")
            
        except Exception as e:
            print(f"Error backing up wallet: {e}")
            messagebox.showerror("Error", f"Failed to backup wallet: {e}")


def main():
    root = tk.Tk()
    app = AleoWalletGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
