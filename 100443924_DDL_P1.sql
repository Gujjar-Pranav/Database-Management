CREATE SCHEMA "100443924_PIERIAN_GAMES_1";
SET search_path TO "100443924_PIERIAN_GAMES_1",PUBLIC;

-- Create the event table with primary key and constraints
CREATE TABLE event (
 ecode CHAR(4) PRIMARY KEY,
 edesc VARCHAR(20) NOT NULL,
 elocation VARCHAR(20) NOT NULL,
 edate DATE NOT NULL CHECK (edate >= '2024-07-01' AND edate <= '2024-07-31'),
 etime TIME NOT NULL CHECK (etime >= '09:00:00'),
 emax SMALLINT NOT NULL CHECK (emax >= 1 AND emax <= 1000)
);
SELECT * FROM event;

-- Create the spectator table with a primary key and constraints
CREATE TABLE spectator (
 sno INTEGER PRIMARY KEY,
 sname VARCHAR(20) NOT NULL,
 semail VARCHAR(20) NOT NULL
);
SELECT * FROM spectator;

-- Create the ticket table with a manual primary key, foreign keys, and constraints
CREATE TABLE ticket (
 tno INTEGER PRIMARY KEY,
 ecode CHAR(4) NOT NULL,
 sno INTEGER NOT NULL,
 FOREIGN KEY (ecode) REFERENCES event(ecode),
 FOREIGN KEY (sno) REFERENCES spectator(sno),
 CHECK (tno >= 1)
);
SELECT * FROM ticket;

-- Create the cancel table 
CREATE TABLE cancel (
 tno INTEGER PRIMARY KEY,
 ecode CHAR(4) NOT NULL,
 sno INTEGER NOT NULL,
 cdate TIMESTAMP DEFAULT current_timestamp,
 cuser VARCHAR(128) NOT NULL
);
SELECT * FROM CANCEL;

-- Trigger function to transfer old event record to cancel table
CREATE OR REPLACE FUNCTION event_cancel_ticket()
    RETURNS trigger
    LANGUAGE 'plpgsql' 
AS 
$$
BEGIN
    INSERT INTO cancel (tno, ecode, sno, cdate, cuser)
    SELECT tno, ecode, sno, CURRENT_DATE, 'Management1'
    FROM ticket
    WHERE ecode = NEW.ecode;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_event_update
    AFTER UPDATE OF elocation, edate, etime
    ON event
    FOR EACH ROW
    EXECUTE FUNCTION event_cancel_ticket();
-- CHECK TRIGGER FUNCTION BY UPDATE EVENT LOCATION
update event set elocation='USA' where ecode='P001'
select * from event;
select * from cancel;

-- Create a view function for event calncellation details
CREATE OR REPLACE FUNCTION event_cancellation_details_view()
RETURNS TABLE (
    ticket_number INTEGER,
	spectator_name VARCHAR(20),
    event_code CHAR(4),
    event_description VARCHAR(20),
    event_location VARCHAR(20),
    event_date DATE,
    event_time TIME,
    cancellation_date TIMESTAMP,
    cancellation_user VARCHAR(128)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.tno AS ticket_number,
        s.sname AS spectator_name,
        e.ecode AS event_code,
        e.edesc AS event_description,
        e.elocation AS event_location,
        e.edate AS event_date,
        e.etime AS event_time,
        c.cdate AS cancellation_date,
        c.cuser AS cancellation_user
    FROM
        ticket t
    JOIN spectator s ON t.sno = s.sno
    JOIN event e ON t.ecode = e.ecode
    JOIN cancel c ON t.tno = c.tno;
END;
$$ LANGUAGE plpgsql;

-- Create the view for events cancellation
CREATE OR REPLACE VIEW event_cancellation AS
SELECT * FROM event_cancellation_details_view();
SELECT * from event_cancellation;


