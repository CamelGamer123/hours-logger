from json import load, dump
import tkinter as tk
from tkinter import ttk

# Constants
DAYS = [['monday', 'mon'], ['tuesday', 'tue'], ['wednesday', 'wed'], ['thursday', 'thu'], ['friday', 'fri']]
simpleDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
path = "users.json"
hoursEntryTableTemplate = [
    ('Monday', ' '),
    ('Tuesday', ' '),
    ('Wednesday', ' '),
    ('Thursday', ' '),
    ('Friday', ' '),
]


class InvalidCommand(Exception):
    def __init__(self, command=None):
        self.command = command


class InvalidDay(Exception):
    def __init__(self, day=None):
        self.day = day


class DatabaseError(Exception):
    def __init__(self, message=None):
        self.message = message


class UserDoesNotExist(DatabaseError):
    def __init__(self, message=None):
        self.message = message


class TooManyHours(DatabaseError):
    def __init__(self, message=None, hours="Default"):
        self.hours = hours
        self.message = message

        # Check if hours is the default value
        if hours == "Default":
            self.message = "Too many hours"


class MissingID(DatabaseError):
    def __init__(self, message=None):
        self.message = message


class MissingParamaters(Exception):
    def __init__(self, message=None):
        self.message = message


def checkDay(day, days):
    for dayList in days:
        if day in dayList:
            return True
    return False


def addUser(id, name, weekNum):
    with open('users.json', 'r') as f:
        users = load(f)
    users[f"{name}#{id}"] = {"weekNum": weekNum, "employeeID": id, "name": name, "days": {}}
    with open('users.json', 'w') as f:
        dump(users, f, sort_keys=True, indent=4)


def removeUser(name, id):
    with open('users.json', 'r') as f:
        users = load(f)
    users.pop(f"{name}#{id}")
    with open('users.json', 'w') as f:
        dump(users, f, sort_keys=True, indent=4)


def flush():
    with open('users.json', 'w') as f:
        dump({}, f, sort_keys=True, indent=4)


def listUsers():
    with open('users.json', 'r') as f:
        users = load(f)
    # If list is empty print a message and return
    if not users:
        print('No users in database')
        return
    for user in users:
        print(user, ':', users[user])


def setHoursPerDay(name, id, hours, day):
    print(f"Setting hours for {name}#{id} on {day} to {hours}")
    if not checkDay(day, simpleDays):  # Check if the day is valid
        raise InvalidDay(day)
    if hours > 24:  # Check if the number of hours is valid
        raise TooManyHours(hours=hours)
    try:
        with open('users.json', 'r') as f:
            users = load(f)

        users[f"{name}#{id}"]["days"][day] = hours
        with open('users.json', 'w') as f:
            dump(users, f, sort_keys=True, indent=4)
    except KeyError:
        raise UserDoesNotExist(name)


def checkHours(name):
    # Checks if a value has been passed before continuing
    if (name is None and id is None) or (name == "" and id == ""):
        raise MissingParamaters

    tooManyHours = []
    tooFewHours = []

    with open('users.json', 'r') as f:
        database = load(f)
        for day in database[name]["days"]:
            if database[name]["days"][day] <= 4:
                tooFewHours.append(day)
            elif database[name]["days"][day] >= 10:
                tooManyHours.append(day)

    if tooManyHours is not []:
        print(f"Too many hours worked on {''.join(str(tooManyHours) for tooManyHours in tooManyHours)}")
    if tooFewHours is not []:
        print(f"Insufficient hours worked on {''.join(str(tooFewHours) for tooFewHours in tooFewHours)}")


def addAllHours(name):
    # Create a function that adds all the hours for a user
    with open('users.json', 'r') as f:
        database = load(f)
    totalHours = 0
    for day in database[name]["days"]:
        totalHours += database[name]["days"][day]
    return totalHours


def makeHoursDict():
    # This function creates a dictionary of the total hours for each user
    with open('users.json', 'r') as f:
        database = load(f)
    hoursDict = {}
    for user in database:
        hoursDict[user] = addAllHours(user)
    return hoursDict


