# Photography Finder System

A desktop-based Photography Management System developed using Python, Tkinter, and MySQL. This application is designed to help manage photography clients, sessions, and available photography packages.

## Features

- User Registration and Login
- Password Recovery using Email OTP
- Add, View, Search, Update, and Delete Client Records
- Photography Package Management
- MySQL Database Integration

## Technologies Used

- Python
- Tkinter
- MySQL
- XAMPP
- MySQL Connector for Python

## Requirements

Before running the application, make sure you have:

- Python 3.x installed
- XAMPP installed
- MySQL Connector for Python

## Installation

1. Download or clone this repository.
2. Extract the downloaded files.
3. Open Command Prompt in the project folder.
4. Install the required dependency:

   ```bash
   py -m pip install -r requirements.txt
   ```

5. Open XAMPP Control Panel.
6. Start MySQL.
7. Configure the database credentials in the Python source code if necessary.
8. Run the application:

   ```bash
   py photography_finder.py
   ```

## Database

The application uses MySQL for storing user accounts, photography packages, and client records.

The database is initialized by the application during startup, if supported by the configured MySQL account.

## Project Type

Student-developed desktop application.

## License

See the LICENSE file for the terms