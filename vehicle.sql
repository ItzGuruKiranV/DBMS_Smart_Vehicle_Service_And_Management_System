-- ------------------------------------------------------
-- 1. CLEANUP AND SETUP
-- ------------------------------------------------------
-- Drop database if it exists, to ensure a clean run.
DROP DATABASE IF EXISTS vehicle;
CREATE DATABASE vehicle;
USE vehicle;

-- Change the delimiter for functions, procedures, and triggers.
DELIMITER $$

-- ------------------------------------------------------
-- 2. CORRECTED TABLE CREATION (Professional Schema)
-- ------------------------------------------------------

-- OWNER Table (FIXED: Ph_no syntax error corrected)
CREATE TABLE Owner (
    Owner_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Ph_no VARCHAR(15) NOT NULL,  -- *FIXED: Removed the extra dot '.'*
    Email VARCHAR(100),
    Address VARCHAR(255)
)$$

-- VEHICLE Table
CREATE TABLE Vehicle (
    V_id INT AUTO_INCREMENT PRIMARY KEY,
    Owner_id INT NOT NULL,
    License VARCHAR(50),
    Model VARCHAR(100),
    Milage INT,
    V_no VARCHAR(50),
    FOREIGN KEY (Owner_id) REFERENCES Owner(Owner_id)
)$$

-- SERVICE_CENTER Table (CORRECTED: V_id removed as a Center serves many vehicles)
CREATE TABLE Service_Center (
    Center_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Location VARCHAR(100),
    Contact_no VARCHAR(15)
)$$

-- MECHANIC Table
CREATE TABLE Mechanic (
    Mec_id INT AUTO_INCREMENT PRIMARY KEY,
    Center_id INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    P_no VARCHAR(15),
    Specialization VARCHAR(100),
    FOREIGN KEY (Center_id) REFERENCES Service_Center(Center_id)
)$$

-- SERVICE_TYPE Table (CORRECTED: V_id removed as a Type applies to many vehicles)
CREATE TABLE Service_Type (
    Type_id INT AUTO_INCREMENT PRIMARY KEY,
    Oil_service BOOLEAN,
    Water_wash BOOLEAN,
    Estimated_cost DECIMAL(10, 2),
    Description TEXT
)$$

-- SERVICE_RECORD Table (This is the central link for service instances)
CREATE TABLE Service_Record (
    Record_id INT AUTO_INCREMENT PRIMARY KEY,
    V_id INT NOT NULL,
    Center_id INT NOT NULL,
    Type_id INT NOT NULL,
    Service_date DATE,
    Cost DECIMAL(10, 2),
    FOREIGN KEY (V_id) REFERENCES Vehicle(V_id),
    FOREIGN KEY (Center_id) REFERENCES Service_Center(Center_id),
    FOREIGN KEY (Type_id) REFERENCES Service_Type(Type_id)
)$$

-- MAINTENANCE_SCHEDULE Table
CREATE TABLE Maintenance_Schedule (
    Schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    V_id INT NOT NULL,
    Schedule_date DATE,
    Reminder_status BOOLEAN,
    FOREIGN KEY (V_id) REFERENCES Vehicle(V_id)
)$$

-- PAYMENT Table (CORRECTED: Added Record_id to link payment to a service)
CREATE TABLE Payment (
    Trans_id INT AUTO_INCREMENT PRIMARY KEY,
    Record_id INT NOT NULL,  -- *CRITICAL FIX*
    Mec_id INT NOT NULL,
    Amount DECIMAL(10, 2),
    UPI VARCHAR(100),
    Credit_card VARCHAR(100),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Added default for professionalism
    Status VARCHAR(50),
    FOREIGN KEY (Record_id) REFERENCES Service_Record(Record_id),
    FOREIGN KEY (Mec_id) REFERENCES Mechanic(Mec_id)
)$$

-- REVIEW Table
CREATE TABLE Review (
    Review_id INT AUTO_INCREMENT PRIMARY KEY,
    Type_id INT NOT NULL,
    Ratings INT CHECK (Ratings BETWEEN 1 AND 5),
    Review_text TEXT,
    FOREIGN KEY (Type_id) REFERENCES Service_Type(Type_id)
)$$

-- SERVICE_ASSIGNMENTS Table (Junction table)
CREATE TABLE Service_Assignments (
    service_center_id INT,
    mechanic_id INT,
    record_id INT,
    PRIMARY KEY (service_center_id, mechanic_id, record_id),
    FOREIGN KEY (service_center_id) REFERENCES Service_Center(Center_id),
    FOREIGN KEY (mechanic_id) REFERENCES Mechanic(Mec_id),
    FOREIGN KEY (record_id) REFERENCES Service_Record(Record_id)
)$$

-- ------------------------------------------------------
-- 3. SAMPLE DATA INSERTS (Adjusted for corrected schema)
-- ------------------------------------------------------

