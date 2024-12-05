# Importing necessary libraries for the application
import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, Scrollbar
import pickle
import os
from datetime import datetime
import re

# Ticket class definition: Stores details of a ticket
class Ticket:
    def __init__(self, name, description, price, validity, discount, terms):
        # Initialize ticket attributes
        self.name = name
        self.description = description
        self.price = price
        self.validity = validity
        self.discount = discount
        self.terms = terms
        self.sold_count = 0  # Track number of tickets sold

    def __str__(self):
        # Define how to represent a ticket as a string
        return f"{self.name} - {self.price} USD (Sold: {self.sold_count})"

# User class definition: Stores user information and their purchase history
class User:
    def __init__(self, username, password, email, phone_number, dob):
        # Initialize user attributes
        self.username = username
        self.password = password
        self.email = email
        self.phone_number = phone_number
        self.dob = dob
        self.purchase_history = []  # List to track the user's ticket purchases

    def add_purchase(self, ticket):
        # Add a purchased ticket to the user's purchase history
        self.purchase_history.append(ticket)

    def update_details(self, email=None, phone_number=None, dob=None):
        # Update the user's details if provided
        if email:
            self.email = email
        if phone_number:
            self.phone_number = phone_number
        if dob:
            self.dob = dob

# Main class for managing the ticket booking system
class TicketBookingSystem:
    def __init__(self):
        # Initialize file names and load users and tickets data
        self.users_file = "users.pkl"  # File to store user data
        self.tickets_file = "tickets.pkl"  # File to store ticket data
        self.users = self.load_users()  # Load existing users from file
        self.tickets = self.load_tickets()  # Load existing tickets from file

    # Load user data from the file if it exists
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "rb") as file:
                return pickle.load(file)
        return {}  # Return an empty dictionary if no user data exists

    # Save user data to the file
    def save_users(self):
        with open(self.users_file, "wb") as file:
            pickle.dump(self.users, file)

    # Load ticket data from the file if it exists
    def load_tickets(self):
        if os.path.exists(self.tickets_file):
            with open(self.tickets_file, "rb") as file:
                return pickle.load(file)
        # Default set of tickets if no file exists
        return [
            Ticket("Single Day Pass", "Access to the park for one day", 275, "1 day", "None", "Valid only on selected date"),
            Ticket("Two-Day Pass", "Access to the park for two consecutive days", 480, "2 days", "10% discount for online purchase", "Cannot be split over multiple trips"),
            Ticket("Annual Membership", "Unlimited access for one year", 1840, "1 year", "15% discount on renewal", "Must be used by the same person"),
            Ticket("Child Ticket", "Discounted ticket for children (ages 3-12)", 185, "1 day", "None", "Valid only on selected date, must be accompanied by an adult"),
            Ticket("Group Ticket (10+)", "Special rate for groups of 10 or more", 220, "1 day", "20% off for groups of 20 or more", "Must be booked in advance"),
            Ticket("VIP Experience Pass", "Includes expedited access and reserved seating for shows", 550, "1 day", "None", "Limited availability, must be purchased in advance")
        ]

    # Save ticket data to the file
    def save_tickets(self):
        with open(self.tickets_file, "wb") as file:
            pickle.dump(self.tickets, file)

    # Register a new user if the username does not already exist
    def register_user(self, username, password, email, phone_number, dob):
        if username in self.users:
            return False  # Return False if the username is already taken
        user = User(username, password, email, phone_number, dob)  # Create a new user
        self.users[username] = user  # Store the user in the dictionary
        self.save_users()  # Save users to file
        return True  # Return True indicating successful registration

    # Login a user by validating the username and password
    def login_user(self, username, password):
        user = self.users.get(username)  # Retrieve user by username
        if user and user.password == password:
            return user  # Return the user object if login is successful
        return None  # Return None if the login fails

    # Add a purchased ticket to the user's purchase history
    def add_purchase_to_user(self, username, ticket):
        user = self.users.get(username)  # Retrieve the user by username
        if user:
            user.add_purchase(ticket)  # Add the ticket to the user's history
            self.save_users()  # Save the updated user data to file

    # Modify the user's details (email, phone number, date of birth)
    def modify_user_details(self, username, email=None, phone_number=None, dob=None):
        user = self.users.get(username)  # Retrieve the user by username
        if user:
            user.update_details(email, phone_number, dob)  # Update the user's details
            self.save_users()  # Save the updated user data to file
            return True  # Return True indicating successful update
        return False  # Return False if the user is not found

    # Purchase a ticket by the user, applying relevant discounts
    def purchase_ticket(self, username, ticket_choice, num_persons=None, visit_date=None, payment_method=None):
        ticket = self.tickets[ticket_choice]  # Get the selected ticket
        discount = 0  # Initialize discount variable

        # Apply discounts based on ticket type
        if ticket.name == "Single Day Pass":
            discount = 0  # No discount for Single Day Pass
        elif ticket.name == "Two-Day Pass":
            discount = 0.10  # 10% discount for Two-Day Pass
        elif ticket.name == "Annual Membership":
            discount = 0.15  # 15% discount for Annual Membership
        elif ticket.name == "Child Ticket":
            discount = 0  # No discount for Child Ticket
        elif ticket.name == "Group Ticket (10+)":
            # Ensure that group size is a valid integer
            if not isinstance(num_persons, int) or num_persons < 1:
                raise ValueError("Group size must be a positive integer.")
            total_price = ticket.price * num_persons  # Calculate total price for group
            if num_persons > 10:
                discount = 0.20  # 20% discount for groups larger than 10
            final_price = total_price * (1 - discount)  # Calculate final price with discount
            ticket_record = f"{ticket.name} ({num_persons} people) - ${final_price:.2f} USD (Discount Applied: {int(discount * 100)}%)"
            self.add_purchase_to_user(username, ticket_record)  # Add purchase record to the user
            ticket.sold_count += num_persons  # Update ticket's sold count
            return final_price, ticket_record  # Return final price and ticket record

        # Standard pricing for single ticket purchase
        final_price = ticket.price * (1 - discount)  # Calculate final price after discount
        ticket_record = f"{ticket.name} - ${final_price:.2f} USD (Discount Applied: {int(discount * 100)}%)"
        self.add_purchase_to_user(username, ticket_record)  # Add purchase record to the user
        
        ticket.sold_count += 1  # Increment sold count by 1 for each ticket purchased
        return final_price, ticket_record  # Return final price and ticket record
 
