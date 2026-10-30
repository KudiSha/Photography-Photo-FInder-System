# 📸 Photography Finder System

A desktop-based Photography Finder and Record Management System developed using **Python, Tkinter, and MySQL**.

The system provides a simple interface for managing photography-related records, searching for existing entries, and maintaining stored information through basic record management operations.

---

## 📌 About the Project

The **Photography Finder System** is a desktop application designed to simplify the process of managing and finding photography records.

Instead of manually browsing through records, users can interact with the application through a graphical user interface (GUI). The system connects to a MySQL database to store and retrieve information.

This project was developed as an academic programming project to demonstrate the practical application of Python GUI development, database connectivity, and CRUD operations.

## ✨ Features

- **Dashboard** – Provides the main navigation interface of the application.
- **Record Management** – Allows users to manage photography-related records.
- **Find Records** – Search for records using a Record ID or client name.
- **Update Records** – Modify information from existing records.
- **Delete Records** – Remove selected records from the database.
- **MySQL Database Integration** – Stores and retrieves application data using MySQL.
- **Email OTP Interface** – Includes a password verification workflow. Email delivery requires SMTP configuration.
- **Sample Data Initialization** – The application automatically initializes its database and sample photography packages when needed.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Tkinter | Graphical User Interface |
| MySQL | Database management |
| MySQL Connector/Python | Python-to-MySQL connection |
| XAMPP | Local MySQL database server |
| PyInstaller | Application packaging |

## 📂 Project Structure

```text
Photography-Finder-System/
│
├── photography_finder.py
│
├── PhotographyFinder.spec
│
├── requirements.txt
│
├── README.md
│
├── build/
│
└── dist/
    └── PhotographyFinder/
        ├── PhotographyFinder.exe
        └── _internal/
```

**Note:** The `build/` and `dist/` directories are generated during the PyInstaller build process. They may not be included in the source repository.

## ⚙️ System Requirements

Before running the project from source, make sure you have:

- Windows operating system
- Python 3.x
- MySQL Server
- XAMPP (MySQL component)
- pip package manager

**Important:** Apache is not required because the application uses MySQL directly.

## 🚀 Installation and Setup

### 1. Clone the Repository

Open your terminal or Command Prompt and run:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd Photography-Finder-System
```

### 2. Install Dependencies

Install the required Python package:

```bash
py -m pip install mysql-connector-python==8.4.0
```

### 3. Start MySQL

1. Open XAMPP Control Panel.
2. Start the **MySQL** service.
3. Make sure MySQL is running before launching the application.

Apache does not need to be started.

### 4. Run the Application

Execute the Python source file:

```bash
py photography_finder.py
```

The application will initialize its database and required tables when launched.

## 🗄️ Database Configuration

The application currently uses the following default database configuration:

```python
DB_CFG = dict(
    host="localhost",
    port=3306,
    user="root",
    password=""
)

DB_NAME = "photography_finder"
```

Make sure your MySQL configuration matches these settings.

If your MySQL installation uses a different username, password, or port, update the database configuration in the source code.

**Security Reminder:** Do not use an empty database password or hardcoded credentials in a production deployment. Use environment variables or a secure configuration method instead.

## 📧 Email OTP Configuration

The application includes an email OTP workflow.

To enable actual email delivery, configure the SMTP settings in the source code:

```python
SMTP_EMAIL = ""
SMTP_APP_PASSWORD = ""
```

The application currently uses a demo OTP popup when SMTP credentials are not configured.

For actual email delivery, configure a supported SMTP account and use an appropriate app password. Never upload your email password or app password to GitHub.

## 📦 Building the Executable

The project can be packaged into a standalone Windows application using PyInstaller.

Install PyInstaller:

```bash
py -m pip install pyinstaller
```

Build the application:

```bash
py -m PyInstaller --clean --noconfirm --onedir --windowed --name PhotographyFinder photography_finder.py
```

After the build completes, the executable will be located at:

```text
dist/PhotographyFinder/PhotographyFinder.exe
```

**Important:** Distribute the entire `PhotographyFinder` folder, not just the `.exe` file. The application also requires its supporting files.

The target computer must also have a compatible MySQL Server available.

## 🧪 Testing

Before distributing a new version, check the following:

- [ ] Application launches successfully.
- [ ] Dashboard displays correctly.
- [ ] Database connection works.
- [ ] Records can be searched.
- [ ] Existing records can be updated.
- [ ] Selected records can be deleted.
- [ ] Navigation buttons work correctly.
- [ ] Email OTP workflow behaves as expected.
- [ ] Packaged executable launches successfully.

## 🔧 Troubleshooting

**1. MySQL Connection Error**

- Check if MySQL is running in XAMPP.
- Verify the host, port, username, and password.
- Make sure the configured MySQL port is correct.

**2. Missing Python Module**

Install the required dependency:

```bash
py -m pip install mysql-connector-python==8.4.0
```

**3. Application Does Not Launch**

- Check whether Python is installed correctly.
- Run the source file through Command Prompt to see error messages.
- Verify that all required dependencies are installed.

**4. Email OTP Is Not Sending**

- Verify the SMTP configuration.
- Check the email account's SMTP settings.
- Make sure the required app password is configured.

## 🔄 Version History

| Version | Description |
|---|---|
| v1.0.0 | Initial application release |
| v1.0.1 | Fixed navigation issue involving the Back button in Update Record and Delete Record. |

## 🎯 Project Objectives

The project aims to:

1. Develop a functional desktop application using Python.
2. Implement database connectivity using MySQL.
3. Apply basic Create, Read, Update, and Delete (CRUD) operations.
4. Practice GUI development using Tkinter.
5. Improve understanding of software organization, debugging, and application deployment.

## 👨‍💻 Developer

**Developed by:** Kurt Soriano

**Project:** Photography Finder System

**Category:** Desktop Application / Database Management System

**Purpose:** Academic Programming Project

---

## 📄 License

This project was developed for educational and academic purposes.

You may study the source code and use it as a reference for learning. Please provide appropriate credit when referencing or reusing the project.

---

⭐ If you find this project useful, feel free to explore the source code and learn from its implementation.
