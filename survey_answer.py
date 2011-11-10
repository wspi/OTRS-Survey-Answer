#!/usr/bin/env python

# Author: Wagner Spirigoni
# E-mail: wagner@wspi.com.br
# Date: 8/8/2011

import MySQLdb

# Survey's ID (Use the ID of your survey (check the id from the database))
id_survey = 1

# Change your password and user
con = MySQLdb.connect('127.0.0.1',  'otrs',  'PASSWORD')
con.select_db('otrs')
cursor = con.cursor()

# Get the first Question of the Survey (Yes/No Question)
cursor.execute("select id from survey_question where survey_id=%s", id_survey)
Question = cursor.fetchone()

# Get all the Answers from the Yes/No Question from the answers that was not checked already
cursor.execute("select vote_value, request_id from survey_vote where request_id not in (select request_id from survey_processed) and  question_id=%s", Question[0])
Answers = cursor.fetchall()

for answer in Answers:
    # Get the Ticket Id from the answer selected
    cursor.execute("select ticket_id from survey_request where id=%s", answer[1])
    Request = cursor.fetchone()

    # Get the last queue from the ticket (Before sent to the Waiting Confirmation Queue)
    cursor.execute("select queue_id from ticket_history where ticket_id=%s", Request[0])
    old_queue = cursor.fetchone()
    
    # Get the ticket state (Closed or Waiting Confirmation) If its already closed doesnt do nothing
    cursor.execute("select ticket_state_id from ticket where id=%s", Request[0])
    Ticket = cursor.fetchone()
        
    # If there is no old_queue (not changed to the Waiting Confirmation queue), the ticket is already closed or it was reopened (ticket_state_id = 12) pass to the next ticket
    if old_queue == None or Ticket[0] == 2 or Ticket[0] == 12:
        pass
    else:
        # If the Answer is Yes, locks the ticket, closes it and change to the last queue it was
        if answer[0] == "Yes":
            cursor.execute("update ticket set ticket_lock_id=2, ticket_state_id=2, queue_id=%s where id=%s" % (old_queue[0], Request[0]))
        else:
            # IF the Answer its not Yes, unlocks the ticket, change the state to reopen (Created in Id 12, check your database) and change to the last queue it was
            cursor.execute("update ticket set ticket_lock_id=1, ticket_state_id=12, queue_id=%s where id=%s" % (old_queue[0], Request[0]))

        # add the current answer to the table that wont be checked again        
        cursor.execute("insert into survey_processed (request_id, process_time) values (%s, NOW())" % (answer[1]))
    
cursor.close()
con.close()