# Main application class, inherits from Tkinter's Tk class
class Application(tk.Tk):
    def __init__(self, system):
        # Initialize the main application window
        super().__init__()
        self.system = system  # The ticket booking system instance
        self.title("Main Menu")  # Set the window title
        self.geometry("700x600")  # Set window size
        self.resizable(False, False)  # Disable window resizing
        self.config(bg="#FEFEBE")  # Set the background color

        # Create and pack the 'Register' button
        self.register_button = tk.Button(self, text="Register", width=25, height=3, font=('Arial', 12), command=self.open_register)
        self.register_button.pack(pady=20)

        # Create and pack the 'Login' button
        self.login_button = tk.Button(self, text="Login", width=25, height=3, font=('Arial', 12), command=self.open_login)
        self.login_button.pack(pady=20)

        # Create and pack the 'Admin' button
        self.admin_button = tk.Button(self, text="Admin", width=25, height=3, font=('Arial', 12), command=self.open_admin)
        self.admin_button.pack(pady=20)

        # Create and pack the 'Exit' button
        self.exit_button = tk.Button(self, text="Exit", width=25, height=3, font=('Arial', 12), command=self.quit)
        self.exit_button.pack(pady=20)

    # Method to open the registration window
    def open_register(self):
        RegisterWindow(self, self.system)

    # Method to open the login window
    def open_login(self):
        LoginWindow(self, self.system)

    # Method to open the admin window
    def open_admin(self):
        AdminWindow(self, self.system)

