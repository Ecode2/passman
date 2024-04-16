#! /usr/bin/python3
import json, logging, random
import ttkbootstrap as tb
from ttkbootstrap.icons import Icon
from tkinter import *
from tkinter import messagebox
from time import sleep
from pathlib import Path

# Import database module 
try:
    from database import database
except ModuleNotFoundError:

    raise RuntimeError("Couldn't find database file")


class Gui:
    
    def __init__(self):
    
        hdlr = logging.StreamHandler()
        hdlr.formatter = logging.Formatter("%(filename)s :: %(funcName)s :: %(levelname)s -> %(message)s")

        self.logger = logging.Logger("gui_logger")
        self.logger.addHandler(hdlr)

        self.logger.info(f"initializing Gui object ...")

        themes = ["minty", "superhero", "darkly", "cosmo", "flatly", 
                  "journal", "litera", "lumen", "pulse", "sandstone", "united", 
                  "yeti", "morph", "simplex", "cerculean", "solar", "cybord", "vapor" ]
        theme = random.choice(themes)

        self.top_widget = tb.Window(themename=theme, iconphoto="assets/padlock.png") #themename="superhero") themename="darkly")  Tk()
        self.top_widget.title("Password Manager")

        self.height = 580
        self.width = 700
        self.top_widget.geometry(f"{self.width}x{self.height}")

        self.db = database.Database()

        self.assets = Path(__file__).resolve().parent / "assets"
        self.padlock_icon = PhotoImage(file= self.assets/"padlock.png")
        self.key_icon = PhotoImage(file= self.assets/"passkey.png")

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
            for widget in self.settings_frame.winfo_children():
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
                self.show_password_int.set(True)
                
                self.show_password.configure(text="")
                self.show_password.configure(text="Hide Password")


    def _show_password(self):
        if self.show_password_int.get():

            self.password_entry.config(show="")
            self.show_password_int.set(True)
            
            self.show_password.configure(text="")
            self.show_password.configure(text="Hide Password")

        else:
            self.password_entry.config(show="*")
            self.show_password_int.set(False)
            
            self.show_password.configure(text="")
            self.show_password.configure(text="Show Password")

    def show_auth_screen(self):
        
        #create work frame
        self.frame_height = 0.85
        self.frame_width = 0.85
        self.frame_relx = 0.075
        self.frame_rely = 0.075

        self.frame = tb.Frame(master = self.top_widget) #Frame(master = self.top_widget, background = "#e6e6e6" )
        self.frame.place(relx = self.frame_relx, rely = self.frame_rely, relheight = self.frame_height, relwidth = self.frame_width)

        #Determines page type
        if self._check_jsonfile():
            page = "Sign In "
            page_name = "Login To Account"
            page_type = "login"
            authNameRelx = 0.13
            authRelx = 0.45

        elif not self._check_jsonfile():
            page = "Register"
            page_name = "Register New Account"
            page_type = "Create Account"
            authNameRelx = 0.1
            authRelx = 0.45

        # Create the Authentication bar
        self.lock_icon = Label(master=self.frame, image= self.padlock_icon, bd=0, bg="#e6e6e6", highlightthickness=0)
        self.lock_icon.place(relheight = 0.25, relwidth = 0.2, relx = 0.23, rely = 0 )

        self.auth = Label(master=self.frame, text=page, bg="#e6e6e6", fg="#333333", activeforeground="#333333", font=("monospace", 25, "bold"), highlightthickness=0)
        self.auth.place(relx = authRelx, rely = 0.05)


        # Registration form 
        self.form_frame = tb.Labelframe(master=self.frame)
        self.form_frame.place(relheight = 0.6, relwidth = 0.6, relx = 0.2, rely = 0.35 )

        self.auth_name = tb.Label(master=self.form_frame, text=page_name, font=("Helvetica", 18))
        self.auth_name.place(relx = authNameRelx, rely = 0.1)

        self.passkey_icon = tb.Label(master=self.form_frame, image= self.key_icon)
        self.passkey_icon.place(relx = authNameRelx, rely = 0.38)

        self.password_name = tb.Label(master=self.form_frame, text="Root:", font=("Helvetica", 13))#, bg="#F6F7F9", fg="#333333", activeforeground="#333333",   highlightthickness=0)
        self.password_name.place(relx = authNameRelx + 0.11, rely = 0.35)

        self.password_entry = tb.Entry(master=self.form_frame, font=("Helvetica", 13), show="*")  #Entry(bd=0, bg="#f6f7f9", fg="#333333", font=("Helvetica", 14), show="*", highlightthickness=0)
        self.password_entry.place(relx = authNameRelx + 0.11, rely = 0.45, relwidth = 0.6)
        self.password_entry.focus()
        self.password_entry.bind("<Return>", lambda event: self._authenticate( self.password_entry.get()))

        #show and hide password section
        self.show_password_int = BooleanVar()
        self.show_password = tb.Checkbutton(self.form_frame, variable=self.show_password_int, bootstyle='round-toggle', text="Show Password", command=self._show_password) #Checkbutton(self.frame, variable=self.show_password_int, text="Show Password", bd=0, bg="#e6e6e6", fg="#333333", activeforeground="#333333", command=self._show_password, highlightthickness=0)
        self.show_password.place(relx = 0.3, rely = 0.6)
        # login or signup button section
        self.confirm_btn = tb.Button(self.form_frame, text = page_type, command = lambda: self._authenticate(self.password_entry.get()), bootstyle="outline-toolbutton") #Button(master = self.frame, background = "#e6e6e6", fg="#333333", activeforeground="#333333", highlightbackground="gray", activebackground="lightgray", relief="flat", text = page_type, font=("monospace", 22, "bold"), command = lambda: self._authenticate(self.password_entry.get()))
        self.confirm_btn.place( relwidth = 0.6, relx = authNameRelx + 0.11, rely = 0.8)


    # Application function logic
    def logout(self):
        self.logger.info("Logging out...")

        # Remove the main page
        self.frame.place_forget()
        #self.display_frame.place_forget()
        self.settings_frame.place_forget()
        """ self.logout_frame.place_forget()
        self.function_frame.place_forget() """
        
        # Go to login page
        self.show_auth_screen()


    def _submit_password(self, name: str, description: str, password: str):
        
        name = str(name); description= str(description); password = str(password)

        # Information Display Label
        info_label = tb.Label(master=self.display_create_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

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
        for widget in self.display_create_frame.winfo_children():
            widget.destroy()
        self.display_create_frame = tb.Labelframe(master=self.create_frame, labelanchor="n", relief="flat") #LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_create_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        # Create explanation label
        title = Label(master=self.display_create_frame, text="Add A New Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)

        # Function container
        self.add_frame = tb.Labelframe(master=self.display_create_frame, labelanchor="n", name="add A New Password")
        self.add_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )

        # Username label with input
        name_label = tb.Label(master=self.add_frame, text="Name:", font=("Helvetica", 15))
        name_label.place(relx=0.05, rely=0.1)
        self.name_input = tb.Entry(master=self.add_frame, name="name", font=("Helvetica", 14))
        self.name_input.place(relx=0.34, rely=0.1, relwidth=0.6)
        self.name_input.focus()

        # Description label with input
        description_label = tb.Label(master=self.add_frame, text="Description:", font=("Helvetica", 15))
        description_label.place(relx=0.05, rely=0.3)
        self.description_input = tb.Entry(master=self.add_frame, font=("Helvetica", 14))
        self.description_input.place(relx=0.34, rely=0.3, relwidth=0.6)

        # Password label with input
        password_label = tb.Label(master=self.add_frame, text="Password:", font=("Helvetica", 15))
        password_label.place(relx=0.05, rely=0.5)
        self.password_input = tb.Entry(master=self.add_frame, font=("Helvetica", 14))
        self.password_input.place(relx=0.34, rely=0.5, relwidth=0.6)

        # Submit Button
        submit_btn = tb.Button(master=self.add_frame, bootstyle="outline-toolbutton", text = "Submit", command= lambda: self._submit_password(self.name_input.get(), self.description_input.get(), self.password_input.get()))
        submit_btn.place(relx=0.21, rely=0.8, relwidth=0.6)


    def _search_by(self):

        #self.search_by = True
        if self.search_int.get():
            self.type_label.configure(text = "")
            self.type_label.configure(text = "By ID")

            self.search_by = False
            self.search_int.set(True)

        else:
            self.type_label.configure(text = "")
            self.type_label.configure(text = "By Name")

            self.search_by = True
            self.search_int.set(False)

    def _show_search_password(self):

        if self.show_pass_int.get():
            self.show = True
            self.show_pass_int.set(True)

        else:
            self.show= False
            self.show_pass_int.set(False)                   

    def _search_password(self, search: str):
        search = str(search)

        # Information Display Label
        info_label = Label(master=self.display_search_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

        try:
            if not self.search_by:
                search = int(search)
        except ValueError:
            info_label.configure(text="")
            info_label.configure(text="Search Must Be A Number")
            return 

        if search == "1":
            info_label.configure(text="")
            info_label.configure(text="Can't search Root Password")
            return
        
        passwords = self.db.get_password(search, name=True) if self.search_by else self.db.get_password(search)

        if passwords == [] or len(passwords) == 0:
            info_label.configure(text="")
            info_label.configure(text="No Matching Name found")
            return

        # Password grid and pady location
        id_grid = 1
        name_grid = 2
        description_grid = 3
        password_grid = 4
        label_space_grid = 6
        id_pady = 5
        
        # Reset the display screen
        for widget in self.get_frame.winfo_children():
            widget.destroy()

        # Add horizontal and vertical scroll
        self.display_canvas = tb.Canvas(master=self.get_frame, borderwidth=2, relief="flat")
        self.display_canvas.place(relx= 0, rely= 0, relheight = 1, relwidth = 1)

        self.horizontal_scroll = tb.Scrollbar(self.get_frame, bootstyle='round', orient="horizontal", command=self.display_canvas.xview)
        self.horizontal_scroll.place(relx=0, rely=0.97, relwidth=1)
        self.vertical_scroll = tb.Scrollbar(self.get_frame, bootstyle='round', orient="vertical", command=self.display_canvas.yview)
        self.vertical_scroll.place(relx=0.975, rely=0, relheight=1)

        self.display_canvas.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)
        self.display_canvas.bind( "<Configure>", lambda e: self.display_canvas.configure(scrollregion= self.display_canvas.bbox("all")))

        self.get_frame = Frame(master=self.display_canvas)
        self.display_canvas.create_window((0,0), window=self.get_frame, anchor="nw")

        self.width = 701 if self.width != 701 else 702
        self.height = 581 if self.height != 581 else 582
        self.top_widget.geometry(f"{self.width}x{self.height}")

        for password in passwords:

            id_label = Label(master=self.get_frame, text="ID:", font=("Helvetica", 15), anchor="w", justify="left")
            id_label.grid(row=id_grid, column=0, sticky="w", padx=20, pady=id_pady)
            password_id = Label(master=self.get_frame, text=password[0], font=("Helvetica", 15))
            password_id.grid(row=id_grid, column=1, sticky="w", padx=20, pady=id_pady)

            name_label = Label(master=self.get_frame, text="Name:", font=("Helvetica", 15))
            name_label.grid(row=name_grid, column=0, sticky="w", padx=20, pady=5)
            password_name = Label(master=self.get_frame, text=password[1], font=("Helvetica", 15))
            password_name.grid(row=name_grid, column=1, sticky="w", padx=20, pady=5)

            description_label = Label(master=self.get_frame, text="Description:", font=("Helvetica", 15))
            description_label.grid(row=description_grid, sticky="w", padx=20, column=0, pady=5)
            password_description = Label(master=self.get_frame, text=password[2], font=("Helvetica", 15))
            password_description.grid(row=description_grid, sticky="w", padx=20, column=1, pady=5)

            label_space = Label(master=self.get_frame, font=("Helvetica", 15))
            label_space.grid(row=label_space_grid, sticky="w", padx=20, column=0, pady=5)

            password_label = Label(master=self.get_frame, text="Password:", font=("Helvetica", 15))
            password_pass = Label(master=self.get_frame, text=password[3], font=("Helvetica", 15))
            if self.show:
                password_label.grid(row=password_grid, column=0, sticky="w", padx=20, pady=5)
                password_pass.grid(row=password_grid, column=1, sticky="w", padx=20, pady=5)

            # push down for next password
            id_grid += 5
            name_grid += 5
            description_grid += 5
            password_grid += 5
            label_space_grid += 5

    def get_1_password(self):
        
        # Reset the display screen
        for widget in self.display_search_frame.winfo_children():
            widget.destroy()
        self.display_search_frame = tb.Labelframe(master=self.search_frame, labelanchor="n", relief="flat")
        self.display_search_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1) 

        # Create explanation label
        title = Label(master=self.display_search_frame, text="Search For Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)

        # Function container
        self.get_frame = tb.Labelframe(master=self.display_search_frame, labelanchor="n")
        self.get_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )

        search_label = tb.Label(master=self.get_frame, text="Search", font=("Helvetica", 15))
        search_label.place(relx=0.35, rely=0.1)

        self.type_label = tb.Label(master=self.get_frame, text="By Name", font=("Helvetica", 15))
        self.type_label.place(relx=0.5, rely=0.1)

        search_input = tb.Entry(master=self.get_frame, font=("Helvetica", 14))
        search_input.place(relx=0.21, rely=0.25, relwidth=0.6)
        search_input.focus()

        self.search_by = True
        self.search_int = BooleanVar()
        self.search_name = tb.Checkbutton(self.get_frame, variable=self.search_int, bootstyle='round-toggle', text="Search By ID", command= self._search_by)
        self.search_name.place(relx=0.21, rely=0.4)

        # Show and hide password
        self.show = False
        self.show_pass_int = BooleanVar()
        self.show_pass = tb.Checkbutton(self.get_frame, variable=self.show_pass_int, bootstyle='round-toggle', text="Show Password", command= self._show_search_password)
        self.show_pass.place(relx=0.21, rely=0.5) 

        # Submit Button
        submit_btn = tb.Button(master=self.get_frame, bootstyle="outline-toolbutton", text = "Submit", command= lambda: self._search_password(search_input.get()))
        submit_btn.place(relx=0.21, rely=0.8, relwidth=0.6)


    def _show_all_password(self):

        if self.show_all_pass_int.get():
            self.show_all = True
            self.show_pass_int.set(True)

        else:
            self.show_all = False
            self.show_all_pass_int.set(False)

    def _get_all_password(self):

        # Information Display Label
        info_label = Label(master=self.display_get_all_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)
        
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
        for widget in self.show_all_frame.winfo_children():
            widget.destroy()

        # Add horizontal and vertical scroll
        self.display_canvas = Canvas(master=self.show_all_frame, borderwidth=2, relief="flat", highlightbackground="gray", highlightthickness=1)
        self.display_canvas.place(relx= 0, rely= 0, relheight = 1, relwidth = 1)

        self.horizontal_scroll = tb.Scrollbar(self.show_all_frame, bootstyle='round', orient="horizontal", command=self.display_canvas.xview)
        self.horizontal_scroll.place(relx=0, rely=0.97, relwidth=1)
        self.vertical_scroll = tb.Scrollbar(self.show_all_frame, bootstyle='round', orient="vertical", command=self.display_canvas.yview)
        self.vertical_scroll.place(relx=0.975, rely=0, relheight=1)

        self.display_canvas.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)
        self.display_canvas.bind( "<Configure>", lambda e: self.display_canvas.configure(scrollregion= self.display_canvas.bbox("all")))

        self.show_all_frame = Frame(master=self.display_canvas)
        self.display_canvas.create_window((0,0), window=self.show_all_frame, anchor="nw")

        self.width = 702 if self.width != 702 else 701
        self.height = 582 if self.height != 582 else 581
        self.top_widget.geometry(f"{self.width}x{self.height}")


        for password in passwords:

            id_label = Label(master=self.show_all_frame, text="ID:", font=("Helvetica", 16), anchor="w", justify="left")
            id_label.grid(row=id_grid, column=0, sticky="w", padx=20, pady=5)
            
            password_id = Label(master=self.show_all_frame, text=password[0], font=("Helvetica", 16))
            password_id.grid(row=id_grid, column=1, sticky="w", padx=20, pady=5)
            

            name_label = Label(master=self.show_all_frame, text="Name:", font=("Helvetica", 16))
            name_label.grid(row=name_grid, column=0, sticky="w", padx=20, pady=5)
            
            password_name = Label(master=self.show_all_frame, text=password[1], font=("Helvetica", 16))
            password_name.grid(row=name_grid, column=1, sticky="w", padx=20, pady=5)
            

            description_label = Label(master=self.show_all_frame, text="Description:", font=("Helvetica", 16))
            description_label.grid(row=description_grid, column=0, sticky="w", padx=20, pady=5)
            password_description = Label(master=self.show_all_frame, text=password[2], font=("Helvetica", 16))
            password_description.grid(row=description_grid, column=1, sticky="w", padx=20, pady=5)

            label_space = Label(master=self.show_all_frame, font=("Helvetica", 16))
            label_space.grid(row=label_space_grid, sticky="w", padx=20, column=0, pady=5)

            password_label = Label(master=self.show_all_frame, text="Password:", font=("Helvetica", 16))
            password_pass = Label(master=self.show_all_frame, text=password[3], font=("Helvetica", 16))
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
        for widget in self.display_get_all_frame.winfo_children():
            widget.destroy()
        self.display_get_all_frame = tb.Labelframe(master=self.get_all_frame, labelanchor="n", relief="flat")
        self.display_get_all_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        # Create explanation label
        title = tb.Label(master=self.display_get_all_frame, text="Show Saved Passwords", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0, relwidth=1)

        self.show_all_frame = tb.Labelframe(master=self.display_get_all_frame, labelanchor="n")
        self.show_all_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )
        
        #show and hide all passwords
        self.show_all = False
        self.show_all_pass_int = BooleanVar()
        self.show_all_pass = tb.Checkbutton(self.show_all_frame, variable=self.show_all_pass_int, bootstyle="round-toggle", text="Show All Password", command= self._show_all_password)
        self.show_all_pass.place(relx=0.32, rely=0.4)
        # Submit Button
        submit_btn = tb.Button(master=self.show_all_frame, bootstyle="outline-toolbutton", text = "Submit", command= self._get_all_password)
        submit_btn.place(relx=0.21, rely=0.72, relwidth=0.6)


    def _update_password(self, id: str, name: str, description: str, password: str):

        id=str(id); name= str(name); description= str(description); password= str(password)

        # Information Display Label
        info_label = Label(master=self.display_update_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

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
        for widget in self.display_update_frame.winfo_children():
            widget.destroy()
        self.display_update_frame = tb.Labelframe(master=self.update_frame, labelanchor="n", relief="flat")
        self.display_update_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        # Create explanation label
        title = tb.Label(master=self.display_update_frame, text="Update A password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)

        # Function container
        self.append_frame = tb.Labelframe(master=self.display_update_frame, labelanchor="n")
        self.append_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )

        id_label = tb.Label(master=self.append_frame, text="Password ID:", font=("Helvetica", 15))
        id_label.place(relx=0.05, rely=0.1)
        type_label = tb.Label(master=self.append_frame, text="Compulsory:", font=("Helvetica", 11))
        type_label.place(relx=0.35, rely=0.05)

        self.update_id_input = tb.Entry(master=self.append_frame, font=("Helvetica", 13))
        self.update_id_input.place(relx=0.34, rely=0.1, relwidth=0.6)
        self.update_id_input.focus()

        # Username label with input
        name_label = tb.Label(master=self.append_frame, text="Name:", font=("Helvetica", 15))
        name_label.place(relx=0.05, rely=0.3)

        self.update_name_input = tb.Entry(master=self.append_frame, font=("Helvetica", 13))
        self.update_name_input.place(relx=0.34, rely=0.3, relwidth=0.6)

        # Description label with input
        description_label = tb.Label(master=self.append_frame, text="Description:", font=("Helvetica", 15))
        description_label.place(relx=0.05, rely=0.5)

        self.update_description_input = tb.Entry(master=self.append_frame, font=("Helvetica", 13))
        self.update_description_input.place(relx=0.34, rely=0.5, relwidth=0.6)

        # Password label with input
        password_label = tb.Label(master=self.append_frame, text="Password:", font=("Helvetica", 15))
        password_label.place(relx=0.05, rely=0.7)

        self.update_password_input = tb.Entry(master=self.append_frame, font=("Helvetica", 13))
        self.update_password_input.place(relx=0.34, rely=0.7, relwidth=0.6)

        # Submit Button
        submit_btn = tb.Button(master=self.append_frame, bootstyle="outline-toolbutton", text = "Submit", command= lambda: self._update_password(self.update_id_input.get(), self.update_name_input.get(), self.update_description_input.get(), self.update_password_input.get()))
        submit_btn.place(relx=0.21, rely=0.87, relwidth=0.6)

    
    def _delete_password(self, id: str, root_password: str):

        id=str(id); root_password= str(root_password);

        # Information Display Label
        info_label = Label(master=self.display_delete_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

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
        for widget in self.display_delete_frame.winfo_children():
            widget.destroy()
        self.display_delete_frame = tb.Labelframe(master=self.delete_frame, labelanchor="n", relief="flat")
        self.display_delete_frame.place(relx = 0, rely = 0, relheight =1, relwidth =1)

        # Create explanation label
        title = tb.Label(master=self.display_delete_frame, text="Remove A password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)
        

        # Function container
        self.del_frame = tb.Labelframe(master=self.display_delete_frame, labelanchor="n")
        self.del_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )

        root_label = tb.Label(master=self.del_frame, text="Root Password:", font=("Helvetica", 15))
        root_label.place(relx=0.04, rely=0.15)

        self.delete_root_input = tb.Entry(master=self.del_frame, font=("Helvetica", 13))
        self.delete_root_input.place(relx=0.34, rely=0.15, relwidth=0.6)
        self.delete_root_input.focus()

        id_label = tb.Label(master=self.del_frame, text="Password ID:", font=("Helvetica", 15))
        id_label.place(relx=0.04, rely=0.35)

        self.delete_id_input = tb.Entry(master=self.del_frame, font=("Helvetica", 13))
        self.delete_id_input.place(relx=0.34, rely=0.35, relwidth=0.6)

        # Submit Button
        submit_btn = tb.Button(master=self.del_frame, bootstyle="outline-toolbutton", text = "Submit", command= lambda: self._delete_password(self.delete_id_input.get(), self.delete_root_input.get()))
        submit_btn.place(relx=0.21, rely=0.7, relwidth=0.6)


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
        info_label = Label(master=self.display_account_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

        # Error handling
        if root_password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        if not self.db.confirm_root(root_password):
            info_label.configure(text="")
            info_label.configure(text="Root Password Incorrect")
            return

        # Pop Up confirmation
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
        for widget in self.func_frame.winfo_children():
            widget.destroy()
        
        self.account_title.place_forget()

        # Create explanation label
        title = tb.Label(master=self.display_account_frame, text="Delete All Passwords", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)

        back_btn = tb.Button(master=self.func_frame, bootstyle="outline-toolbutton", text = "Back", command= lambda: self._show_previous_page("Account Info"))
        back_btn.place(relx=0.04, rely=0.03)

        root_label = tb.Label(master=self.func_frame, text="Root Password:", font=("Helvetica", 15))
        root_label.place(relx=0.35, rely=0.3)

        self.delete_all_root_input = tb.Entry(master=self.func_frame, font=("Helvetica", 14))
        self.delete_all_root_input.place(relx=0.21, rely=0.4, relwidth=0.6)
        self.delete_all_root_input.focus()

        # Submit Button
        submit_btn = tb.Button(master=self.func_frame, text = "Delete", bootstyle="outline-toolbutton", command= lambda: self._delete_all_password(self.delete_all_root_input.get()))
        submit_btn.place(relx=0.21, rely=0.8, relwidth=0.6)


    def _update_root_password(self, root_password: str, new_root: str, confirm_root: str):
        
        root_password= str(root_password); new_root = str(new_root); confirm_root = str(confirm_root)

        # Information Display Label
        info_label = Label(master=self.display_account_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

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

        # Pop Up confirmation
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
        for widget in self.func_frame.winfo_children():
            widget.destroy()
        self.account_title.place_forget()

        # Create explanation label
        title = tb.Label(master=self.display_account_frame, text="Update Root Password", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)


        back_btn = tb.Button(master=self.func_frame, bootstyle="outline-toolbutton", text = "Back", command= lambda: self._show_previous_page("Account Info") )
        back_btn.place(relx=0.05, rely=0.03)

        root_label = tb.Label(master=self.func_frame, text="Old Password:", font=("Helvetica", 15))
        root_label.place(relx=0.05, rely=0.2)

        self.current_root_input = tb.Entry(master=self.func_frame, font=("Helvetica", 14))
        self.current_root_input.place(relx=0.34, rely=0.2, relwidth=0.6)
        self.current_root_input.focus()

        new_root_label = tb.Label(master=self.func_frame, text="New Password:", font=("Helvetica", 15))
        new_root_label.place(relx=0.05, rely=0.4)

        self.new_root_input = tb.Entry(master=self.func_frame, font=("Helvetica", 14))
        self.new_root_input.place(relx=0.34, rely=0.4, relwidth=0.6)
        
        confirm_root_label = tb.Label(master=self.func_frame, text="Confirm:", font=("Helvetica", 15))
        confirm_root_label.place(relx=0.05, rely=0.6)

        self.confirm_root_input = tb.Entry(master=self.func_frame, font=("Helvetica", 14))
        self.confirm_root_input.place(relx=0.34, rely=0.6, relwidth=0.6)

        # Submit Button
        submit_btn = tb.Button(master=self.func_frame, text = "Update", bootstyle="outline-toolbutton", command= lambda: self._update_root_password(self.current_root_input.get(), self.new_root_input.get(), self.confirm_root_input.get()))
        submit_btn.place(relx=0.21, rely=0.8, relwidth=0.6)


    def _delete_account(self, root_password: str):

        root_password = str(root_password)

        # Information Display Label
        info_label = Label(master=self.display_account_frame, text="", anchor="center", justify="center", font=("monospace", 20))
        info_label.place(relx=0, rely=0.1, relwidth=1)

        # Error handling
        if root_password == "":
            info_label.configure(text="")
            info_label.configure(text="Fill All Sections")
            return

        if not self.db.confirm_root(root_password):
            info_label.configure(text="")
            info_label.configure(text="Root Password Incorrect")
            return

        # Pop Up confirmation
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
        for widget in self.func_frame.winfo_children():
            widget.destroy()
        self.account_title.place_forget()

        # Create explanation label
        title = tb.Label(master=self.display_account_frame, text="Delete Account", anchor="center", justify="center", font=("monospace", 25, "bold"))
        title.place(relx=0, rely=0.01, relwidth=1)

        back_btn = tb.Button(master=self.func_frame, bootstyle="outline-toolbutton", text = "Back", command= lambda: self._show_previous_page("Account Info"))
        back_btn.place(relx=0.04, rely=0.03)

        root_label = tb.Label(master=self.func_frame, text="Root Password:", font=("Helvetica", 16))
        root_label.place(relx=0.35, rely=0.3)

        self.delete_account_root_input = tb.Entry(master=self.func_frame, font=("Helvetica", 14))
        self.delete_account_root_input.place(relx=0.21, rely=0.4, relwidth=0.6)
        self.delete_account_root_input.focus()

        # Submit Button
        submit_btn = tb.Button(master=self.func_frame, text = "Delete Account", bootstyle="outline-toolbutton", command= lambda: self._delete_account(self.delete_account_root_input.get()))
        submit_btn.place(relx=0.21, rely=0.8, relwidth=0.6)       

    def _show_previous_page(self, page: str):

        tab_functions = {
            "Create": self.add_new_password,
            "Logout": self.logout,
            "Search": self.get_1_password,
            "Get All Passwords": self.get_all_password,
            "Update": self.update_1_password,
            "Delete": self.delete_1_password,
            "File Encryption": self.file_actions,
            "Account Info": self.display_settings
        }

        if page in tab_functions.keys():
            tab_functions[page]()


    def display_settings(self):
       
        # Reset the display screen
        for widget in self.display_account_frame.winfo_children():
            widget.destroy()
        self.display_account_frame = tb.Labelframe(master=self.account_frame, labelanchor="n", relief="flat")
        self.display_account_frame.place(relx = 0, rely = 0, relheight =1, relwidth =1)

        # Create explanation label
        self.account_title = tb.Label(master=self.display_account_frame, text="Account Settings", anchor="center", justify="center", font=("monospace", 25, "bold"))
        self.account_title.place(relx=0, rely=0.01, relwidth=1)

        # Function container
        self.func_frame = tb.Labelframe(master=self.display_account_frame, labelanchor="n")
        self.func_frame.place(relx = 0.15, rely = 0.2, relwidth=0.7, relheight=0.7 )

        """ ico = PhotoImage(data=Icon.warning, height=20, width=20)
        id_label = tb.Label(master=self.func_frame, text="unknown", image=ico)
        id_label.place(relx=0.04, rely=0.35) """

        logout_btn = tb.Button(master=self.func_frame, bootstyle="outline-toolbutton", text = "Logout", command= self.logout)
        logout_btn.place(relx=0.05, rely=0.05)

        self.update_root = tb.Button(master=self.func_frame, text = "Change Root Password", bootstyle="outline-toolbutton", command = self.change_root_password)
        self.update_root.place(relx=0.21, rely=0.2, relwidth=0.6)

        self.purge_password = tb.Button(master=self.func_frame, text = "Delete All Passwords", bootstyle="danger-outline-toolbutton", command = self.delete_all_password)
        self.purge_password.place(relx=0.21, rely=0.6, relwidth=0.6)

        self.delete_btn = tb.Button(master=self.func_frame, text = "Delete Account", bootstyle="danger-outline-toolbutton", command = self.delete_account)
        self.delete_btn.place(relx=0.21, rely=0.8, relwidth=0.6)


    def file_actions(self):
        pass


    def _on_tab_change(self, event):
        
        tab_functions = {
            "Create": self.add_new_password,
            "Logout": self.logout,
            "Search": self.get_1_password,
            "Get All Passwords": self.get_all_password,
            "Update": self.update_1_password,
            "Delete": self.delete_1_password,
            "File Encryption": self.file_actions,
            "Account Info": self.display_settings
        }

        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        if tab_text in tab_functions.keys():
            
            tab_functions[tab_text]()

    def main_page(self):

        # Resizing work frame
        self.frame_width = 1
        self.frame_height = 1
        self.frame_relx = 0
        self.frame_rely = 0

        self.logger.info("Cueing Main screen")

        # Display frame
        self.frame = Frame(master = self.top_widget)
        self.frame.place(relx = self.frame_relx, rely = self.frame_rely, relheight = self.frame_height, relwidth = self.frame_width)

        self.settings_frame = tb.Notebook(master=self.frame, bootstyle='dark') #LabelFrame(master=self.frame, borderwidth=2, labelanchor="n", relief="flat", highlightbackground="gray", highlightthickness=1)
        self.settings_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.create_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.search_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.update_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.delete_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.get_all_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.files_frame = tb.Frame(master=self.settings_frame, relief="flat")
        self.account_frame = tb.Frame(master=self.settings_frame, relief="flat")

        self.display_create_frame = tb.Labelframe(master=self.create_frame, labelanchor="n", relief="flat")
        self.display_create_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_search_frame = tb.Labelframe(master=self.search_frame, labelanchor="n", relief="flat")
        self.display_search_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_update_frame = tb.Labelframe(master=self.update_frame, labelanchor="n", relief="flat")
        self.display_update_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_delete_frame = tb.Labelframe(master=self.delete_frame, labelanchor="n", relief="flat")
        self.display_delete_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_get_all_frame = tb.Labelframe(master=self.get_all_frame, labelanchor="n", relief="flat")
        self.display_get_all_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_files_frame = tb.Labelframe(master=self.files_frame, labelanchor="n", relief="flat")
        self.display_files_frame.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

        self.display_account_frame = tb.Labelframe(master=self.account_frame, labelanchor="n", relief="flat")
        self.display_account_frame.place(relx = 0.1, rely = 0, relheight = 0.9, relwidth = 0.9)

    
        # Start default function
        self.add_new_password()

        self.settings_frame.add(self.create_frame, text='Create')
        self.settings_frame.add(self.search_frame, text='Search')
        self.settings_frame.add(self.update_frame, text='Update')
        self.settings_frame.add(self.delete_frame, text='Delete')
        self.settings_frame.add(self.get_all_frame, text='Get All Passwords')
        self.settings_frame.add(self.files_frame, text='File Encryption')
        self.settings_frame.add(self.account_frame, text='Account Info')
        self.settings_frame.bind("<<NotebookTabChanged>>", self._on_tab_change)

        
        """ # Important Account section
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
        self.delete_frame.place(rely=0.9, relx=0, relwidth=0.4, relheight=0.1) """

    def __del__(self):
    
        self.logger.info("destroying Gui object ...")
        self.top_widget.quit()


if __name__ == "__main__":
    
    gui = Gui()

    gui.show_auth_screen()

    gui.top_widget.mainloop()
