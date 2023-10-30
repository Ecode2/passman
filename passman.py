#! /usr/bin/python3
import os, logging
import tkinter, json
from tkinter import ttk
from tkinter import messagebox
from time import sleep
from pathlib import Path

# Import database module 
try:
    from database.database import Database, UnSupportedOs, DatabaseInitError
except ModuleNotFoundError:

    raise RuntimeError("Couldn't find database file")


class Gui:
    
    def __init__(self):
    
        hdlr = logging.StreamHandler()
        hdlr.formatter = logging.Formatter("%(filename)s :: %(funcName)s :: %(levelname)s -> %(message)s")

        self.logger = logging.Logger("gui_logger")
        self.logger.addHandler(hdlr)

        self.logger.info(f"initializing Gui object ...")

        self.top_widget = tkinter.Tk()
        self.top_widget.title("Password Manager")
        self.style_tk = ttk.Style()

        self.height = 580
        self.width = 700
        self.top_widget.geometry(f"{self.width}x{self.height}")

        self.db = Database()

        self.assets = Path(__file__).resolve().parent / "assets"
        self.padlock_icon = tkinter.PhotoImage(file= self.assets/"padlock.png")
        self.key_icon = tkinter.PhotoImage(file= self.assets/"passkey.png")

    def _check_jsonfile(self):
        with open(Path(__file__).parent/"database"/"database_table.json", 'r') as json_file:
            json_data = json.load(json_file)

            if json_data["validate_table"] == "False":
                return False
            elif json_data["validate_table"] == "True":
                return True

    def _authenticate(self, root_password: str):
            
        #creates account if it dosen't exists
        if not self._check_jsonfile():

            self.logger.info("Creatng new account...")

            self.db.create_tables(str(root_password))
            # get encryption key
            self.db.cipher_key(root_password)

            #Clear the login Page
            for widget in self.frame.winfo_children():
                    widget.destroy()
            
            #Starting main app
            self.main_page()

        #checks password if account exists
        elif self._check_jsonfile():

            self.logger.info("Authenticating password...")

            #checks if password is valid
            if self.db.confirm_root(root_password):

                self.logger.info("Password confirmed...")

                # get encryption key
                self.db.cipher_key(root_password)

                #Clear the login Page
                for widget in self.frame.winfo_children():
                    widget.destroy()
                
                #Starting main app
                self.main_page()

            # Display wrong password if password is not valid
            elif not self.db.confirm_root(root_password):
                self.logger.info("Wrong Password...")
                      
                self.password_entry.delete(first=0, last="end")
                self.password_entry.insert(0, "Wrong Password")
                # change checkbox to hide password
                self.password_entry.config(show="")
                self.hide_password_int.set(True)
                self.show_password.place_forget()
                self.hide_password.place(relx = 0.3, rely = 0.7)

    def _show_password(self):
        if self.show_password_int:
            self.password_entry.config(show="")
            self.hide_password_int.set(True)
            self.show_password.place_forget()
            self.hide_password.place(relx = 0.3, rely = 0.7) 

    def _hide_password(self):
        if self.hide_password_int:
            self.password_entry.config(show="*")
            self.show_password_int.set(False)
            self.hide_password.place_forget()
            self.show_password.place(relx = 0.3, rely = 0.7) 

    def show_auth_screen(self):
        
        #create work frame
        self.frame_height = 0.85
        self.frame_width = 0.85
        self.frame_relx = 0.075
        self.frame_rely = 0.075

        self.frame = tkinter.Frame(master = self.top_widget, background = "#e6e6e6" )
        self.frame.place(relx = self.frame_relx, rely = self.frame_rely, relheight = self.frame_height, relwidth = self.frame_width)

        #Determines page type
        if self._check_jsonfile():
            page = "Sign In "
            page_name = "Login To Account"
            page_type = "login"
            authNameRelx = 0.35
            authRelx = 0.385

        elif not self._check_jsonfile():
            page = "Register"
            page_name = "Register New Account"
            page_type = "Create Account"
            authNameRelx = 0.32
            authRelx = 0.3759


        # Create the Authentication bar
        self.lock_icon = tkinter.Label(master=self.frame, image= self.padlock_icon, bd=0, bg="#e6e6e6", highlightthickness=0)
        self.lock_icon.place(relheight = 0.25, relwidth = 0.2, relx = 0.4, rely = 0.005 )

        self.auth = tkinter.Label(master=self.frame, text=page, bg="#e6e6e6", fg="#333333", activeforeground="#333333", font=("monospace", 25, "bold"), highlightthickness=0)
        self.auth.place(relx = authRelx, rely = 0.28)

        self.auth_name = tkinter.Label(master=self.frame, text=page_name, bg="#e6e6e6", fg="#333333", activeforeground="#333333", font=("Helvetica", 18), highlightthickness=0)
        self.auth_name.place(relx = authNameRelx, rely = 0.46)

        # password input section
        self.password_bar = tkinter.Label(master=self.frame, bd=0, bg="#F6F7F9", fg="#333333", activeforeground="#333333", highlightthickness=0)
        self.password_bar.place(relheight = 0.12, relwidth = 0.52, relx = 0.245, rely = 0.575)

        self.passkey_icon = tkinter.Label(master=self.frame, image= self.key_icon, bd=0, bg="#F6F7F9", highlightthickness=0)
        self.passkey_icon.place(relx = 0.25, rely = 0.593)

        self.password_name = tkinter.Label(master=self.frame, text="Root Password:", bg="#F6F7F9", fg="#333333", activeforeground="#333333", font=("Helvetica", 16),  highlightthickness=0)
        self.password_name.place(relx = 0.31, rely = 0.58)

        self.password_entry = tkinter.Entry(bd=0, bg="#f6f7f9", fg="#333333", font=("Helvetica", 14), show="*", highlightthickness=0)
        self.password_entry.place(relheight = 0.045, relwidth = 0.35, relx = 0.35, rely = 0.61)
        self.password_entry.focus()

        #show and hide password section
        self.show_password_int = tkinter.BooleanVar()
        self.show_password = tkinter.Checkbutton(self.frame, variable=self.show_password_int, text="Show Password", bd=0, bg="#e6e6e6", fg="#333333", activeforeground="#333333", command=self._show_password, highlightthickness=0)
        self.show_password.place(relx = 0.3, rely = 0.7)

        self.hide_password_int = tkinter.BooleanVar()
        self.hide_password = tkinter.Checkbutton(self.frame, variable=self.hide_password_int, text="Hide Password", bd=0, bg="#e6e6e6", fg="#333333", activeforeground="#333333", command=self._hide_password, highlightthickness=0)
              
        # login or signup button section
        self.confirm_btn = tkinter.Button(master = self.frame, background = "#e6e6e6", fg="#333333", activeforeground="#333333", highlightbackground="gray", activebackground="lightgray", relief="flat", text = page_type, font=("monospace", 22, "bold"), command = lambda: self._authenticate(self.password_entry.get()))
        self.confirm_btn.place(relheight = 0.1, relwidth = 0.52, relx = 0.245, rely = 0.8)


    # Application function logic
    def logout(self):
        self.logger.info("Logging out...")

        # Remove the main page
        self.frame.place_forget()
        self.display_frame.place_forget()
        self.logout_frame.place_forget()
        self.function_frame.place_forget()
        
        # Go to login page
        self.show_auth_screen()


    def _submit_password(self, name: str, description: str, password: str):
        
        name = str(name); description= str(description); password = str(password)

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.11)

        # Exit if entris are not filled
        if name == "" or description == "" or password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        # Add password to database and update screen
        self.db.append_password(name, description, password)
        info_label.configure(text="")
        info_label.configure(text="Password Saved")

        self.name_input.delete(first=0, last="end")
        self.description_input.delete(first=0, last="end")
        self.password_input.delete(first=0, last="end")


    def add_new_password(self):

        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Add A New Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        # Username label with input
        name_label = tkinter.Label(master=self.display_frame, text="Name:", font=("Helvetica", 16))
        name_label.place(relx=0.05, rely=0.2)
        self.name_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.name_input.place(relx=0.34, rely=0.2, relwidth=0.65, relheight=0.05)
        self.name_input.focus()

        # Description label with input
        description_label = tkinter.Label(master=self.display_frame, text="Description:", font=("Helvetica", 16))
        description_label.place(relx=0.05, rely=0.3)
        self.description_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.description_input.place(relx=0.34, rely=0.3, relwidth=0.65, relheight=0.05)

        # Password label with input
        password_label = tkinter.Label(master=self.display_frame, text="Password:", font=("Helvetica", 16))
        password_label.place(relx=0.05, rely=0.4)
        self.password_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.password_input.place(relx=0.34, rely=0.4, relwidth=0.65, relheight=0.05)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Submit", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._submit_password(self.name_input.get(), self.description_input.get(), self.password_input.get()))
        submit_btn.place(relx=0.05, rely=0.5, relwidth=0.3, relheight=0.08)


    def _search_by_name(self):

        self.search_by = True
        if self.search_name_int:
            self.type_label.configure(text = "")
            self.type_label.configure(text = "By Name:")

            # switch checkbox
            self.search_name.place_forget()
            self.search_id.place(relx=0.05, rely=0.3)
            self.search_id_int = tkinter.BooleanVar(value=False)
    
    def _search_by_id(self):

        self.search_by = False
        if self.search_id_int:
            self.type_label.configure(text = "")
            self.type_label.configure(text = "By ID:")

            # switch checkbox
            self.search_id.place_forget()
            self.search_name.place(relx=0.05, rely=0.3)
            self.search_name_int = tkinter.BooleanVar(value=False)

    def _add_password(self):

        if self.show_pass_int:
            # add password
            self.show_pass.place_forget()
            self.hide_pass.place(relx=0.5, rely=0.3)
            self.show = True

    def _remove_password(self):

        if self.hide_pass_int:
            # remove password
            self.hide_pass.place_forget()
            self.show_pass.place(relx=0.5, rely=0.3)    
            self.show = False                      


    def _search_password(self, search: str):
        search = str(search)

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)
        
        if self.search_by:
            passwords = self.db.get_password(search, name=True)

            if passwords == []:
                info_label.configure(text="")
                info_label.configure(text="No Matching Name found")
                return

            # Loop through passwords
            elif len(passwords) > 0:

                # Password grid and pady location
                id_grid = 1
                name_grid = 2
                description_grid = 3
                password_grid = 4
                label_space_grid = 6

                id_pady = 5
                
                # Reset the display screen
                for widget in self.display_frame.winfo_children():
                    widget.destroy()

                # Add horizontal and vertical scroll
                self.display_canvas = tkinter.Canvas(master=self.frame, borderwidth=2, relief="flat", highlightbackground="gray", highlightthickness=1)
                self.display_canvas.place(relx= 0.4, rely= 0, relheight = 1, relwidth = 0.6)

                self.horizontal_scroll = ttk.Scrollbar(master=self.frame, orient="horizontal", command=self.display_canvas.xview)
                self.horizontal_scroll.place(relx=0.4, rely=0.975, relwidth=0.585)
                self.vertical_scroll = ttk.Scrollbar(master=self.frame, orient="vertical", command=self.display_canvas.yview)
                self.vertical_scroll.place(relx=0.985, rely=0, relheight=1)

                self.display_canvas.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)
                self.display_canvas.bind( "<Configure>", lambda e: self.display_canvas.configure(scrollregion= self.display_canvas.bbox("all")))

                self.display_frame = tkinter.Frame(master=self.display_canvas)
                self.display_canvas.create_window((0,0), window=self.display_frame, anchor="nw")

                self.width = 701
                self.height = 581
                self.top_widget.geometry(f"{self.width}x{self.height}")

                # Display search result
                title = tkinter.Label(master=self.display_frame, text="Search For Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
                title.grid(row=0, column=0, columnspan=2)

                for password in passwords:

                    id_label = tkinter.Label(master=self.display_frame, text="ID:", font=("Helvetica", 16), anchor="w", justify="left")
                    id_label.grid(row=id_grid, column=0, sticky="w", padx=20, pady=id_pady)
                    password_id = tkinter.Label(master=self.display_frame, text=password[0], font=("Helvetica", 16))
                    password_id.grid(row=id_grid, column=1, sticky="w", padx=20, pady=id_pady)

                    name_label = tkinter.Label(master=self.display_frame, text="Name:", font=("Helvetica", 16))
                    name_label.grid(row=name_grid, column=0, sticky="w", padx=20, pady=5)
                    password_name = tkinter.Label(master=self.display_frame, text=password[1], font=("Helvetica", 16))
                    password_name.grid(row=name_grid, column=1, sticky="w", padx=20, pady=5)

                    description_label = tkinter.Label(master=self.display_frame, text="Description:", font=("Helvetica", 16))
                    description_label.grid(row=description_grid, sticky="w", padx=20, column=0, pady=5)
                    password_description = tkinter.Label(master=self.display_frame, text=password[2], font=("Helvetica", 16))
                    password_description.grid(row=description_grid, sticky="w", padx=20, column=1, pady=5)

                    label_space = tkinter.Label(master=self.display_frame, font=("Helvetica", 16))
                    label_space.grid(row=label_space_grid, sticky="w", padx=20, column=0, pady=5)

                    password_label = tkinter.Label(master=self.display_frame, text="Password:", font=("Helvetica", 16))
                    password_pass = tkinter.Label(master=self.display_frame, text=password[3], font=("Helvetica", 16))
                    if self.show:
                        password_label.grid(row=password_grid, column=0, sticky="w", padx=20, pady=5)
                        password_pass.grid(row=password_grid, column=1, sticky="w", padx=20, pady=5)

                    # push down for next password
                    id_grid += 5
                    name_grid += 5
                    description_grid += 5
                    password_grid += 5
                    label_space_grid += 5

        # Search by Id
        if not self.search_by:

            try:
                search = int(search)
            except ValueError:
                info_label.configure(text="")
                info_label.configure(text="Search Must Be A Number")
                return 

            if search == "1":
                info_label.configure(text="")
                info_label.configure(text="Can't search Root Password")
                return

            password = self.db.get_password(search)
            if password == []:
                info_label.configure(text="")
                info_label.configure(text="No Matching ID found")
                return

            # Reset the display screen
            for widget in self.display_frame.winfo_children():
                widget.destroy()

            # Add horizontal and vertical scroll
            self.display_canvas = tkinter.Canvas(master=self.frame, borderwidth=2, relief="flat", highlightbackground="gray", highlightthickness=1)
            self.display_canvas.place(relx= 0.4, rely= 0, relheight = 1, relwidth = 0.6)

            self.horizontal_scroll = ttk.Scrollbar(master=self.frame, orient="horizontal", command=self.display_canvas.xview)
            self.horizontal_scroll.place(relx=0.4, rely=0.98, relwidth=0.598)

            self.display_canvas.configure(xscrollcommand=self.horizontal_scroll.set)
            self.display_canvas.bind( "<Configure>", lambda e: self.display_canvas.configure(scrollregion= self.display_canvas.bbox("all")))

            self.display_frame = tkinter.Frame(master=self.display_canvas)
            self.display_canvas.create_window((0,0), window=self.display_frame, anchor="nw")

            self.width = 701
            self.top_widget.geometry(f"{self.width}x{self.height}")

            # Display search result
            title = tkinter.Label(master=self.display_frame, text="Search For Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
            title.grid(row=0, column=0, sticky="w", padx=20, columnspan=2)

            id_label = tkinter.Label(master=self.display_frame, text="ID:", font=("Helvetica", 16))
            id_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)
            password_id = tkinter.Label(master=self.display_frame, text=password[0], font=("Helvetica", 16))
            password_id.grid(row=1, column=1, sticky="w", padx=20, pady=5)

            name_label = tkinter.Label(master=self.display_frame, text="Name:", font=("Helvetica", 16))
            name_label.grid(row=2, column=0, sticky="w", padx=20, pady=5)
            password_name = tkinter.Label(master=self.display_frame, text=password[1], font=("Helvetica", 16))
            password_name.grid(row=2, column=1, sticky="w", padx=20, pady=5)

            description_label = tkinter.Label(master=self.display_frame, text="Description:", font=("Helvetica", 16))
            description_label.grid(row=3, column=0, sticky="w", padx=20, pady=5)
            password_description = tkinter.Label(master=self.display_frame, text=password[2], font=("Helvetica", 16))
            password_description.grid(row=3, column=1, sticky="w", padx=20, pady=5)

            label_space = tkinter.Label(master=self.display_frame, font=("Helvetica", 16))
            label_space.grid(row=5, sticky="w", padx=20, column=0, pady=5)

            password_label = tkinter.Label(master=self.display_frame, text="Password:", font=("Helvetica", 16))
            password_pass = tkinter.Label(master=self.display_frame, text=password[3], font=("Helvetica", 16))
            if self.show:
                password_label.grid(row=4, column=0, sticky="w", padx=20, pady=5)
                password_pass.grid(row=4, column=1, sticky="w", padx=20, pady=5)


                
    def get_1_password(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Search For Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        search_label = tkinter.Label(master=self.display_frame, text="Search:", font=("Helvetica", 16))
        search_label.place(relx=0.05, rely=0.2)

        self.type_label = tkinter.Label(master=self.display_frame, text="By ID:", anchor="w", justify="left", bg="#e6e6e6", font=("Helvetica", 11))
        self.type_label.place(relx=0.34, rely=0.18, relwidth=0.65, relheight=0.05)

        search_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        search_input.place(relx=0.34, rely=0.22, relwidth=0.65, relheight=0.05)
        search_input.focus()

        self.search_by = False
        # Search by Name
        self.search_name_int = tkinter.BooleanVar()
        self.search_name = tkinter.Checkbutton(self.display_frame, variable=self.search_name_int, text="Search By Name", font=("Helvetica", 12), command= self._search_by_name, highlightthickness=0)
        self.search_name.place(relx=0.05, rely=0.3)

        # Search by id
        self.search_id_int = tkinter.BooleanVar()
        self.search_id = tkinter.Checkbutton(self.display_frame, variable=self.search_id_int, text="Search By ID", font=("Helvetica", 12), command= self._search_by_id, highlightthickness=0)

        # Show and hide password
        self.show = False
        self.show_pass_int = tkinter.BooleanVar()
        self.show_pass = tkinter.Checkbutton(self.display_frame, variable=self.show_pass_int, text="Add Password", font=("Helvetica", 12), command= self._add_password, highlightthickness=0)
        self.show_pass.place(relx=0.5, rely=0.3)

        self.hide_pass_int = tkinter.BooleanVar()
        self.hide_pass = tkinter.Checkbutton(self.display_frame, variable=self.hide_pass_int, text="Remove Password", font=("Helvetica", 12), command= self._remove_password, highlightthickness=0)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Search", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._search_password(search_input.get()))
        submit_btn.place(relx=0.05, rely=0.4, relwidth=0.3, relheight=0.08)
    

    # Show and hide passwords
    def _show_all_password(self):

        self.show_all = True
        if self.show_all_pass_int:
            self.show_all_pass.place_forget()
            self.hide_all_pass.place(relx=0.05, rely=0.2)

    def _not_show_all_password(self):
    
        self.show_all = False
        if self.not_show_all_pass_int:
            self.hide_all_pass.place_forget()
            self.show_all_pass.place(relx=0.05, rely=0.2)

    def _get_all_password(self):
        print("starting")

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)
        
        passwords = self.db.get_passwords()

        if passwords == []:
            info_label.configure(text="")
            info_label.configure(text="No Password Saved")
            return

        # Loop through passwords

        # Password grid and pady location
        id_grid = 1
        name_grid = 2
        description_grid = 3
        password_grid = 4
        label_space_grid = 5
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Add horizontal and vertical scroll
        self.display_canvas = tkinter.Canvas(master=self.frame, borderwidth=2, relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_canvas.place(relx= 0.4, rely= 0, relheight = 1, relwidth = 0.6)

        self.horizontal_scroll = ttk.Scrollbar(master=self.frame, orient="horizontal", command=self.display_canvas.xview)
        self.horizontal_scroll.place(relx=0.4, rely=0.98, relwidth=0.583)
        self.vertical_scroll = ttk.Scrollbar(master=self.frame, orient="vertical", command=self.display_canvas.yview)
        self.vertical_scroll.place(relx=0.983, rely=0, relheight=1)

        self.display_canvas.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)
        self.display_canvas.bind( "<Configure>", lambda e: self.display_canvas.configure(scrollregion= self.display_canvas.bbox("all")))

        self.display_frame = tkinter.Frame(master=self.display_canvas)
        self.display_canvas.create_window((0,0), window=self.display_frame, anchor="nw")

        self.width = 702
        self.height = 582
        self.top_widget.geometry(f"{self.width}x{self.height}")

        # Display search result
        title = tkinter.Label(master=self.display_frame, text="Show Saved Passwords", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=20, columnspan=2)

        for password in passwords:

            id_label = tkinter.Label(master=self.display_frame, text="ID:", font=("Helvetica", 16), anchor="w", justify="left")
            id_label.grid(row=id_grid, column=0, sticky="w", padx=20, pady=5)
            
            password_id = tkinter.Label(master=self.display_frame, text=password[0], font=("Helvetica", 16))
            password_id.grid(row=id_grid, column=1, sticky="w", padx=20, pady=5)
            

            name_label = tkinter.Label(master=self.display_frame, text="Name:", font=("Helvetica", 16))
            name_label.grid(row=name_grid, column=0, sticky="w", padx=20, pady=5)
            
            password_name = tkinter.Label(master=self.display_frame, text=password[1], font=("Helvetica", 16))
            password_name.grid(row=name_grid, column=1, sticky="w", padx=20, pady=5)
            

            description_label = tkinter.Label(master=self.display_frame, text="Description:", font=("Helvetica", 16))
            description_label.grid(row=description_grid, column=0, sticky="w", padx=20, pady=5)
            password_description = tkinter.Label(master=self.display_frame, text=password[2], font=("Helvetica", 16))
            password_description.grid(row=description_grid, column=1, sticky="w", padx=20, pady=5)

            label_space = tkinter.Label(master=self.display_frame, font=("Helvetica", 16))
            label_space.grid(row=label_space_grid, sticky="w", padx=20, column=0, pady=5)

            password_label = tkinter.Label(master=self.display_frame, text="Password:", font=("Helvetica", 16))
            password_pass = tkinter.Label(master=self.display_frame, text=password[3], font=("Helvetica", 16))
            if self.show_all:
                password_label.grid(row=password_grid, column=0, sticky="w", padx=20, pady=5)
                password_pass.grid(row=password_grid, column=1, sticky="w", padx=20, pady=5)

            # push down for next password
            id_grid += 5
            name_grid += 5
            description_grid += 5
            password_grid += 5
            label_space_grid += 5


    def get_all_password(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Show Saved Passwords", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.02, rely=0.01)
        
        #show and hide all passwords
        self.show_all = False
        self.show_all_pass_int = tkinter.BooleanVar()
        self.show_all_pass = tkinter.Checkbutton(self.display_frame, variable=self.show_all_pass_int, text="Add All Password", font=("Helvetica", 12), command= self._show_all_password, highlightthickness=0)
        self.show_all_pass.place(relx=0.05, rely=0.2)
        
        self.not_show_all_pass_int = tkinter.BooleanVar()
        self.hide_all_pass = tkinter.Checkbutton(self.display_frame, variable=self.not_show_all_pass_int, text="Remove All Password", font=("Helvetica", 12), command= self._not_show_all_password, highlightthickness=0)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Get Passwords", anchor="center", justify="center", font=("Helvetica", 18), command= self._get_all_password)
        submit_btn.place(relx=0.05, rely=0.25, relwidth=0.48, relheight=0.07)

    def _update_password(self, id: str, name: str, description: str, password: str):

        id=str(id); name= str(name); description= str(description); password= str(password)

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)

        # Error handling
        if name == "" and description == "" and password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill At Least 1 Section")
            return
        if id == "":
            info_label.configure(text="")
            info_label.configure(text="Password ID Compulsory")
            return

        try:
            id = int(id)
        except ValueError:
            info_label.configure(text="")
            info_label.configure(text="ID Must Be A Number")
            return

        if id == 1:
            info_label.configure(text="")
            info_label.configure(text="Update Not Allowed")
            return

        if not self.db.confirm_id(id):
            info_label.configure(text="")
            info_label.configure(text="Password Doesn't Exist")
            return

        # Add password to database and update screen
        self.db.update_password(id, name=name, description=description, password=password)
        info_label.configure(text="")
        info_label.configure(text="Details Updated")

        self.update_id_input.delete(first=0, last="end")
        self.update_name_input.delete(first=0, last="end")
        self.update_description_input.delete(first=0, last="end")
        self.update_password_input.delete(first=0, last="end")

    def update_1_password(self):

        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Update A password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        id_label = tkinter.Label(master=self.display_frame, text="Password ID:", font=("Helvetica", 16))
        id_label.place(relx=0.05, rely=0.2)
        type_label = tkinter.Label(master=self.display_frame, text="Compulsory:", anchor="w", justify="left", bg="#e6e6e6", font=("Helvetica", 11))
        type_label.place(relx=0.37, rely=0.19, relwidth=0.62, relheight=0.03)
        self.update_id_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 13), highlightthickness=0)
        self.update_id_input.place(relx=0.37, rely=0.215, relwidth=0.62, relheight=0.05)
        self.update_id_input.focus()

        # Username label with input
        name_label = tkinter.Label(master=self.display_frame, text="Name:", font=("Helvetica", 16))
        name_label.place(relx=0.05, rely=0.3)
        name_option_label = tkinter.Label(master=self.display_frame, text="optional:", anchor="w", justify="left", bg="#e6e6e6", font=("Helvetica", 11))
        name_option_label.place(relx=0.37, rely=0.29, relwidth=0.62, relheight=0.03)
        self.update_name_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 13), highlightthickness=0)
        self.update_name_input.place(relx=0.37, rely=0.315, relwidth=0.62, relheight=0.05)

        # Description label with input
        description_label = tkinter.Label(master=self.display_frame, text="Description:", font=("Helvetica", 16))
        description_label.place(relx=0.05, rely=0.4)
        description_option_label = tkinter.Label(master=self.display_frame, text="optional:", anchor="w", justify="left", bg="#e6e6e6", font=("Helvetica", 11))
        description_option_label.place(relx=0.37, rely=0.39, relwidth=0.62, relheight=0.03)
        self.update_description_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 13), highlightthickness=0)
        self.update_description_input.place(relx=0.37, rely=0.415, relwidth=0.62, relheight=0.05)

        # Password label with input
        password_label = tkinter.Label(master=self.display_frame, text="Password:", font=("Helvetica", 16))
        password_label.place(relx=0.05, rely=0.5)
        password_option_label = tkinter.Label(master=self.display_frame, text="optional:", anchor="w", justify="left", bg="#e6e6e6", font=("Helvetica", 11))
        password_option_label.place(relx=0.37, rely=0.49, relwidth=0.62, relheight=0.03)
        self.update_password_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 13), highlightthickness=0)
        self.update_password_input.place(relx=0.37, rely=0.515, relwidth=0.62, relheight=0.05)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Update", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._update_password(self.update_id_input.get(), self.update_name_input.get(), self.update_description_input.get(), self.update_password_input.get()))
        submit_btn.place(relx=0.05, rely=0.6, relwidth=0.3, relheight=0.08)

    
    def _delete_password(self, id: str, root_password: str):

        id=str(id); root_password= str(root_password);

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)

        # Error handling
        if id == "" or root_password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        try:
            id = int(id)
        except ValueError:
            info_label.configure(text="")
            info_label.configure(text="ID Must Be A Number")
            return

        if id == 1:
            info_label.configure(text="")
            info_label.configure(text="Deletion Not Allowed")
            return

        if not self.db.confirm_id(id):
            info_label.configure(text="")
            info_label.configure(text="Password Doesn't Exist")
            return

        if not self.db.confirm_root(root_password):
            info_label.configure(text="")
            info_label.configure(text="Root Password Incorrect")
            return

        # delete selected password
        self.db.delete_password(id, root_password)
        info_label.configure(text="")
        info_label.configure(text="Password Deleted")

        self.delete_root_input.delete(first=0, last="end")
        self.delete_id_input.delete(first=0, last="end")

    def delete_1_password(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Remove A password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        root_label = tkinter.Label(master=self.display_frame, text="Root Password:", font=("Helvetica", 16))
        root_label.place(relx=0.05, rely=0.2)
        self.delete_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.delete_root_input.place(relx=0.425, rely=0.2, relwidth=0.57, relheight=0.05)
        self.delete_root_input.focus()

        id_label = tkinter.Label(master=self.display_frame, text="Password ID:", font=("Helvetica", 16))
        id_label.place(relx=0.05, rely=0.3)
        self.delete_id_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 13), highlightthickness=0)
        self.delete_id_input.place(relx=0.425, rely=0.3, relwidth=0.57, relheight=0.05)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Delete", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._delete_password(self.delete_id_input.get(), self.delete_root_input.get()))
        submit_btn.place(relx=0.05, rely=0.4, relwidth=0.3, relheight=0.08)


    def _confirm(self, purge: bool= False, update_root: bool = False, del_account: bool = False):

        if purge:
            response = messagebox.askyesno(title="Delete All Password", message="Are you sure you want to\n   Delete all password")
            return response

        elif update_root:
            response = messagebox.askyesno(title="Update Root Password", message="Are you sure you want to\n  Update root password")
            return response

        elif del_account:
            response = messagebox.askyesno(title="Delete Account", message="Are you sure you want to\n  Delete Your Account")
            return response

        elif not purge and not update_root and not del_account:
            return "Mark one parameter as true"

        elif purge and update_root and del_account:
            return "Mark only one parameter as true"
    
    def _delete_all_password(self, root_password):

        root_password= str(root_password);

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)

        # Error handling
        if root_password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        if not self.db.confirm_root(root_password):
            info_label.configure(text="")
            info_label.configure(text="Root Password Incorrect")
            return

        # TODO: create a notification function
        # TODO: call the notification function
        # TODO: call the remainig code if function is yes but cancle if no

        response = self._confirm(purge=True)
        
        if response:
            # delete All password
            self.db.purge(root_password)
            info_label.configure(text="")
            info_label.configure(text="All Passwords Deleted")
            self.delete_all_root_input.delete(first=0, last="end")
        
        elif not response:
            info_label.configure(text="")
            info_label.configure(text="Operation Cancelled")
            self.delete_all_root_input.delete(first=0, last="end")

    def delete_all_password(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Delete All Passwords", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        root_label = tkinter.Label(master=self.display_frame, text="Root Password:", font=("Helvetica", 16))
        root_label.place(relx=0.05, rely=0.2)
        self.delete_all_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.delete_all_root_input.place(relx=0.425, rely=0.2, relwidth=0.57, relheight=0.05)
        self.delete_all_root_input.focus()

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Delete", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._delete_all_password(self.delete_all_root_input.get()))
        submit_btn.place(relx=0.05, rely=0.3, relwidth=0.3, relheight=0.08)

    def _update_root_password(self, root_password: str, new_root: str, confirm_root: str):
        
        root_password= str(root_password); new_root = str(new_root); confirm_root = str(confirm_root)

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1, relwidth=0.9)

        # Error handling
        if root_password == "" or new_root == "" or confirm_root == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        if not self.db.confirm_root(root_password):
            info_label.config(text="Root Password Incorrect")
            return

        if new_root != confirm_root:
            info_label.configure(text="")
            info_label.configure(text="Passwords Don't Match")
            return

        response = self._confirm(update_root=True)
        
        if response:
            # update root password
            self.db.update_root_password(root_password, new_root)

            info_label.configure(text="")
            info_label.configure(text="Root Password Updated")

            self.current_root_input.delete(first=0, last="end")
            self.new_root_input.delete(first=0, last="end")
            self.confirm_root_input.delete(first=0, last="end")
        
        elif not response:
            info_label.configure(text="")
            info_label.configure(text="Operation Cancelled")
            
            self.current_root_input.delete(first=0, last="end")
            self.new_root_input.delete(first=0, last="end")
            self.confirm_root_input.delete(first=0, last="end")

    def change_root_password(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Update Root Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.03, rely=0.01)

        root_label = tkinter.Label(master=self.display_frame, text="Old Password:", font=("Helvetica", 15))
        root_label.place(relx=0.03, rely=0.2)
        self.current_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.current_root_input.place(relx=0.45, rely=0.2, relwidth=0.545, relheight=0.05)
        self.current_root_input.focus()

        new_root_label = tkinter.Label(master=self.display_frame, text="New Password:", font=("Helvetica", 15))
        new_root_label.place(relx=0.03, rely=0.3)
        self.new_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.new_root_input.place(relx=0.45, rely=0.3, relwidth=0.545, relheight=0.05)
        
        confirm_root_label = tkinter.Label(master=self.display_frame, text="Confirm Password:", font=("Helvetica", 15))
        confirm_root_label.place(relx=0.03, rely=0.4)
        self.confirm_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.confirm_root_input.place(relx=0.45, rely=0.4, relwidth=0.545, relheight=0.05)

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Update", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._update_root_password(self.current_root_input.get(), self.new_root_input.get(), self.confirm_root_input.get()))
        submit_btn.place(relx=0.05, rely=0.5, relwidth=0.3, relheight=0.08)

    def _delete_account(self, root_password: str):

        root_password = str(root_password)

        # Information Display Label
        info_label = tkinter.Label(master=self.display_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0.05, rely=0.1)

        # Error handling
        if root_password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        if not self.db.confirm_root(root_password):
            info_label.configure(text="")
            info_label.configure(text="Root Password Incorrect")
            return

        # TODO: create a notification function
        # TODO: call the notification function
        # TODO: call the remainig code if function is yes but cancle if no

        response = self._confirm(del_account= True)
        
        if response:

            # delete Account
            info_label.configure(text="")
            info_label.configure(text="Account Deleted")
            self.db.delete_account(root_password)

            sleep(0.5)
            self.logout()
        
        elif not response:
            info_label.configure(text="")
            info_label.configure(text="Operation Cancelled")
            self.delete_account_root_input.delete(first=0, last="end")

    def delete_account(self):
        
        # Reset the display screen
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Create explanation label
        title = tkinter.Label(master=self.display_frame, text="Delete Account", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0.05, rely=0.01)

        root_label = tkinter.Label(master=self.display_frame, text="Root Password:", font=("Helvetica", 16))
        root_label.place(relx=0.05, rely=0.2)
        self.delete_account_root_input = tkinter.Entry(master=self.display_frame, bd=0, bg="#e6e6e6", font=("Helvetica", 14), highlightthickness=0)
        self.delete_account_root_input.place(relx=0.425, rely=0.2, relwidth=0.57, relheight=0.05)
        self.delete_account_root_input.focus()

        # Submit Button
        submit_btn = tkinter.Button(master=self.display_frame, highlightbackground="gray", activebackground="#e6e6e6", relief="flat", text = "Delete Account", anchor="center", justify="center", font=("Helvetica", 18), command= lambda: self._delete_account(self.delete_account_root_input.get()))
        submit_btn.place(relx=0.05, rely=0.3, relwidth=0.3, relheight=0.08)        

    def main_page(self):

        # Resizing work frame
        self.frame_width = 1
        self.frame_height = 1
        self.frame_relx = 0
        self.frame_rely = 0

        self.logger.info("Cueing Main screen")

        # Display frame
        self.frame = tkinter.Frame(master = self.top_widget)
        self.frame.place(relx = self.frame_relx, rely = self.frame_rely, relheight = self.frame_height, relwidth = self.frame_width)

        self.display_frame = tkinter.LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_frame.place(relx = 0.4, rely = 0, relheight = 1, relwidth = 0.6)

        # Start default function
        self.add_new_password()


        # Application functions and commands
        # Logout section
        self.logout_frame = tkinter.LabelFrame(master=self.frame, borderwidth=1, bg="#e6e6e6", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.logout_frame.place(rely=0, relx=0, relwidth=0.4, relheight=0.1)

        # TODO: add a logout icon to the text
        self.logout_btn = tkinter.Button(master=self.logout_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Logout", font=("monospace", 17, "bold"), command = self.logout)
        self.logout_btn.place(relheight= 0.7, relwidth= 0.85, relx= 0.05, rely= 0.15)


        # Function section
        self.function_frame = tkinter.LabelFrame(master=self.frame, borderwidth=1, bg="#e6e6e6", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.function_frame.place(rely=0.1, relx=0, relwidth=0.4, relheight=0.6)

        # Add password fuction
        self.add_password = tkinter.Button(master=self.function_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Add New Password", anchor="w", justify="left", font=("monospace", 12), command = self.add_new_password)
        self.add_password.place(relheight= 0.1, relwidth= 0.85, relx= 0.05, rely= 0.06)

        # Get a password
        self.get_password = tkinter.Button(master=self.function_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Search Password", anchor="w", justify="left", font=("monospace", 12), command = self.get_1_password)
        self.get_password.place(relheight= 0.1, relwidth= 0.85, relx= 0.05, rely= 0.2)

        # Get all password
        self.show_password = tkinter.Button(master=self.function_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Show All Password", anchor="w", justify="left", font=("monospace", 12), command = self.get_all_password)
        self.show_password.place(relheight= 0.1, relwidth= 0.85, relx= 0.05, rely= 0.35)

        # Update a password
        self.update_password = tkinter.Button(master=self.function_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Update A Password", anchor="w", justify="left", font=("monospace", 12), command = self.update_1_password)
        self.update_password.place(relheight= 0.1, relwidth= 0.85, relx= 0.05, rely= 0.5)

        # Delete a password
        self.delete_password = tkinter.Button(master=self.function_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Delete A Password", anchor="w", justify="left", font=("monospace", 12), command = self.delete_1_password)
        self.delete_password.place(relheight= 0.1, relwidth= 0.85, relx= 0.05, rely= 0.65)


        # Important Account section
        self.important_frame = tkinter.LabelFrame(master=self.frame, borderwidth=1, bg="#e6e6e6", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.important_frame.place(rely=0.7, relx=0, relwidth=0.4, relheight=0.2)

        # Delete all password
        self.purge_password = tkinter.Button(master=self.important_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Delete All Password", anchor="w", justify="left", font=("monospace", 12), command = self.delete_all_password)
        self.purge_password.place(relheight= 0.3, relwidth= 0.85, relx= 0.05, rely= 0.15)

        # Update root password
        self.update_root = tkinter.Button(master=self.important_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Change Root Password", anchor="w", justify="left", font=("monospace", 12), command = self.change_root_password)
        self.update_root.place(relheight= 0.3, relwidth= 0.85, relx= 0.05, rely= 0.55)


        # Delete account section add a popup option when the button is clicked
        self.delete_frame = tkinter.LabelFrame(master=self.frame, borderwidth=1, bg="#e6e6e6", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.delete_frame.place(rely=0.9, relx=0, relwidth=0.4, relheight=0.1)

        self.delete_btn = tkinter.Button(master=self.delete_frame, bg="#e6e6e6", relief="flat", activebackground="lightgray", highlightbackground="#e6e6e6", text = "Delete Account", font=("monospace", 17, "bold"), command = self.delete_account)
        self.delete_btn.place(relheight= 0.7, relwidth= 0.85, relx= 0.05, rely= 0.15)

    def __del__(self):
    
        self.logger.info("destroying Gui object ...")
        self.top_widget.quit()


if __name__ == "__main__":
    
    gui = Gui()

    gui.show_auth_screen()

    gui.top_widget.mainloop()
