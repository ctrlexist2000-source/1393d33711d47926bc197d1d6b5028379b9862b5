MERCH SPLITTER

A simple Streamlit application for splitting a large XLSX file into smaller files
and downloading them as a ZIP archive.

--------------------------------------------------

WHAT THE APP DOES

The application accepts an .xlsx file containing two columns:

product
quantity

The file can contain up to 10,000 rows.

After uploading the file, the user can split the data using two modes.

1. MAX 100 ROWS PER FILE

This mode splits the file into equal sized chunks with a maximum of 100 rows
per output file.

Example:
1000 rows -> 10 files


2. MAX QUANTITY SUM PER FILE

This mode creates files so that the total sum of the "quantity" column
inside each file does not exceed a specified limit.

Example input:

product   quantity
A         40
B         30
C         50

If the limit is 100:

File 1 -> quantity sum = 70
File 2 -> quantity sum = 50


--------------------------------------------------

FILE NAMING

If the uploaded file follows this naming pattern:

test 100.01.xlsx

The numbering will continue automatically:

test 100.01.xlsx
test 100.02.xlsx
test 100.03.xlsx
...

All generated files are packaged into a single ZIP archive
that can be downloaded from the application.


--------------------------------------------------

REQUIREMENTS

Python 3.9 or newer.

Required Python packages:

streamlit
pandas
openpyxl

All dependencies are listed in the file:

requirements.txt


--------------------------------------------------

RUNNING THE APP LOCALLY

1. Install dependencies:

pip install -r requirements.txt


2. Start the application:

streamlit run streamlit_app.py


After running the command, Streamlit will open the application
in your default web browser.


--------------------------------------------------

DEPLOYMENT FOR A TEAM (EASIEST OPTION)

The fastest way to share the app with a team is using
Streamlit Community Cloud.

Steps:

1. Push the repository to GitHub.
2. Open https://share.streamlit.io
3. Connect your GitHub repository.
4. Select the main file:

streamlit_app.py

5. Click Deploy.
6. Share the generated link with your team.


--------------------------------------------------

ALTERNATIVE DEPLOYMENT

The application can also be deployed internally using:

Docker
a virtual machine
a reverse proxy such as Nginx or Traefik

Since the project is a single Streamlit app,
deployment is straightforward.