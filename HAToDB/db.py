from datetime import datetime

import mariadb
import config
import random
import mail

class Db:
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
        email = mail.Mail()
        for member in members:
            self.execute("SELECT COUNT(*) FROM members WHERE email=?", (member["customFields"][0]["answer"],))
            if self.cursor.fetchone()[0] == 0:
                # convert from HelloAsso format to database format
                member["payments"][0]["date"] = member["payments"][0]["date"].split("T")[0] + " " + \
                                                member["payments"][0]["date"].split("T")[1].split(".")[0]
                expiration_date = datetime.strptime(member["payments"][0]["date"], '%Y-%m-%d %H:%M:%S').replace(year=datetime.now().year + 1)

                token = random.randint(100000, 999999)

                self.execute("INSERT INTO members (name, firstname, email, registrationToken, registrationDate, expirationDate) VALUES (?, ?, ?, ?, ?, ?)",
                            (member["user"]["lastName"], member["user"]["firstName"], member["customFields"][0]["answer"], token, member["payments"][0]["date"], expiration_date))

                email.sendRegistrationMail(member["user"]["firstName"], token, member["customFields"][0]["answer"])
        del email