# Registration window class, inherits from Toplevel for creating a new window
class RegisterWindow(tk.Toplevel):
    def __init__(self, parent, system):
        # Initialize the registration window
        super().__init__(parent)
        self.system = system  # The ticket booking system instance
        self.title("Register")  # Set the window title
        self.geometry("700x700")  # Set window size
        self.config(bg="#FEFEBE")  # Set the background color
        
        # Create and pack the input fields for registration details

        self.username_label = tk.Label(self, text="Username", font=('Arial', 12))
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self, font=('Arial', 14), width=25)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self, text="Password", font=('Arial', 12))
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self, font=('Arial', 14), show="*", width=25)
        self.password_entry.pack(pady=10)

        self.email_label = tk.Label(self, text="Email", font=('Arial', 12))
        self.email_label.pack(pady=10)
        self.email_entry = tk.Entry(self, font=('Arial', 14), width=25)
        self.email_entry.pack(pady=10)

        self.phone_label = tk.Label(self, text="Phone Number", font=('Arial', 12))
        self.phone_label.pack(pady=10)
        self.phone_entry = tk.Entry(self, font=('Arial', 14), width=25)
        self.phone_entry.pack(pady=10)

        self.dob_label = tk.Label(self, text="Date of Birth (YYYY-MM-DD)", font=('Arial', 12))
        self.dob_label.pack(pady=10)
        self.dob_entry = tk.Entry(self, font=('Arial', 14), width=25)
        self.dob_entry.pack(pady=10)

        # Register button to submit registration details
        self.register_button = tk.Button(self, text="Register", font=('Arial', 12), width=25, height=3, command=self.register)
        self.register_button.pack(pady=20)

    # Method to handle user registration
    def register(self):
        # Get the data from the input fields
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        phone_number = self.phone_entry.get().strip()
        dob = self.dob_entry.get().strip()

        # Check if all fields are filled
        if not username or not password or not email or not phone_number or not dob:
            messagebox.showerror("Input Error", "All fields are required!")
            return

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Input Error", "Invalid email format!")
            return

        # Validate phone number format (basic format validation)
        if not re.match(r"^\+?1?\d{9,15}$", phone_number):
            messagebox.showerror("Input Error", "Invalid phone number format!")
            return

        # Validate date of birth format (YYYY-MM-DD)
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date of birth format. Use YYYY-MM-DD.")
            return

        # Proceed with registration if all inputs are valid
        if self.system.register_user(username, password, email, phone_number, dob):
            messagebox.showinfo("Success", "Registration successful!")
            self.destroy()  # Close the registration window
        else:
            messagebox.showerror("Error", "Username already exists!")  # Show error if username is taken

# Login window class, inherits from Toplevel for creating a new window
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, system):
        # Initialize the login window
        super().__init__(parent)
        self.system = system  # The ticket booking system instance
        self.title("Login")  # Set the window title
        self.geometry("700x600")  # Set window size
        self.config(bg="#FEFEBE")  # Set the background color

        # Create and pack the input fields for login details

        self.username_label = tk.Label(self, text="Username", font=('Arial', 12))
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self, font=('Arial', 14), width=25)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self, text="Password", font=('Arial', 12))
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self, font=('Arial', 14), show="*", width=25)
        self.password_entry.pack(pady=10)

        # Login button to submit login details
        self.login_button = tk.Button(self, text="Login", font=('Arial', 12), width=25, height=3, command=self.login)
        self.login_button.pack(pady=20)

    # Method to handle user login
    def login(self):
        # Get the data from the input fields
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Check if both fields are filled
        if not username or not password:
            messagebox.showerror("Input Error", "Both fields are required!")
            return
        
        # Attempt to login the user with the provided credentials
        user = self.system.login_user(username, password)
        if user:
            messagebox.showinfo("Success", "Login successful!")  # Show success message
            self.destroy()  # Close the login window
            UserMenu(self.master, user, self.system)  # Open the user menu
        else:
            messagebox.showerror("Error", "Invalid credentials!")  # Show error if login fails

