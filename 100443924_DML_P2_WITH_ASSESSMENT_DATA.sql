SET search_path TO "100443924_PIERIAN_GAMES_1",PUBLIC;
--A Insert a new spectator.
--sno = 100, sname =  ‘F Liza’, semail = ‘f.liza@uea.ac.uk’
INSERT INTO spectator VALUES
   (100,'F Liza','f.liza@uea.ac.uk');
   
--B(1) Insert a new event. 
--ecode  = 'A100', edesc = '100 metres sprint', elocation ='Stadium 1', 
--edate = '2024-07-12', etime='16:00', emax = 1000
INSERT INTO event VALUES
   ('A100','100 metres sprint','Stadium 1','2024-07-12','16:00',1000);
   
--E(1) Issue a ticket for an event. where ecode  =   'A100' , sno  =   100       
-- Insert into the event table
INSERT INTO event (ecode, edesc, elocation, edate, etime, emax)
SELECT 'A100', '100 metres sprint', 'Stadium 1', '2024-07-12', '16:00', 1000
WHERE NOT EXISTS (SELECT 1 FROM event WHERE ecode = 'A100');

-- Insert into the spectator table
INSERT INTO spectator (sno, sname, semail)
SELECT 100, 'J. Chin', 'j.chin@uea.ac.uk'
WHERE NOT EXISTS (SELECT 1 FROM spectator WHERE sno = 100);

-- Get the next available ticket number
INSERT INTO ticket (tno, ecode, sno)
SELECT COALESCE(MAX(tno), 0) + 1, 'A100', 100 FROM ticket
WHERE NOT EXISTS ( SELECT 1 FROM ticket WHERE ecode = 'A100' AND sno = 100
);

--F Produce a report showing the total number of spectators liable to travel to a location. 
--The table should show the total number of spectators that could travel 
--to a location on each date an event is held at a location.
SELECT 
    event.elocation AS LOCATION,
    event.edate AS EVENT_DATE,
    COUNT(spectator.sno) AS TOTAL_SPECTATORS
FROM event 
LEFT JOIN ticket  ON event.ecode = ticket.ecode
LEFT JOIN spectator  ON ticket.sno = spectator.sno
GROUP BY event.elocation, event.edate
ORDER BY event.elocation, event.edate;

--G Produce a report showing the total number of tickets issued for each event. 
--Present the data in event description sequence.
SELECT event.edesc AS EVENT_DESCRIPTION,
    COUNT(ticket.tno) AS TOTAL_TICKETS_ISSUED
FROM event 
LEFT JOIN ticket  ON event.ecode = ticket.ecode
GROUP BY event.edesc
ORDER BY event.edesc;

--H As task G but only for a given event which is specified by the event code.
--ecode = 'A100'
SELECT event.edesc AS EVENT_DESCRIPTION, 
       event.ecode AS EVENT_CODE, 
	   COUNT(ticket.tno) AS TOTAL_TICKETS_ISSUED
FROM event 
LEFT JOIN ticket  ON event.ecode = ticket.ecode
WHERE event.ecode = 'A100' 
GROUP BY event.edesc, event.ecode;

--I Produce a report showing the schedule for a given spectator. 
--The spectator is specified by his/her spectator number. 
--The schedule should contain the spectator's name and the date, location, time 
--and event description of each event for which the spectator has been issued a ticket.
--sno = 200
SELECT spectator.sname AS SPECTATOR_NAME, 
       event.edate AS EVENT_DATE, 
	   event.elocation AS EVENT_LOCATION, 
	   event.etime AS EVENT_TIME, 
	   event.edesc AS EVENT_DISCRIPTION
FROM spectator 
JOIN ticket  ON spectator.sno = ticket.sno
JOIN event  ON ticket.ecode = event.ecode
WHERE spectator.sno = 200; 

--J(1) Given a specific ticket reference number, display the name of the spectator 
--and the event code for the ticket and indicate if the ticket is valid or is cancelled.
--tno = 20
SELECT spectator.sname AS SPECTATOR_NAME, ticket.ecode AS EVENT_CODE,
       (cancel.tno IS NOT NULL) AS TICKET_IS_CANCELLED
FROM ticket 
JOIN spectator  ON ticket.sno = spectator.sno
LEFT JOIN cancel  ON ticket.tno = cancel.tno
WHERE ticket.tno = 20;

--K(1) View the details of all cancelled tickets for a specific event.
--ecode = 'A100'
SELECT cancel.tno AS TICKET_NUMBER, 
       spectator.sname AS SPECTATOR_NAME, 
	   event.edesc AS EVENT_DESCRIPTION, 
	   cancel.cdate AS CANCELLATION_DATE