def makeThresholdList():
    # This function creates a list of users who have worked more than 40 hours, less than 30 hours,
    # or between 37 and 39 hours
    with open('users.json', 'r') as f:
        database = load(f)
    maxList = []
    minList = []
    otherList = []
    for user in database:
        if addAllHours(user) > 40:
            maxList.append(user)
        elif addAllHours(user) < 30:
            minList.append(user)
        elif 37 <= addAllHours(user) <= 39:
            otherList.append(user)
    return maxList, minList, otherList


def makeFancyDisplay():
    # This function makes a fancy display of each user's entry
    with open('users.json', 'r') as f:
        database = load(f)
    for user in database:
        print(f"Name: {database[user]['name']}\n"
              f"Week Number: {database[user]['weeknum']}\n"
              f"Employee ID: {database[user]['employeeID']}\n"
              f"Days:")
        for day in database[user]['days']:
            _ = f"    {day}: {database[user]['days'][day]}"
            print(_)
        print(f"{'*' * (len(_) + 10)}\n"
              f"Total hours worked: {addAllHours(user)}\n")
        checkHours(user)
        print(f"Total hours worked: {addAllHours(user)}\n")


class UserInterface:
    def __init__(self):
        # Creates the main GUI window
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.geometry("300x300")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        # Adds the main menu window to the list of windows
        self.windows = [self.root]

        # Creates all UI elements

        ttk.Label(self.root, text="Please select an option below:").grid(column=0, row=1, columnspan=3, padx=10,
                                                                         pady=10)
        ttk.Button(self.root, text="Add User", command=self.createAddUserWindow).grid(column=0, row=3, padx=10,
                                                                                      pady=10)
        ttk.Button(self.root, text="Remove User", command=self.createRemoveUserWindow).grid(column=1, row=3,
                                                                                            padx=10, pady=10)
        ttk.Button(self.root, text="Set Hours", command=self.createSetHoursWindow).grid(column=2, row=3,
                                                                                        padx=10, pady=10)
        ttk.Button(self.root, text="Produce Report", command=self.produceReport).grid(column=1, row=4, padx=10,
                                                                                      pady=10)
        ttk.Button(self.root, text="Clear Database", command=self.confirmFlush).grid(column=1, row=5, padx=10, pady=10)
        # Creates future windows
        self.addUserWindow = None
        self.removeUserWindow = None
        self.setHoursWindow = None
        self.confirmWindow = None

        # Runs the main menu
        self.root.mainloop()

    def confirmFlush(self):
        # Creates a confirmation window for the flush database function
        self.confirmWindow = tk.Tk()
        self.confirmWindow.title("Confirm")
        self.confirmWindow.geometry("300x300")
        self.confirmWindow.resizable(False, False)
        self.confirmWindow.configure(bg="white")

        # Adds the confirmation window to the list of windows
        self.windows.append(self.confirmWindow)

        ttk.Label(
            self.confirmWindow,
            text="Are you sure you want to clear the database?"
        ).grid(column=0, row=1, columnspan=3, padx=10, pady=10)

        ttk.Button(self.confirmWindow, text="Yes", command=self.flushAll).grid(column=0, row=3, padx=10, pady=10)
        ttk.Button(self.confirmWindow, text="No", command=self.confirmWindow.destroy).grid(column=1, row=3, padx=10,
                                                                                           pady=10)

    def flushAll(self):
        flush()
        self.windows.remove(self.confirmWindow)
        self.confirmWindow.destroy()

    def createAddUserWindow(self):
        # Creates the add user window
        self.addUserWindow = tk.Tk()
        self.addUserWindow.title("Add User")
        self.addUserWindow.geometry("300x600")
        self.addUserWindow.resizable(False, False)
        self.addUserWindow.configure(bg="white")

        # Adds the add user window to the list of windows
        self.windows.append(self.addUserWindow)

        self.employeeId = tk.StringVar(self.addUserWindow)
        self.name = tk.StringVar(self.addUserWindow)
        self.weekNum = tk.StringVar(self.addUserWindow)
        self.mondayHours = tk.StringVar(self.addUserWindow)
        self.tuesdayHours = tk.StringVar(self.addUserWindow)
        self.wednesdayHours = tk.StringVar(self.addUserWindow)
        self.thursdayHours = tk.StringVar(self.addUserWindow)
        self.fridayHours = tk.StringVar(self.addUserWindow)

        # Adds all buttons and text boxes and labels
        ttk.Label(self.addUserWindow, text="Employee ID").grid(column=0, row=0, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.employeeId).grid(column=1, row=0, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Name").grid(column=0, row=1, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.name).grid(column=1, row=1, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Week Number").grid(column=0, row=2, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.weekNum).grid(column=1, row=2, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Monday").grid(column=0, row=3, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.mondayHours).grid(column=1, row=3, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Tuesday").grid(column=0, row=4, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.tuesdayHours).grid(column=1, row=4, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Wednesday").grid(column=0, row=5, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.wednesdayHours).grid(column=1, row=5, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Thursday").grid(column=0, row=6, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.thursdayHours).grid(column=1, row=6, padx=10, pady=10)

        ttk.Label(self.addUserWindow, text="Friday").grid(column=0, row=7, padx=10, pady=10)
        ttk.Entry(self.addUserWindow, textvariable=self.fridayHours).grid(column=1, row=7, padx=10, pady=10)

        ttk.Button(self.addUserWindow, text="Confirm", command=self.addUserButtonCommand).grid(column=0, row=8, padx=10,
                                                                                               pady=10)

        # Runs the add user window
        self.addUserWindow.mainloop()

    def addUserButtonCommand(self):
        weekNum = self.weekNum.get()
        employeeId = self.employeeId.get()
        name = self.name.get()
        mondayHours = self.mondayHours.get()
        tuesdayHours = self.tuesdayHours.get()
        wednesdayHours = self.wednesdayHours.get()
        thursdayHours = self.thursdayHours.get()
        fridayHours = self.fridayHours.get()

        addUser(id=employeeId, name=name, weekNum=weekNum)
        setHoursPerDay(name=name, id=employeeId, day="Monday", hours=int(mondayHours))
        setHoursPerDay(name=name, id=employeeId, day="Tuesday", hours=int(tuesdayHours))
        setHoursPerDay(name=name, id=employeeId, day="Wednesday", hours=int(wednesdayHours))
        setHoursPerDay(name=name, id=employeeId, day="Thursday", hours=int(thursdayHours))
        setHoursPerDay(name=name, id=employeeId, day="Friday", hours=int(fridayHours))

        self.weekNum.set("")
        self.employeeId.set("")
        self.name.set("")
        self.mondayHours.set("")
        self.tuesdayHours.set("")
        self.wednesdayHours.set("")
        self.thursdayHours.set("")
        self.fridayHours.set("")

    def createRemoveUserWindow(self):
        # Creates the remove user window
        self.removeUserWindow = tk.Tk()
        self.removeUserWindow.title("Remove User")
        self.removeUserWindow.geometry("300x300")
        self.removeUserWindow.resizable(False, False)
        self.removeUserWindow.configure(bg="white")

        # Adds the remove user window to the list of windows
        self.windows.append(self.removeUserWindow)

        # Adds all buttons and text boxes and labels

        # Runs the remove user window
        self.removeUserWindow.mainloop()

    def createSetHoursWindow(self):
        # Creates the set hours window
        self.setHoursWindow = tk.Tk()
        self.setHoursWindow.title("Set Hours")
        self.setHoursWindow.geometry("300x300")
        self.setHoursWindow.resizable(False, False)
        self.setHoursWindow.configure(bg="white")

        # Adds the set hours window to the list of windows
        self.windows.append(self.setHoursWindow)

        # Adds all buttons and text boxes and labels

        # Runs the set hours window
        self.setHoursWindow.mainloop()

    def produceReport(self):
        # This function should produce a report of all the users and their hours the same way that createFancyDisplay
        # does and write it to a text file called report.txt in the same directory as the program. It should also
        # open a notepad window with the report in it.
        pass

    def close(self):
        for window in self.windows:
            window.destroy()
        exit(0)


if __name__ == '__main__':
    # Check if the file exists
    try:
        with open('users.json', 'r') as f:
            pass
    # If the file does not exist create it
    except FileNotFoundError:
        with open('users.json', 'w') as f:
            dump({}, f, sort_keys=True, indent=4)

    gui = UserInterface()
