#!/usr/bin/env python
# coding=utf-8

class LogEntry(object):
    def __init__(self, main, id=0, dependancy="", viewed_by=[], members_concerned=[], created_by="", log_to="", log_type="", log_description="", log_time=""):
        self.main = main
        self.id = id
        self.dependancy = dependancy
        if len(viewed_by) == 0:
            self.viewed_by = ["obolduc", "vdelbroucq", "lclavet", "costiguy", "dcayerdesforges", "yshan", "earismendez", "jberger", "lgregoire", "yjobin", "cgonnord", "mroz", "slachapelle", "thoudon", "erodrigue", "mbeaudoin", "mchretien", "achaput"]
        else:
            self.viewed_by = viewed_by
        self.members_concerned = members_concerned
        self.created_by = created_by
        self.log_to = log_to
        self.type = log_type
        self.description = log_description
        self.time = log_time

    def print_log(self):
        print "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.dependancy, self.viewed_by, self.members_concerned, self.created_by, self.log_to, self.type, self.description, self.time)

    def add_log_to_database(self):
        self.main.cursor.execute('''INSERT INTO log(log_dependancy, viewed_by, members_concerned, created_by, log_to, log_type, log_description, log_time) VALUES(?,?,?,?,?,?,?,?)''', (self.dependancy, ",".join(self.viewed_by), ",".join(self.members_concerned), self.created_by, self.log_to, self.type, self.description, self.time,))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

