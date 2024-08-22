from datetime import datetime

import mariadb
import config

class db:
    def __init__(self):
        self.conn = mariadb.connect(
            user=config.DATABASE_USER,
            password=config.DATABASE_PASSWORD,
            host=config.DATABASE_HOST,
            database=config.DATABASE_NAME
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
        return self.cursor

    def save_members(self, members):
        for member in members:
            #convert from HelloAsso format to database format
            member["payments"][0]["date"] = member["payments"][0]["date"].split("T")[0] + " " + member["payments"][0]["date"].split("T")[1].split(".")[0]
            expiration_date = datetime.strptime(member["payments"][0]["date"], '%Y-%m-%d %H:%M:%S')
            expiration_date = expiration_date.replace(year=expiration_date.year + 1)

            self.execute("SELECT COUNT(*) FROM members WHERE email=?", (member["customFields"][0]["answer"],))
            if self.cursor.fetchone()[0] == 0:
                self.execute("INSERT INTO members (name, firstname, email, token, registrationDate, expirationDate) VALUES (?, ?, ?, ?, ?, ?)",
                            (member["user"]["lastName"], member["user"]["firstName"], member["customFields"][0]["answer"], "token", member["payments"][0]["date"], expiration_date))