FROM cancel 
JOIN spectator  ON cancel.sno = spectator.sno
JOIN event  ON cancel.ecode = event.ecode
WHERE cancel.ecode = 'A100'; 

--D Delete an event. All the tickets for the event must be cancelled 
--before an event can be deleted.
--ecode = 'A100'
--Comment : Made Trigger function for cancel ticket record transfer to cancel table 
--before delete event. Below code for delete event 
--and trigger function executed and record of cancel ticket(output) in next task (Kii).
CREATE OR REPLACE FUNCTION cancel_tickets_and_delete_event()
RETURNS TRIGGER AS $$
DECLARE
    v_ticket_number INTEGER;
BEGIN
    -- cancel all  associated tickets before delete event
    INSERT INTO cancel (tno, ecode, sno, cuser)
    SELECT ticket.tno, ticket.ecode, ticket.sno, 'Management 1' 
	FROM ticket WHERE ticket.ecode = OLD.ecode;
    -- Delete the associated tickets
    DELETE FROM ticket WHERE ecode = OLD.ecode;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
-- Create the trigger
CREATE TRIGGER cancel_tickets_and_delete_event_trigger
BEFORE DELETE ON event
FOR EACH ROW
EXECUTE FUNCTION cancel_tickets_and_delete_event();
DELETE FROM event WHERE ecode = 'A100';

--K(2) View the details of all cancelled tickets for a specific event.
--ecode = 'A100'
--Comment: from above task D output reflect here as mentioned in previous task comment.
--         All canceled tickets records viewed.
select * from cancel;

--C(1) Delete a spectator. The spectator must not have any valid (i.e. not cancelled) 
--tickets before it can be deleted.
--sno = 300;
DELETE FROM spectator
 WHERE sno = 300 AND sno NOT IN ( SELECT sno FROM ticket
 WHERE tno NOT IN ( SELECT tno FROM cancel)
);

--C(2) Delete a spectator. The spectator must not have any valid (i.e. not cancelled) 
--tickets before it can be deleted.
--sno = 400;
DELETE FROM spectator
 WHERE sno = 400 AND sno NOT IN ( SELECT sno FROM ticket
 WHERE tno NOT IN ( SELECT tno FROM cancel)
);

--J(2) Given a specific ticket reference number, display the name of the spectator 
--and the event code for the ticket and indicate if the ticket is valid or is cancelled.
--tno = 20
SELECT
    spectator.sname AS SPECTATOR_NAME,
    ticket.ecode AS EVENT_CODE,
    CASE
        WHEN cancel.tno IS NOT NULL THEN 'Cancelled'
        ELSE 'Valid'
    END AS TICKET_STATUS
FROM ticket 
JOIN spectator ON ticket.sno = spectator.sno
LEFT JOIN
    cancel ON ticket.tno = cancel.tno 
	WHERE ticket.tno = 20;
	
--E(2) Issue a ticket for an event.  where ecode  =  'JUDO'  , sno  =   400 
INSERT INTO ticket (tno, ecode, sno)
VALUES (
    (SELECT COALESCE(MAX(tno), 0) + 1 FROM ticket),
    'JUDO',400
);

--B(2) Insert a new event. 
--ecode  = 'A400', edesc = '400 metres sprint', elocation ='Stadium 1',
--edate = '2024-07-12', etime='10:00', emax = 1000

INSERT INTO event (ecode, edesc, elocation, edate, etime, emax)
VALUES ('A400', '400 metres sprint', 'Stadium 1', '2024-07-12', '10:00', 1000);

--B(3) Insert a new event. 
--ecode  = 'A900', edesc = '900 metres sprint', elocation ='Stadium 1', 
--edate = '2023-07-12', etime='10:00', emax = 1000

INSERT INTO event (ecode, edesc, elocation, edate, etime, emax)
VALUES ('A900', '900 metres sprint', 'Stadium 1', '2023-07-12', '10:00', 1000);

--E(3) Issue a ticket for an event. where ecode  =  'AXXX'  , sno  =   100 
INSERT INTO ticket (tno, ecode, sno)
VALUES (
    (SELECT COALESCE(MAX(tno), 0) + 1 FROM ticket),
    'AXXX',100
);
--E(4) Issue a ticket for an event.  where ecode  =  'A400'  , sno  =   900
INSERT INTO ticket (tno, ecode, sno)
VALUES (
    (SELECT COALESCE(MAX(tno), 0) + 1 FROM ticket),
    'A400',900
);
--L Delete the contents of the database tables. 

-- Delete all records from the ticket table
DELETE FROM ticket;
-- Delete all records from the cancel table
DELETE FROM cancel;
-- Delete all records from the spectator table
DELETE FROM spectator;
-- Delete all records from the event table
DELETE FROM event;




























   
   
