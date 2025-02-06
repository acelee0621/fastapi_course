import dbm

FILE_DB = "file_db"
SHARE_DB = "share_db"


class FileDB:
    def __init__(self):
        pass

    def create_file(self, unique_name: str, file_name: str):
        db = dbm.open("FILE_DB", "c")
        db[unique_name] = file_name.encode("utf-8")
        db.close()

    def get_file(self, unique_name: str):
        db = dbm.open("FILE_DB", "r")
        files = db.keys()
        find_name = bytes(unique_name, encoding="utf-8")
        if find_name in files:
            return db.get(unique_name)

    def get_all_files(self):
        files = dbm.open(FILE_DB, "r")
        codes = dbm.open(SHARE_DB, "r")
        all_files = []
        for key in files.keys():
            file = {
                "file_name": str(files[key], encoding="utf-8"),
                "unique_name": str(key, encoding="utf-8"),
                "code": str(codes[key], encoding="utf-8"),
            }
            all_files.append(file)
        return all_files

    def create_share_code(self, unique_name: str, code: str):
        db = dbm.open("SHARE_DB", "c")
        db[unique_name] = code
        db.close()

    def get_share_code(self, unique_name: str):
        db = dbm.open(SHARE_DB, "r")
        return db[unique_name]


file_db = FileDB()
