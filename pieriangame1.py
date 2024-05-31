# Connection between psgresql( database) and python interface.
import time

import psycopg2
conn = psycopg2.connect(user="nxp23mgu", password="ExplainSoupAlong46?",
                        host='cmpstudb-01.cmp.uea.ac.uk', port="5432", database="nxp23mgu")
conn.autocommit=True
cur = conn.cursor()
cur.execute("SET search_path TO 'PIERIAN_GAMES_1',public;")
# Clear data in Output file function
def clearOutput():
    with open("output.txt", "w") as clearfile:
        clearfile.write('')

# Query Output data into text file function
def writeOutput(output):
    with open("output.txt", "a") as myfile:
        myfile.write(str(output))

# Create a Dictionary for  taking data from input file for reference.
task_values_dictionary = {}
file_open = open('input.txt', 'r')
clearOutput()
data = file_open.readlines()
for i in data:
    i = i.strip("\n")
    i = i.split("#")
    if len(i) > 1:
        task_values_dictionary[i[0]] = i[1:]
    else:
        task_values_dictionary[i[0]] = "None"
print(task_values_dictionary)

# Query_a
# Insert a new spectator.
for key, value in task_values_dictionary.items():
    if key == 'A':
        writeOutput("TASK " + key + "\n")
        query_a = f"INSERT INTO spectator (sno,sname,semail) VALUES ({int(value[0])}, '{value[1]}', '{value[2]}');"
        cur.execute(query_a)
        # Ensure that query functioning properly
        verify = f"select * from spectator where sno={int(value[0])};"
        cur.execute(verify)
        writeOutput(cur.statusmessage + "\n")
        verify_insert = cur.fetchall()
        for spectator_data in verify_insert:
            if spectator_data[0] == int(value[0]) and spectator_data[1] == value[1] and spectator_data[2] == \
                    value[2]:
                writeOutput("new spectator data verified successfully\n")
                writeOutput(str(spectator_data))
                writeOutput("\n")
                break
        writeOutput("\n")
    # Query_b
    # Insert a new event.
    elif key == 'B':
        writeOutput("TASK " + key + "\n")
        query_b = f"INSERT INTO event (ecode, edesc, elocation, edate, etime, emax) \
VALUES ('{value[0]}','{value[1]}','{value[2]}','{value[3]}','{value[4]}', {int(value[5])});"
        cur.execute(query_b)
        # Ensure that query functioning properly
        verify = f"select * from event where ecode='{value[0]}';"
        cur.execute(verify)
        writeOutput(cur.statusmessage + "\n")
        verify_insert = cur.fetchall()
        for event_data in verify_insert:
            if event_data[0] == value[0]:
                writeOutput("new event data inserted successfully\n")
                writeOutput(str(event_data))
                writeOutput("\n")
                break
        writeOutput("\n")
    # Query_c
    # Delete a spectator.The spectator must not have any valid (i.e. not cancelled)tickets before it can be deleted.
    elif key == 'C':
        writeOutput("TASK " + key + "\n")
        query_c = f"DELETE FROM spectator WHERE sno = {int(value[0])} AND \
sno NOT IN ( SELECT sno FROM ticket WHERE tno NOT IN ( SELECT tno FROM cancel));"
        cur.execute(query_c)
        # Ensure that query functioning properly
        verify = f"select * from spectator where sno={int(value[0])};"
        cur.execute(verify)
        writeOutput(cur.statusmessage + "\n")
        verify_insert = cur.fetchall()
        if not verify_insert:
            writeOutput("Spectator data deleted successful\n")
            writeOutput(str(verify_insert))
            writeOutput("\n")
        writeOutput("\n")
    # Query_d
    # Delete an event. All the tickets for the event must be cancelled before an event can be deleted.
    elif key == 'D':
        writeOutput("TASK " + key + "\n")
        query_d = (f"DELETE FROM event WHERE ecode = '{value[0]}' AND ecode NOT IN "
                   f"(SELECT ecode FROM ticket WHERE tno NOT IN (SELECT tno FROM cancel));")
        cur.execute(query_d)
        # Ensure that query functioning properly
        verify = f"select * from event where ecode = '{(value[0])}';"
        cur.execute(verify)
        writeOutput(cur.statusmessage + "\n")
        verify_insert = cur.fetchall()
        if not verify_insert:
            writeOutput(str(verify_insert))
            writeOutput("\n")
            writeOutput("Event data deleted successful\n")
        writeOutput("\n")

    # Query_e
    # Issue a ticket for an event. A spectator may have only one ticket for a given event.
    # TO run this query_e following pre-requisition data in the respective table
    elif key == 'E':
        writeOutput("TASK " + key + "\n")
        # 1st insert spectator data in to spectator table
        query_insert_spectator = (f"INSERT INTO spectator (sno,sname,semail) "
                                  f"VALUES (100, 'Jamie','jamie@gmail.com');")
        cur.execute(query_insert_spectator)
        # 2nd insert event data into event table
        query_insert_event = (f"INSERT INTO event (ecode, edesc, elocation, edate, etime, emax) "
                              f"VALUES ('A100','football','SPORT_PARK','2024-07-15','10:30:00', 450);")
        cur.execute(query_insert_event)
        # 3rd insert ticket data into ticket table
        query_insert_ticket = f"INSERT INTO ticket (tno,ecode,sno) VALUES ({int(value[0])},'{value[1]}',{int(value[2])});"
        cur.execute(query_insert_ticket)
        # with the available data in respective tables, we can issue only ticket for each event to each spectator.
        query_e = (f"INSERT INTO ticket (tno, ecode, sno) SELECT 2, '{value[1]}',{int(value[2])} WHERE "
                   f"NOT EXISTS( SELECT ecode FROM ticket WHERE ecode IN (SELECT ticket.ecode FROM ticket ,event "
                   f"WHERE ticket.ecode = event.ecode));")
        cur.execute(query_e)
        # Ensure that query functioning properly
        verify = f"select * from ticket where tno = 2;"
        cur.execute(verify)
        writeOutput(cur.statusmessage + "\n")
        verify_insert_1 = cur.fetchall()
        if not verify_insert_1:
            writeOutput(str(verify_insert_1))
            writeOutput("\n")
            writeOutput("Issue a single ticket for single event  to single spectator successful\n")
        writeOutput("\n")

    # Query_f
    # Produce a report showing the total number of spectators liable to travel to a location.
    # The table should show the total number of spectators that could travel to a location
    # on each date an event is held at a location.
    elif key == 'F':
        writeOutput("TASK " + key + "\n")
        query_f = (f"SELECT event.elocation AS LOCATION, event.edate AS EVENT_DATE, "
                   f"COUNT(ticket.sno) AS TOTAL_SPECTATORS FROM event JOIN ticket  ON event.ecode = ticket.ecode"
                   f" GROUP BY event.elocation, event.edate ORDER BY event.elocation, event.edate;")
        cur.execute(query_f)
        # Ensure that query functioning properly
        writeOutput(cur.statusmessage + "\n")
        verify_ticket_report = cur.fetchall()
        if verify_ticket_report:
            writeOutput("Ticket report generated successfully\n")
            writeOutput(str(verify_ticket_report))
            writeOutput("\n")
        writeOutput("\n")

    # Query_g
    # Produce a report showing the total number of tickets issued for each event.
    # Present the data in event description sequence.
    elif key == 'G':
        writeOutput("TASK " + key + "\n")
        query_g = (f"SELECT event.edesc AS EVENT_DESCRIPTION,event.ecode AS EVENT_CODE,"
                   f"COUNT(ticket.tno) AS TOTAL_TICKETS_ISSUED FROM event "
                   f"LEFT JOIN ticket  ON event.ecode = ticket.ecode "
                   f"GROUP BY event.edesc, event.ecode ORDER BY event.edesc;")
        cur.execute(query_g)
        # Ensure that query functioning properly
        writeOutput(cur.statusmessage + "\n")
        verify_event_report = cur.fetchall()
        if verify_event_report:
            writeOutput("Event report generated successfully\n")
            writeOutput(str(verify_event_report))
            writeOutput("\n")
        writeOutput("\n")

    # Query_h
    # As task G but only for a given event which is specified by the event code.
    elif key == 'H':
        writeOutput("TASK " + key + "\n")
        query_h = (f"SELECT event.edesc AS EVENT_DESCRIPTION, event.ecode AS EVENT_CODE, "
                   f"COUNT(ticket.tno) AS TOTAL_TICKETS_ISSUED FROM event "
                   f"LEFT JOIN ticket  ON event.ecode = ticket.ecode WHERE event.ecode = '{value[0]}'"
                   f"GROUP BY event.edesc, event.ecode;")
        cur.execute(query_h)
        # Ensure that query functioning properly
        writeOutput(cur.statusmessage + "\n")
        verify_specific_ticket_ecode_event = cur.fetchall()
        if verify_specific_ticket_ecode_event:
            writeOutput("For Event , Specific ticket report generated by event code successfully\n")
            writeOutput(str(verify_specific_ticket_ecode_event))
            writeOutput("\n")
        writeOutput("\n")

    # Query_i
    # Produce a report showing the schedule for a given spectator. The spectator is specified by his/her
    # spectator number. The schedule should contain the spectator's name and the date, location, time and event
    # description of each event for which the spectator has been issued a ticket.
    elif key == 'I':
        writeOutput("TASK " + key + "\n")
        query_i = (f"SELECT spectator.sname AS SPECTATOR_NAME,event.edate AS EVENT_DATE,"
                   f"event.elocation AS EVENT_LOCATION,event.etime AS EVENT_TIME,event.edesc AS EVENT_DISCRIPTION "
                   f"FROM spectator JOIN ticket  ON spectator.sno = ticket.sno "
                   f"JOIN event  ON ticket.ecode = event.ecode WHERE spectator.sno = '{value[0]}';")
        cur.execute(query_i)
        # Ensure that query functioning properly
        writeOutput(cur.statusmessage + "\n")
        verify_schedule_spectator = cur.fetchall()
        if verify_schedule_spectator:
            writeOutput("spectator schedule report generated successfully\n")
            writeOutput(str(verify_schedule_spectator))
            writeOutput("\n")
        writeOutput("\n")

    # Query_J
    # Given a specific ticket reference number, display the name of the spectator and
    # the event code for the ticket and indicate if the ticket is valid or is cancelled.
    elif key == 'J':
        writeOutput("TASK " + key + "\n")
        query_j = (f"SELECT spectator.sname AS SPECTATOR_NAME, ticket.ecode AS EVENT_CODE,"
                   f"(cancel.tno IS NOT NULL) AS TICKET_IS_CANCELLED FROM ticket "
                   f"JOIN spectator  ON ticket.sno = spectator.sno LEFT JOIN cancel  ON ticket.tno = cancel.tno "
                   f"WHERE ticket.tno = '{int(value[0])}';")
        cur.execute(query_j)
        # Ensure that query functioning properly
        writeOutput(cur.statusmessage + "\n")
        verify_valid_specific_ticket = cur.fetchall()
        if verify_valid_specific_ticket:
            writeOutput("Specific ticket ref number and name displayed successfully\n")
            writeOutput(str(verify_valid_specific_ticket))
            writeOutput("\n")
        else:
            writeOutput(f"Creating new ticket {value[0]} \n")

            # 1st insert spectator data in to spectator table
            query_insert_spectator_n = (f"INSERT INTO spectator (sno,sname,semail) "
                                      f"VALUES (200, 'Alex','alex@gmail.com');")
            cur.execute(query_insert_spectator_n)
            # 2nd insert event data into ticket table
            query_insert_ticket_n = (f"INSERT INTO ticket(tno,ecode,sno)"
                                  f"VALUES ({int(value[0])},'A100',200);")
            cur.execute(query_insert_ticket_n)
            cur.execute(query_j)
            verify_valid_specific_ticket = cur.fetchall()
            if verify_valid_specific_ticket:
                writeOutput("Specific ticket ref number and name displayed successfully\n")
                writeOutput(str(verify_valid_specific_ticket))
                writeOutput("\n")
                writeOutput("\n")




    # Query_k
    # View the details of all cancelled tickets for a specific event.
    elif key == 'K':
        writeOutput("TASK " + key + "\n")
        select_spectator_query = f"select tno, sno from ticket where ecode='A100';"
        cur.execute(select_spectator_query)
        get_ticket_spec_list = cur.fetchall()
        tno, sno = 0, 0
        for ticket_spec in get_ticket_spec_list:
            tno, sno = ticket_spec[0], ticket_spec[1]
        writeOutput(f"Fetched spectator {sno} who's assigned the ticket {tno} for event {value[0]}\n")
        query_pre_k = (f"insert into cancel (tno,ecode,sno,cuser)"
                       f"values ({tno},'{value[0]}',{sno},'prnav')")
        writeOutput(str(query_pre_k))
        writeOutput("\n")
        cur.execute(query_pre_k)

        query_k = (f"SELECT cancel.tno AS TICKET_NUMBER,spectator.sname AS SPECTATOR_NAME,"
                   f"event.edesc AS EVENT_DESCRIPTION,cancel.cdate AS CANCELLATION_DATE FROM cancel "
                   f"JOIN spectator  ON cancel.sno = spectator.sno JOIN event  ON cancel.ecode = event.ecode "
                   f"WHERE cancel.ecode = '{value[0]}';")
        cur.execute(query_k)
        writeOutput(cur.statusmessage + "\n")
        verify_cancel_details = cur.fetchall()
        # Ensure that query functioning properly
        for cancelled_data in verify_cancel_details:
            if cancelled_data[0] == tno:
                writeOutput(f"Cancelled tickets report for event {value[0]} generated successfully\n")
                writeOutput(str(verify_cancel_details))
                writeOutput("\n")
                break
        writeOutput("\n")

    # Query_l
    # Delete the contents of the database tables.
    elif key == 'L':
        writeOutput("TASK " + key + "\n")
        query_L = f"DELETE FROM cancel; DELETE FROM ticket; DELETE FROM spectator; DELETE FROM event;"
        cur.execute(query_L)
        # Ensure that query functioning properly
        verify_delete_on_event = "select * from event"
        cur.execute(verify_delete_on_event)
        writeOutput(cur.statusmessage + "\n")
        event_data_list = cur.fetchall()
        if not event_data_list:
            writeOutput(str(event_data_list))
            writeOutput("\n")
            writeOutput("Delete all data from event table successful\n")
        writeOutput("\n")

        verify_delete_on_spectator = "select * from spectator"
        cur.execute(verify_delete_on_spectator)
        writeOutput(cur.statusmessage + "\n")
        spectator_data_list = cur.fetchall()
        if not spectator_data_list:
            writeOutput(str(spectator_data_list))
            writeOutput("\n")
            writeOutput("Delete all data from spectator table successful\n")
        writeOutput("\n")

        verify_delete_on_ticket = "select * from ticket"
        cur.execute(verify_delete_on_ticket)
        writeOutput(cur.statusmessage + "\n")
        ticket_data_list = cur.fetchall()
        if not ticket_data_list:
            writeOutput(str(ticket_data_list))
            writeOutput("\n")
            writeOutput("Delete all data from ticket table successful\n")
        writeOutput("\n")

        verify_delete_on_cancel = "select * from cancel"
        cur.execute(verify_delete_on_cancel)
        writeOutput(cur.statusmessage + "\n")
        cancel_data_list = cur.fetchall()
        if not cancel_data_list:
            writeOutput(str(cancel_data_list))
            writeOutput("\n")
            writeOutput("Delete all data from cancel table successful\n")
        writeOutput("\n")
