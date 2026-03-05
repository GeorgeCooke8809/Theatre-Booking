CREATE TABLE dbo.Users (userID INT NOT NULL, fName VARCHAR(30) NOT NULL, lName VARCHAR(30) NOT NULL, email VARCHAR(100) NOT NULL, password VARCHAR(50) NOT NULL, phone VARCHAR(16) NOT NULL, userType VARCHAR(7) NOT NULL);

CREATE TABLE dbo.Bookings (bookingID INT NOT NULL, showingID INT NOT NULL, userID INT NOT NULL);

CREATE TABLE dbo.BookingSeats(bookingSeatID INT NOT NULL, bookingID INT NOT NULL, seatID VARCHAR(3) NOT NULL, bookingType VARCHAR(7) NOT NULL);

CREATE TABLE dbo.Performances(performanceID INT NOT NULL, title VARCHAR(100) NOT NULL, performanceDescription VARCHAR(MAX) NOT NULL, childPrice DECIMAL(2) NOT NULL, adultPrice DECIMAL(2) NOT NULL, elderlyPrice DECIMAL(2) NOT NULL);

CREATE TABLE dbo.PerformanceUnavailableSeats(PerformanceUnavailableSeatID INT NOT NULL, performanceID INT NOT NULL, seatID INT NOT NULL);

CREATE TABLE dbo.Seats(seatID VARCHAR(3) NOT NULL);

CREATE TABLE dbo.Showings(showingID INT NOT NULL, performanceID INT NOT NULL, showingDate DATE NOT NULL);