# UserMenu class represents the main interface for the regular user
class UserMenu(tk.Toplevel):
    def __init__(self, parent, user, system):
        super().__init__(parent)
        self.user = user  # Store the user object
        self.system = system  # Store the system object
        self.title(f"Welcome {user.username}")  # Set the window title with the username
        self.geometry("700x700")  # Set window size
        self.config(bg="#FEFEBE")  # Set background color

        # Create a button for purchasing a ticket
        self.purchase_button = tk.Button(self, text="Purchase a Ticket", font=('Arial', 12), width=25, height=3, command=self.purchase_ticket)
        self.purchase_button.pack(pady=20)

        # Create a button to view purchase history
        self.history_button = tk.Button(self, text="View Purchase History", font=('Arial', 12), width=25, height=3, command=self.view_history)
        self.history_button.pack(pady=20)

        # Create a button for account management
        self.account_button = tk.Button(self, text="Account Management", font=('Arial', 12), width=25, height=3, command=self.account_management)
        self.account_button.pack(pady=20)

        # Create an exit button to close the window
        self.exit_button = tk.Button(self, text="Exit", font=('Arial', 12), width=25, height=3, command=self.quit)
        self.exit_button.pack(pady=20)

    # Function to open the ticket purchase window
    def purchase_ticket(self):
        purchase_window = tk.Toplevel(self)
        purchase_window.title("Select a Ticket")
        purchase_window.geometry("600x400")  # Set window size

        # Label for available tickets
        tk.Label(purchase_window, text="Available Tickets", font=("Arial", 16, "bold")).pack(pady=10)

        # Listbox to display the available tickets
        ticket_listbox = Listbox(purchase_window, font=("Arial", 12), width=50, height=10)
        ticket_listbox.pack(pady=20)

        # Insert available tickets into the listbox
        for idx, ticket in enumerate(self.system.tickets):
            ticket_listbox.insert(tk.END, f"{ticket.name} - ${ticket.price} USD")

        # Function to handle ticket selection from the listbox
        def on_select_ticket(event):
            selected_idx = ticket_listbox.curselection()[0]  # Get the selected ticket index
            ticket = self.system.tickets[selected_idx]  # Retrieve the ticket object
            # Ask the user for the visit date
            visit_date = simpledialog.askstring("Visit Date", "Enter your visit date (YYYY-MM-DD):")
            if not visit_date:
                return  # Exit if no date is provided
            # Ask for the payment method
            payment_method = simpledialog.askstring("Payment Method", "Enter Payment Method (e.g., Credit/Debit Card):")
            if not payment_method:
                return  # Exit if no payment method is provided
            # Ask for the number of persons
            num_persons = simpledialog.askinteger("Group Size", "Enter the number of persons:", minvalue=1)
            if num_persons:
                # If group size is specified, purchase the ticket for the group
                price, ticket_details = self.system.purchase_ticket(self.user.username, selected_idx, num_persons, visit_date, payment_method)
                messagebox.showinfo("Ticket Purchase", f"Ticket Purchased: {ticket_details}\nTotal: ${price:.2f}")
            else:
                # If no group size is provided, purchase for a single person
                price, ticket_details = self.system.purchase_ticket(self.user.username, selected_idx, visit_date=visit_date, payment_method=payment_method)
                messagebox.showinfo("Ticket Purchase", f"Ticket Purchased: {ticket_details}\nTotal: ${price:.2f}")

        # Bind the double-click event to select a ticket
        ticket_listbox.bind("<Double-1>", on_select_ticket)

    # Function to view purchase history
    def view_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Purchase History")
        history_window.geometry("600x400")

        tk.Label(history_window, text="Purchase History", font=("Arial", 16, "bold")).pack(pady=10)

        # Listbox to display the user's purchase history
        history_listbox = Listbox(history_window, font=("Arial", 12), width=50, height=10)
        history_listbox.pack(pady=20)

        # Populate the listbox with purchase history data
        for history_item in self.user.purchase_history:
            history_listbox.insert(tk.END, history_item)

    # Function to manage user account details
    def account_management(self):
        account_window = tk.Toplevel(self)
        account_window.title("Account Management")
        account_window.geometry("500x500")
        
        # Display account details
        tk.Label(account_window, text="Account Details", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(account_window, text=f"Username: {self.user.username}", font=("Arial", 14)).pack(pady=10)
        tk.Label(account_window, text=f"Email: {self.user.email}", font=("Arial", 14)).pack(pady=10)
        tk.Label(account_window, text=f"Phone Number: {self.user.phone_number}", font=("Arial", 14)).pack(pady=10)
        tk.Label(account_window, text=f"Date of Birth: {self.user.dob}", font=("Arial", 14)).pack(pady=10)

        # Button to modify user details
        modify_button = tk.Button(account_window, text="Modify Details", font=("Arial", 14), command=lambda: self.modify_details(account_window))
        modify_button.pack(pady=20)

    # Function to modify user account details
    def modify_details(self, account_window):
        modify_window = tk.Toplevel(account_window)
        modify_window.title("Modify Account Details")
        modify_window.geometry("400x400")

        # Entry fields for new account details
        email_label = tk.Label(modify_window, text="New Email:", font=("Arial", 12))
        email_label.pack(pady=10)
        email_entry = tk.Entry(modify_window, font=("Arial", 14), width=25)
        email_entry.pack(pady=10)

        phone_label = tk.Label(modify_window, text="New Phone Number:", font=("Arial", 12))
        phone_label.pack(pady=10)
        phone_entry = tk.Entry(modify_window, font=("Arial", 14), width=25)
        phone_entry.pack(pady=10)

        dob_label = tk.Label(modify_window, text="New Date of Birth (YYYY-MM-DD):", font=("Arial", 12))
        dob_label.pack(pady=10)
        dob_entry = tk.Entry(modify_window, font=("Arial", 14), width=25)
        dob_entry.pack(pady=10)

        # Function to save modified details
        def save_changes():
            new_email = email_entry.get().strip()
            new_phone = phone_entry.get().strip()
            new_dob = dob_entry.get().strip()

            # Update the system with new details
            if self.system.modify_user_details(self.user.username, new_email, new_phone, new_dob):
                messagebox.showinfo("Success", "Account details updated successfully!")
                self.user.email = new_email
                self.user.phone_number = new_phone
                self.user.dob = new_dob
                modify_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update details!")

        # Button to save the changes
        save_button = tk.Button(modify_window, text="Save Changes", font=("Arial", 14), command=save_changes)
        save_button.pack(pady=20)

# AdminWindow class represents the admin interface
class AdminWindow(tk.Toplevel):
    def __init__(self, parent, system):
        super().__init__(parent)
        self.system = system  # Store the system object
        self.title("Admin Menu")
        self.geometry("800x600")  # Set window size
        self.resizable(True, True)  # Allow resizing
        self.config(bg="#dcdcdc")  # Set background color

        # Button for user management
        self.user_management_button = tk.Button(self, text="User Management", font=('Arial', 14), width=30, height=3, command=self.user_management)
        self.user_management_button.pack(pady=20)

        # Button for ticket updation
        self.ticket_update_button = tk.Button(self, text="Ticket Updation", font=('Arial', 14), width=30, height=3, command=self.ticket_updation)
        self.ticket_update_button.pack(pady=20)

        # Button to view total tickets sold
        self.total_tickets_button = tk.Button(self, text="Total Tickets Sold", font=('Arial', 14), width=30, height=3, command=self.total_tickets_sold)
        self.total_tickets_button.pack(pady=20)

        # Button to exit the admin window
        self.exit_button = tk.Button(self, text="Exit", font=('Arial', 14), width=30, height=3, command=self.quit)
        self.exit_button.pack(pady=20)

    # Function to manage users
    def user_management(self):
        user_management_window = tk.Toplevel(self)
        user_management_window.title("User Management")
        user_management_window.geometry("600x400")  # Larger window for user management
        user_management_window.resizable(True, True)

        # Scrollbar and listbox to show users
        scrollbar = Scrollbar(user_management_window)
        scrollbar.pack(side="right", fill="y")

        user_listbox = Listbox(user_management_window, font=("Arial", 14), width=50, height=15, yscrollcommand=scrollbar.set)
        user_listbox.pack(pady=20)

        # Insert users into the listbox
        for username in self.system.users.keys():
            user_listbox.insert(tk.END, username)

        # Link the scrollbar to the listbox
        scrollbar.config(command=user_listbox.yview)

        # Function to delete a selected user
        def delete_user():
            selected_user = user_listbox.get(tk.ACTIVE)  # Get the selected user
            if selected_user:
                confirm_delete = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user: {selected_user}?")
                if confirm_delete:
                    del self.system.users[selected_user]  # Delete user from the system
                    self.system.save_users()  # Save the updated user list
                    user_listbox.delete(user_listbox.curselection())  # Remove the user from the listbox
                    messagebox.showinfo("Success", "User deleted successfully!")
            else:
                messagebox.showerror("Error", "No user selected!")

        # Button to delete a user
        delete_button = tk.Button(user_management_window, text="Delete User", font=("Arial", 14), width=20, height=2, command=delete_user)
        delete_button.pack(pady=20)

        # Button to close the user management window
        close_button = tk.Button(user_management_window, text="Close", font=("Arial", 14), width=20, height=2, command=user_management_window.destroy)
        close_button.pack(pady=10)

    # Function for ticket updation
    def ticket_updation(self):
        ticket_updation_window = tk.Toplevel(self)
        ticket_updation_window.title("Ticket Updation")
        ticket_updation_window.geometry("600x500")  # Larger window for ticket updation
        ticket_updation_window.resizable(True, True)

        tk.Label(ticket_updation_window, text="Available Tickets", font=("Arial", 16, "bold")).pack(pady=10)

        # Scrollbar and listbox to display available tickets
        scrollbar = Scrollbar(ticket_updation_window)
        scrollbar.pack(side="right", fill="y")

        ticket_listbox = Listbox(ticket_updation_window, font=("Arial", 14), width=50, height=15, yscrollcommand=scrollbar.set)
        ticket_listbox.pack(pady=20)

        for ticket in self.system.tickets:
            ticket_listbox.insert(tk.END, f"{ticket.name} - ${ticket.price}")

        scrollbar.config(command=ticket_listbox.yview)

        # Frame to input new price for the ticket
        input_frame = tk.Frame(ticket_updation_window)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="New Price:", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
        price_entry = tk.Entry(input_frame, font=("Arial", 14), width=15)
        price_entry.grid(row=0, column=1, padx=5, pady=5)

        # Function to update the ticket price
        def update_ticket():
            selected = ticket_listbox.curselection()  # Get selected ticket
            if not selected:
                messagebox.showerror("Error", "No ticket selected!")
                return

            ticket_name = ticket_listbox.get(selected[0]).split(" - ")[0]  # Extract ticket name
            ticket = next((t for t in self.system.tickets if t.name == ticket_name), None)
            if not ticket:
                messagebox.showerror("Error", "Ticket not found!")
                return

            try:
                # Get the new price from the entry field
                new_price = float(price_entry.get().strip())
                if new_price <= 0:
                    raise ValueError("Price must be positive!")
            except ValueError:
                messagebox.showerror("Error", "Invalid price entered!")
                return

            ticket.price = new_price  # Update ticket price
            self.system.save_tickets()  # Save the updated ticket list
            ticket_listbox.delete(selected[0])  # Remove the old ticket entry
            ticket_listbox.insert(selected[0], f"{ticket.name} - ${new_price}")  # Add updated ticket
            messagebox.showinfo("Success", f"{ticket.name} updated successfully!")

        # Button to update the selected ticket
        tk.Button(ticket_updation_window, text="Update Ticket", font=("Arial", 14), command=update_ticket).pack(pady=10)

        # Button to close the ticket updation window
        tk.Button(ticket_updation_window, text="Close", font=("Arial", 14), command=ticket_updation_window.destroy).pack(pady=10)

    # Function to view total tickets sold
    def total_tickets_sold(self):
        total_window = tk.Toplevel(self)
        total_window.title("Total Tickets Sold")
        total_window.geometry("500x400")

        # Label for total tickets sold title
        tk.Label(total_window, text="Total Tickets Sold", font=("Arial", 16, "bold")).pack(pady=10)

        # Listbox to show ticket sales data
        listbox = Listbox(total_window, font=("Arial", 12), width=50, height=10)
        listbox.pack(pady=20)

        # Populate the listbox with sales data
        for ticket in self.system.tickets:
            listbox.insert(tk.END, f"{ticket.name} - Sold: {ticket.sold_count} tickets")

        # Close button to exit the window
        close_button = tk.Button(total_window, text="Close", font=("Arial", 12), width=20, height=2, command=total_window.destroy)
        close_button.pack(pady=10)

# Main application code to initialize the system and run the app
if __name__ == "__main__":
    system = TicketBookingSystem()  # Initialize the ticket booking system
    app = Application(system)  # Create the application instance with the system
    app.mainloop()  # Start the main event loop