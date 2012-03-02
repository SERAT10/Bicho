# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Bitergia
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:  Alvaro del Castillo <acs@bitergia.com>
#


from Bicho.Config import Config

from Bicho.backends import Backend
from Bicho.utils import printdbg, printout, printerr
from Bicho.db.database import DBIssue, DBBackend, get_database

import json
import os
import pprint
import random
import sys
import time
import urllib

from storm.locals import DateTime, Int, Reference, Unicode


class DBAlluraIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_allura'

    id = Int(primary=True)
    issue_id = Int()
    
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBAlluraIssueExtMySQL(DBAlluraIssueExt):
    """
    MySQL subclass of L{DBBugzillaIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_allura ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    issue_id INTEGER NOT NULL, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBAlluraBackend(DBBackend):
    """
    Adapter for Allura backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBAlluraIssueExtMySQL]

class Allura():
    
    def __init__(self):
        self.delay = Config.delay
        self.url = Config.url
        
    def analyze_bug(self, bug_url):
        #Retrieving main bug information
        printdbg(bug_url)        

        try:
            f = urllib.urlopen(bug_url)
            json_ticket = f.read()
            issue = json.loads(json_ticket)
    
        except Exception, e:
            printerr("Error in bug analysis: " + bug_url);
            print(e)
            raise

        #Retrieving changes
#        bug_activity_url = url + "show_activity.cgi?id=" + bug_id
#        printdbg( bug_activity_url )
#        data_activity = urllib.urlopen(bug_activity_url).read()
#        parser = SoupHtmlParser(data_activity, bug_id)
#        changes = parser.parse_changes()
#        for c in changes:
#            issue.add_change(c)
        return issue


    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))
        
        bugs = [];
        bugsdb = get_database (DBAlluraBackend())
        
        # url_ticket = "http://sourceforge.net/rest/p/allura/tickets/3824/"
        url_tickets = "http://sourceforge.net/rest/p/allura/tickets"
        self.url = url_tickets;
        
        if self.url.find("tickets/")>0:
            bugs.append(self.url.split("tickets/")[1].strip('/'))

        else:
            # f = urllib.urlopen(url)
            f = open(os.path.join(os.path.dirname(__file__),"tickets_allura.json"));
            ticketList_json = f.read()
            f.close()
            ticketList = json.loads(ticketList_json)
            for ticket in ticketList["tickets"]:
                bugs.append(ticket["ticket_num"])                    
        
        nbugs = len(bugs)
        
        if len(bugs) == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)

        print "TOTAL BUGS", str(len(bugs))
        
        test_bugs = bugs[random.randint(0,len(bugs))::100][0:1]
                
        for bug in test_bugs:
            try:
                issue_url = url_tickets+"/"+str(bug)
                issue_data = self.analyze_bug(issue_url)
                pprint.pprint(issue_data) 
            except Exception, e:
                printerr("Error in function analyze_bug " + issue_url)
                print(e)

#            try:
#                bugsdb.insert_issue(issue_data, dbtrk.id)
#            except UnicodeEncodeError:
#                printerr("UnicodeEncodeError: the issue %s couldn't be stored"
#                      % (issue_data.issue))

            time.sleep(self.delay)
            
        printout("Done. %s bugs analyzed" % (len(bugs)))

        

def test_parse_ticket ():
    url = "http://sourceforge.net/rest/p/allura/tickets/3824/"
    json = urllib2.urlopen(url)

    parser = AlluraParser()
    parser.parse_issue(json)
        
if __name__ == "__main__":
    test_parse_ticket()

Backend.register_backend('allura', Allura)