INSERT INTO Owner (Owner_id, Name, Ph_no, Email, Address) VALUES
(1, 'John Doe', '1234567890', 'john@example.com', '123 Elm St'),
(2, 'Jane Smith', '0987654321', 'jane@example.com', '456 Oak St'),
(3, 'Alice Brown', '2223334444', 'alice@example.com', '789 Birch St'),
(4, 'David Green', '5556667777', 'david@example.com', '1010 Cedar St'),
(5, 'Emily White', '8889990000', 'emily@example.com', '2020 Walnut St');

INSERT INTO Vehicle (V_id, Owner_id, License, Model, Milage, V_no) VALUES
(1, 1, 'ABC123', 'Toyota Corolla', 15000, 'V001'),
(2, 2, 'XYZ789', 'Honda Civic', 12000, 'V002'),
(3, 3, 'LMN456', 'Ford Focus', 18000, 'V003'),
(4, 4, 'GHJ321', 'Chevrolet Malibu', 22000, 'V004'),
(5, 5, 'JKL654', 'Nissan Altima', 14000, 'V005');

-- Service_Center Insert (No V_id column)
INSERT INTO Service_Center (Center_id, Name, Location, Contact_no) VALUES
(1, 'AutoFix', 'Downtown', '111-222-3333'),
(2, 'CarCare', 'Uptown', '444-555-6666'),
(3, 'SpeedyService', 'Midtown', '777-888-9999'),
(4, 'DrivePro', 'Westside', '222-333-4444'),
(5, 'FixItFast', 'Eastside', '999-000-1111');

INSERT INTO Mechanic (Mec_id, Center_id, Name, Address, P_no, Specialization) VALUES
(1, 1, 'Mike Johnson', '789 Pine St', '555-111-2222', 'Engine Specialist'),
(2, 2, 'Sara Lee', '321 Maple St', '555-333-4444', 'Transmission Specialist'),
(3, 3, 'Tom Hardy', '555 Cedar St', '111-222-3333', 'Brake Specialist'),
(4, 4, 'Rachel Adams', '777 Spruce St', '444-555-6666', 'AC Specialist'),
(5, 5, 'Chris Evans', '888 Aspen St', '777-888-9999', 'Tire Specialist');

-- Service_Type Insert (No V_id column)
INSERT INTO Service_Type (Type_id, Oil_service, Water_wash, Estimated_cost, Description) VALUES
(1, TRUE, FALSE, 100.00, 'Oil change service'),
(2, FALSE, TRUE, 50.00, 'Water wash service'),
(3, TRUE, TRUE, 150.00, 'Full service including oil change and wash'),
(4, TRUE, FALSE, 110.00, 'Engine oil and filter replacement'),
(5, FALSE, TRUE, 55.00, 'Detailed water wash service');

INSERT INTO Service_Record (Record_id, V_id, Center_id, Type_id, Service_date, Cost) VALUES
(1, 1, 1, 1, '2025-09-29', 99.99),
(2, 2, 2, 2, '2025-09-20', 49.99),
(3, 3, 3, 3, '2025-10-01', 149.99),
(4, 4, 4, 4, '2025-10-05', 109.99),
(5, 5, 5, 5, '2025-10-07', 54.99);

INSERT INTO Maintenance_Schedule (Schedule_id, V_id, Schedule_date, Reminder_status) VALUES
(1, 1, '2025-10-01', TRUE),
(2, 2, '2025-10-05', FALSE),
(3, 3, '2025-10-15', TRUE),
(4, 4, '2025-10-20', FALSE),
(5, 5, '2025-10-25', TRUE);

-- Payment Insert (Record_id added, linking to Service_Record)
INSERT INTO Payment (Trans_id, Record_id, Mec_id, Amount, UPI, Credit_card, Timestamp, Status) VALUES
(1, 1, 1, 99.99, 'john@upi', NULL, '2025-09-29 10:00:00', 'Completed'),
(2, 2, 2, 49.99, NULL, '1234-5678-9012-3456', '2025-09-20 15:30:00', 'Pending'),
(3, 3, 3, 149.99, 'alice@upi', NULL, '2025-10-01 11:00:00', 'Completed'),
(4, 4, 4, 109.99, NULL, '2345-6789-0123-4567', '2025-10-05 14:00:00', 'Completed'),
(5, 5, 5, 54.99, 'emily@upi', NULL, '2025-10-07 16:30:00', 'Pending');

INSERT INTO Review (Review_id, Type_id, Ratings, Review_text) VALUES
(1, 1, 5, 'Excellent service!'),
(2, 2, 3, 'Good, but room for improvement.'),
(3, 3, 4, 'Good full service, minor delay.'),
(4, 4, 5, 'Quick and professional.'),
(5, 5, 2, 'Wash wasn’t thorough.');

INSERT INTO Service_Assignments (service_center_id, mechanic_id, record_id) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3),
(4, 4, 4),
(5, 5, 5);

-- ------------------------------------------------------
-- 4. FUNCTIONS, PROCEDURES, AND TRIGGERS (Corrected Logic)
-- ------------------------------------------------------

