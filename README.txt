Required Libraries:
- flask,
- logging,
- datetime,
- reportlab,
- pyodbc,

Run and tested in Python 3.14 with ODBC Driver 18 for SQL Server (also tested with version 17 to a lesser extent)

Common Issues:
I found that on ODBC version 17 it would often struggle with dates. This version represents dates as strings where version 18 represents them as datetime objects. I have made efforts to fix this and have tested (somewhat) but note anyway.

Admin Login:
Username: ADMIN
Password: AdminPassword123

Alternatively, bypass by going to 127.0.0.1:500/admin-dashboard

File To Run:
main.py