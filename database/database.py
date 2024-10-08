import os, json
import logging, sqlite3
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, base64
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


    def create_tables(self, root_password: str):

        self.logger.info("creating new database tables ...")
        self.cursor_lock.acquire()

        # create new table password
        self.db_cur.execute("""CREATE TABLE IF NOT EXISTS password (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description VARCHAR(300),
            password TEXT NOT NULL,
            salt TEXT
        )
        """)

        # Encrypt password with hash encryption
        hasher = hashlib.sha256()
        hasher.update(root_password.encode())
        root_password = hasher.hexdigest()

        salt = os.urandom(16)

        # add admin password as the first password
        root_list = ['root', 'root password', root_password, salt]
        self.db_cur.execute("INSERT INTO password (name, description, password, salt) VALUES (?, ?, ?, ?)", (root_list))
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
      
    # create cipher key
    def cipher_key(self, root_password: str):
        root_password = str(root_password)

        if self.confirm_root(root_password):

            salt = self.db_cur.execute("SELECT salt FROM password WHERE id = 1").fetchall()[0][0]
            #key = hashlib.pbkdf2_hmac("sha256", root_password.encode("utf-8"), salt, 100000)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), salt=salt, iterations=100000, length=32)
            key = base64.urlsafe_b64encode(kdf.derive(root_password.encode("utf-8")))

            self.cipher = Fernet(key)

    # confirms root password
    def confirm_root(self, root_password:str):
        self.logger.info("Confirming Root Password...")

        root_password = str(root_password)
        root = self.db_cur.execute("SELECT password FROM password WHERE id= 1").fetchall()[0][0]

        hasher = hashlib.sha256()
        hasher.update(root_password.encode())
        hashed_root = hasher.hexdigest()

        if hashed_root == root:
            return True
        elif hashed_root != root:
            return False

    #confirms if id exists
    def confirm_id(self, id):

        try:
            id = int(id)
        except ValueError:
            return "Invalid ID"

        all_id = self.db_cur.execute("SELECT id FROM password WHERE id != 1").fetchall()
        
        all_id_list = []
        for i in all_id:
            all_id_list.append(i[0])

        if id in all_id_list:
            return True
        elif id not in all_id_list:
            return False

    def append_password(self, name: str, description: str, password: str):

        self.logger.info("adding new password ...")
        
        # Encrypt password with aes encryption
        password = self.cipher.encrypt(password.encode("utf-8"))
        #password = str(password)

        self.db_cur.execute(
            "INSERT INTO password (name, description, password) VALUES(?, ?, ?)", (name, description, password))
        self.db.commit()

    def get_passwords(self):

        self.logger.info("getting all password information ...")

        passlist = self.db_cur.execute("SELECT * FROM password WHERE id != 1;").fetchall()
        passinfo_list = []

        # Decrypt passwords
        for password in passlist:

            passinfo = []
            passinfo.append(password[0])
            passinfo.append(password[1])
            passinfo.append(password[2])
            passinfo.append(password[3])
            
            passinfo[3] = self.cipher.decrypt(passinfo[3]).decode()

            passinfo_list.append(passinfo)

        return passinfo_list

    def get_password(self, search: str, name: bool = False) -> list:

        self.logger.info("getting all password information ...")

        by = "name" if name else "oid"
        search = str(search)

        passlist = []
        for passinfo in self.db_cur.execute(f"SELECT * FROM password WHERE oid != 1 AND {by} == (?)", (search,)).fetchall():
            
            password = []
            password.append(passinfo[0])
            password.append(passinfo[1])
            password.append(passinfo[2])
            password.append(passinfo[3])

            password[3] =self.cipher.decrypt(password[3]).decode()
            passlist.append(password)

        return passlist
            
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
            # Encrypt password
            password = self.cipher.encrypt(password.encode("utf-8"))
            
            self.db_cur.execute("UPDATE Password SET password = (?) WHERE oid != 1 AND oid == (?)", (password, id))

        # Update two columns
        if name != "" and description != "" and password == "":
            self.db_cur.execute("UPDATE Password SET name = (?), description = (?) WHERE oid != 1 AND oid == (?)", (name, description, id))
        elif name != "" and description == "" and password != "":
            # Encrypt password
            password = self.cipher.encrypt(password.encode("utf-8"))
            
            self.db_cur.execute("UPDATE Password SET name = (?), password = (?) WHERE oid != 1 AND oid == (?)", (name, password, id))
        elif name == "" and description != "" and password != "":
            # Encrypt password
            password = self.cipher.encrypt(password.encode("utf-8"))
            
            self.db_cur.execute("UPDATE Password SET description = (?), password = (?) WHERE oid != 1 AND oid == (?)", (description, password, id))

        # Update all columns
        if name != "" and description != "" and password != "":
            # Encrypt password
            password = self.cipher.encrypt(password.encode("utf-8"))
            
            self.db_cur.execute("UPDATE Password SET name = (?), description = (?) WHERE oid != 1 AND oid == (?)", (name, description, id))

        self.db.commit()
        #self.cursor_lock.release()

    def update_root_password(self, root_password: str, new_root_password: str):

        self.logger.info(f"Updating Root Password ...")
        #self.cursor_lock.acquire()

        root_password = str(root_password); new_root_password

        if not self.confirm_root(root_password):
            self.logger.info("Wrong root passsword...")
            self.db.commit()
            #self.cursor_lock.release()
            return "Wrong Root Password"
        
        else:
            # Encrypt root password
            hasher = hashlib.sha256()
            hasher.update(new_root_password.encode())
            new_root_pass = hasher.hexdigest()

            self.db_cur.execute("UPDATE Password SET password= (?) WHERE oid = 1", (new_root_pass, ))
            self.db.commit()
            #self.cursor_lock.release()

            # Change All Password encryption
            passlist = self.get_passwords()
            self.cipher_key(new_root_password)

            for password in passlist:
                self.update_password(password[0], password=password[3])
            
            #del passlist

    def delete_password(self, id: int, root_password: str):

        self.logger.info(f"deleting password with id {id} ...")

        id = str(id)

        if not self.confirm_root(root_password):
            self.logger.info("Wrong root passsword...")
            self.db.commit()
            return "Wrong Root Password"

        else:
            self.db_cur.execute("DELETE FROM password WHERE oid != 1 AND id == ?;", id)
            self.db.commit()

#TODO: Create File encryption feature (use aes encryption and option to set the decryption key
#         yourself so the file can be decrypted by other users with the key)

    def purge(self, root_password: str):

        self.logger.info("purging database passwords ...")

        if not self.confirm_root(root_password):
            self.logger.warning("Wrong root passsword...")
            self.db.commit()
            return "Wrong Root Password"

        else:
            # delete all passwords
            self.db_cur.execute("DELETE FROM password WHERE id != 1")
            self.db.commit()

    def delete_account(self, root_password: str):
        self.logger.info("Removing Database...")
        #self.cursor_lock.acquire()

        if not self.confirm_root(root_password):
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
    """ obj = Database()

    obj.create_tables("root_password")
    obj.append_password("ecode", "alayaabubakar2005@gmail.com", "Elias_code11")
    #obj.update_password(2, name="Ecode2", description="alayaabubakar@gmail.com")

    #obj.delete_account("root_password") """