-- FUNCTION: Calculates total service cost for a vehicle
CREATE FUNCTION total_service_cost(vehicleId INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT IFNULL(SUM(Cost), 0) INTO total
    FROM Service_Record
    WHERE V_id = vehicleId;
    RETURN total;
END$$

-- FUNCTION: Calculates average rating for a service type
CREATE FUNCTION avg_service_rating(serviceTypeId INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avgRating DECIMAL(3,2);
    SELECT IFNULL(AVG(Ratings), 0) INTO avgRating
    FROM Review
    WHERE Type_id = serviceTypeId;
    RETURN avgRating;
END$$

-- PROCEDURE: Get Vehicle Service Details (Improved logic using the Service_Assignments table)
CREATE PROCEDURE GetVehicleServiceDetails(IN vehicleId INT)
BEGIN
    SELECT 
        O.Name AS Owner_Name, -- Added Owner Name
        V.V_no AS Vehicle_Number,
        SC.Name AS Service_Center,
        M.Name AS Mechanic_Name, -- Added Mechanic Name
        ST.Description AS Service_Type,
        SR.Service_date,
        SR.Cost
    FROM Service_Record SR
    JOIN Vehicle V ON SR.V_id = V.V_id
    JOIN Owner O ON V.Owner_id = O.Owner_id
    JOIN Service_Center SC ON SR.Center_id = SC.Center_id
    JOIN Service_Type ST ON SR.Type_id = ST.Type_id
    JOIN Service_Assignments SA ON SR.Record_id = SA.record_id 
    JOIN Mechanic M ON SA.mechanic_id = M.Mec_id
    WHERE V.V_id = vehicleId
    ORDER BY SR.Service_date DESC;
END$$

-- PROCEDURE: Get Mechanic Payments (Corrected logic using the new Payment schema)
CREATE PROCEDURE GetMechanicPayments(IN mechanicId INT)
BEGIN
    -- Input Validation
    IF NOT EXISTS (SELECT 1 FROM Mechanic WHERE Mec_id = mechanicId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Mechanic ID not found.';
    END IF;

    -- Result Set 1: Detailed Payment List with Service Context
    SELECT 
        M.Name AS Mechanic_Name,
        P.Trans_id,
        P.Amount,
        P.Status,
        P.Timestamp,
        SR.Record_id,
        ST.Description AS Service_Description, -- Context added
        V.V_no AS Vehicle_Number               -- Context added
    FROM Payment P
    JOIN Mechanic M ON P.Mec_id = M.Mec_id
    JOIN Service_Record SR ON P.Record_id = SR.Record_id -- CRITICAL JOIN
    JOIN Service_Type ST ON SR.Type_id = ST.Type_id
    JOIN Vehicle V ON SR.V_id = V.V_id
    WHERE P.Mec_id = mechanicId
    ORDER BY P.Timestamp DESC;

    -- Result Set 2: Summary of Total Amount Received
    SELECT 
        M.Name AS Mechanic_Name,
        SUM(P.Amount) AS Total_Amount_Received
    FROM Payment P
    JOIN Mechanic M ON P.Mec_id = M.Mec_id
    WHERE P.Mec_id = mechanicId
      AND P.Status = 'Completed'
    GROUP BY M.Name;
END$$

-- TRIGGER: Prevents negative mileage input
CREATE TRIGGER before_vehicle_insert
BEFORE INSERT ON Vehicle
FOR EACH ROW
BEGIN
    IF NEW.Milage < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Milage cannot be negative';
    END IF;
END$$

-- TRIGGER: Consolidated Payment Trigger (Combines validation and timestamp)
-- NOTE: The original trigger logic (IF NEW.Amount < 100 THEN SET NEW.Status = 'Completed';)
-- was removed as it is business logic, not data integrity, and is often flawed.
CREATE TRIGGER before_payment_insert
BEFORE INSERT ON Payment
FOR EACH ROW
BEGIN
    -- Data Validation: Amount must be positive
    IF NEW.Amount IS NULL OR NEW.Amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment amount must be greater than zero.';
    END IF;
    
    -- Ensure the timestamp is set upon insertion if not provided
    IF NEW.Timestamp IS NULL THEN
        SET NEW.Timestamp = NOW();
    END IF;
END$$

-- TRIGGER: Auto-sets reminder status based on schedule date
CREATE TRIGGER before_schedule_insert
BEFORE INSERT ON Maintenance_Schedule
FOR EACH ROW
BEGIN
    IF NEW.Schedule_date > CURDATE() THEN
        SET NEW.Reminder_status = TRUE;
    ELSE
        SET NEW.Reminder_status = FALSE;
    END IF;
END$$

-- Restore original delimiter
DELIMITER ;

-- ------------------------------------------------------
-- 5. TEST QUERIES
-- ------------------------------------------------------

SELECT total_service_cost(1) AS Total_Cost_V001;
SELECT avg_service_rating(3) AS Average_Rating_Type3;
CALL GetMechanicPayments(1);
CALL GetVehicleServiceDetails(3);

USE vehicle;
SHOW TABLES;
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mechanic_id INT NOT NULL,
    record_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_detail VARCHAR(100),
    status VARCHAR(20)
);
DESCRIBE payments;
USE vehicle;

USE vehicle;
SHOW TABLES;