import os, json
import logging
import sqlite3
from pathlib import Path
from threading import Lock
 

class UnSupportedOs(Exception):
    ...


class DatabaseInitError(Exception):
    ...


class Database:
    # NOTE :: root_password should be stored as a sha hash
    # NOTE :: other passwords are to be stored as an AES encryption with the original value of the root
    # password being the key
    def __init__(self):

        hdlr = logging.StreamHandler()
        hdlr.formatter = logging.Formatter(
            "%(filename)s :: %(funcName)s :: %(levelname)s -> %(message)s")

        self.logger = logging.Logger("database_logger")
        self.logger.addHandler(hdlr)

        self.logger.info(f"initializing Database object ...")

        home_dir = Path(os.path.expanduser("~"))
        os_name = os.uname().sysname.lower()
        if "linux" in os_name:

            cache_dir = home_dir / ".cache"

        elif "windows" in os_name:

            cache_dir = home_dir / "AppData" / "Local"

        elif "mac" in os_name:

            cache_dir = home_dir / "Library" / "Caches"

        else:

            raise UnSupportedOs(f"os {os_name} is not supported")

        if not cache_dir.exists():

            raise DatabaseInitError(
                f"cache directory {cache_dir} does not exists")

        if not cache_dir.is_dir():

            raise DatabaseInitError(
                f"cache directory {cache_dir} is not a directory")

        app_cache = cache_dir / "passman"
        self.cache_dir = app_cache

        if not (app_cache).exists():

            # create application's cache if it doesn't exists
            self.logger.error(f"cannot find cache directory {app_cache}")
            self.logger.info(
                f"creating new cache directory at {app_cache} ...")
            app_cache.mkdir()

        self.db = sqlite3.connect(app_cache / "database.db")
        self.db_cur = self.db.cursor()
        self.cursor_lock = Lock()

        self.root_password = ""

    def create_tables(self, root_password: str):

        self.logger.info("creating new database tables ...")
        self.cursor_lock.acquire()

        # create new table password
        self.db_cur.execute("""CREATE TABLE IF NOT EXISTS password (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description VARCHAR(300),
            password TEXT NOT NULL
        )
        """)
        # self.db.commit()

        # add admin password as the first password
        root_list = ['root', 'root password', root_password]
        self.db_cur.execute("INSERT INTO password (name, description, password) VALUES (?, ?, ?)", (root_list))
        self.db.commit()

        # Validate table creation to True
        try: #ensure that the json exists and is not empty
            with open(Path(__file__).parent/"database_table.json", 'r') as json_file:
                json_data = json.load(json_file)

        # fill json file if exception occurs
        except (FileNotFoundError, json.JSONDecodeError):
            json_data = {"validate_table": "False"}

        # Validate database creation to be true
        json_data["validate_table"] = "True"

        # dumps the modified dictionary to the json file
        with open(Path(__file__).parent/"database_table.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        self.cursor_lock.release()
      
    # returns root password
    def show_root(self):
        self.logger.info("Getting Root Password...")
        return self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]

    #confirms if id exists
    def confirm_id(self, id):

        try:
            id = int(id)
        except ValueError:
            return "Invalid ID"

        for i in self.db_cur.execute("SELECT oid FROM password WHERE id != 1").fetchall():
            if id in i:
                return True
            elif id not in i:
                return False

    def append_password(self, name: str, description: str, password: str):

        self.logger.info("adding new password ...")
        #self.cursor_lock.acquire()

        self.db_cur.execute(
            "INSERT INTO password (name, description, password) VALUES(?, ?, ?)", (name, description, password))
        self.db.commit()
        #self.cursor_lock.release()

    def get_passwords(self):

        self.logger.info("getting all password information ...")
        #self.cursor_lock.acquire()

        passlist = self.db_cur.execute("SELECT * FROM password WHERE id != 1;").fetchall()

        return passlist

        #self.db.commit()
        #self.cursor_lock.release()

    def get_password(self, search: str, name: bool = False) -> list:

        self.logger.info("getting all password information ...")
        #self.cursor_lock.acquire()

        # Search by name
        if name:
            search = str(search)

            passlist = []
            for passinfo in self.db_cur.execute("SELECT * FROM password WHERE oid != 1 AND name == (?)", (search,)).fetchall():

                passlist.append(passinfo)
            
            return passlist

        #search by id
        elif not name:
            search = str(search)

            passlist = []
            for passinfo in self.db_cur.execute("SELECT * FROM password WHERE oid != 1 AND oid == (?)", (search)).fetchall():

                passlist.append(passinfo)
            
            return passlist
            #print(passlist)
            

        #self.db.commit()
        #self.cursor_lock.release()

    def update_password(self, id: str, name="", description="", password=""):
        
        self.logger.info("Updating A Password ...")
        #self.cursor_lock.acquire()

        # search and update by id
        id = str(id)

        if name == "" and description == "" and password == "":
            return "A Change Must Be Made"

        # Update only one column
        if name != "" and description == "" and password == "":
            self.db_cur.execute("UPDATE Password SET name = (?) WHERE oid != 1 AND oid == (?)", (name, id))
        elif name == "" and description != "" and password == "":
            self.db_cur.execute("UPDATE Password SET description = (?) WHERE oid != 1 AND oid == (?)", (description, id))
        elif name == "" and description == "" and password != "":
            self.db_cur.execute("UPDATE Password SET password = (?) WHERE oid != 1 AND oid == (?)", (password, id))

        # Update two columns
        if name != "" and description != "" and password == "":
            self.db_cur.execute("UPDATE Password SET name = (?), description = (?) WHERE oid != 1 AND oid == (?)", (name, description, id))
        elif name != "" and description == "" and password != "":
            self.db_cur.execute("UPDATE Password SET name = (?), password = (?) WHERE oid != 1 AND oid == (?)", (name, password, id))
        elif name == "" and description != "" and password != "":
            self.db_cur.execute("UPDATE Password SET description = (?), password = (?) WHERE oid != 1 AND oid == (?)", (description, password, id))

        # Update all columns
        if name != "" and description != "" and password != "":
            self.db_cur.execute("UPDATE Password SET name = (?), description = (?) WHERE oid != 1 AND oid == (?)", (name, description, id))

        self.db.commit()
        #self.cursor_lock.release()

    def update_root_password(self, root_password: str, new_root_password: str):

        self.logger.info(f"Updating Root Password ...")
        #self.cursor_lock.acquire()

        root_password = str(root_password); new_root_password

        if root_password != self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]:
            self.logger.info("Wrong root passsword...")
            self.db.commit()
            #self.cursor_lock.release()
            return "Wrong Root Password"
        
        else:
            self.db_cur.execute("UPDATE Password SET password= (?) WHERE oid = 1", (new_root_password, ))
            self.db.commit()
            #self.cursor_lock.release()


    def delete_password(self, id: int, root_password: str):

        self.logger.info(f"deleting password with id {id} ...")
        #self.cursor_lock.acquire()

        id = str(id)

        if root_password != self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]:
            self.logger.info("Wrong root passsword...")
            self.db.commit()
            #self.cursor_lock.release()
            return "Wrong Root Password"

        else:
            self.db_cur.execute("DELETE FROM password WHERE id == ?;", id)
            self.db.commit()
            #self.cursor_lock.release()

    def purge(self, root_password: str):

        self.logger.info("purging database passwords ...")
        #self.cursor_lock.acquire()

        if root_password != self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]:
            self.logger.warning("Wrong root passsword...")
            self.db.commit()
            #self.cursor_lock.release()
            return "Wrong Root Password"

        else:
            # delete all passwords
            self.db_cur.execute("DELETE FROM password WHERE id != 1")
            self.db.commit()
            #self.cursor_lock.release()

    def delete_account(self, root_password: str):
        self.logger.info("Removing Database...")
        #self.cursor_lock.acquire()

        if root_password != self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]:
            self.logger.warning("Wrong root passsword...")
            self.db.commit()
            #self.cursor_lock.release()
            return "Wrong Root Password"

        else:
            # Delete database
            self.db_cur.execute("DROP TABLE IF EXISTS password")
            self.db.commit()

            # Validate table creation to True
            try: #ensure that the json exists and is not empty
                with open(Path(__file__).parent/"database_table.json", 'r') as json_file:
                    json_data = json.load(json_file)

            # fill json file if exception occurs
            except (FileNotFoundError, json.JSONDecodeError):
                json_data = {"validate_table": "False"}

            # Validate database creation to be true
            json_data["validate_table"] = "False"

            # dumps the modified dictionary to the json file
            with open(Path(__file__).parent/"database_table.json", "w") as json_file:
                json.dump(json_data, json_file, indent=4)

            #self.cursor_lock.release()
        
    def __del__(self):

        self.logger.info("destroying Database object ...")
        self.db.close()

if __name__ == "__main__":
    obj = Database()

    obj.create_tables("root_password")
    obj.append_password("ecode", "alayaabubakar2005@gmail.com", "Elias_code11")
    #obj.update_password(2, name="Ecode2", description="alayaabubakar@gmail.com")

    #obj.delete_account("root_password")