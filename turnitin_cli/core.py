import configparser
from getpass import getpass
import json
from pathlib import Path
import requests

parser = configparser.ConfigParser()
parser.read(Path.home() / "tiiconfig.ini")

url = "https://turnitin-api.herokuapp.com"

USERNAME = parser["login"]["username"]
PASSWORD = parser["login"]["password"]

if USERNAME == "example@example.com":
    parser["login"]["username"] = input("What is your username? ")
    parser["login"]["password"] = getpass("What is your password (input hidden for security?\n")
    print("The configuration file is at", Path.home() / "tiiconfig.ini")
    print("Default keybindings:")
    for v in ("menu_up", "menu_down", "quit"):
        print(f"{v:10} {parser['keybindings'][v]}")
    input("Enter to continue\n")
    with open(Path.home() / "tiiconfig.ini", 'w') as fout:
        parser.write(fout)

USERNAME = parser["login"]["username"]
PASSWORD = parser["login"]["password"]

s = requests.Session()

def login():
    login_result = s.post(url + "/login", json={
        "email": USERNAME,
        "password": PASSWORD
    })
    auth = login_result.json()
    return auth

def get_courses(auth):
    courses_result = s.post(url + "/courses", json=auth)
    courses = courses_result.json()
    return courses

def get_assignments(auth, course):
    first_course_data = dict(**auth, course=course)
    assignments_result = s.post(url + "/assignments", json=first_course_data)
    assignments = assignments_result.json()
    return assignments

def download(auth, assignment, filename):
    download_query = dict(**auth, assignment=assignment, pdf=True)
    r = s.post(url + '/download', json=download_query)
    with open(filename, 'wb+') as fout:
        fout.write(r.content)

def submit(auth, assignment, filename, title):
    # Example case - submit to the fourth assignment 
    with open(filename, 'rb') as uf:
        # We must convert the json to a string to submit in a form
        submit_query = dict(
            auth=json.dumps(auth["auth"]),
            assignment=json.dumps(assignment),
            title=title,
            filename=filename
        )
        r = s.post(url + "/submit", data=submit_query, files={"userfile": uf})
    return r.json()

