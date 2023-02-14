import json

# Constants
DAYS = [['monday', 'mon'], ['tuesday', 'tue'], ['wednesday', 'wed'], ['thursday', 'thu'], ['friday', 'fri']]
simpleDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


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


def addUser(weekNum, id, name):
    with open('users.json', 'r') as f:
        users = json.load(f)
    users[name] = {"weeknum": weekNum, "employeeID": id, "name": name, "days": {}}
    with open('users.json', 'w') as f:
        json.dump(users, f, sort_keys=True, indent=4)


def removeUser(name):
    with open('users.json', 'r') as f:
        users = json.load(f)
    users.pop(name)
    with open('users.json', 'w') as f:
        json.dump(users, f, sort_keys=True, indent=4)


def flush():
    with open('users.json', 'w') as f:
        json.dump({}, f, sort_keys=True, indent=4)


def listUsers():
    with open('users.json', 'r') as f:
        users = json.load(f)
    # If list is empty print a message and return
    if not users:
        print('No users in database')
        return
    for user in users:
        print(user, ':', users[user])


def setHoursPerDay(name, hours, day):
    if not checkDay(day, simpleDays):  # Check if the day is valid
        raise InvalidDay(day)
    if hours > 24:  # Check if the number of hours is valid
        raise TooManyHours(hours=hours)
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)

        users[name]["days"][day] = hours
        with open('users.json', 'w') as f:
            json.dump(users, f, sort_keys=True, indent=4)
    except KeyError:
        raise UserDoesNotExist(name)


def checkHours(name):
    # Checks if a value has been passed before continuing
    if (name is None and id is None) or (name == "" and id == ""):
        raise MissingParamaters

    tooManyHours = []
    tooFewHours = []

    with open('users.json', 'r') as f:
        database = json.load(f)
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
        database = json.load(f)
    totalHours = 0
    for day in database[name]["days"]:
        totalHours += database[name]["days"][day]
    return totalHours


def makeHoursDict():
    # This function creates a dictionary of the total hours for each user
    with open('users.json', 'r') as f:
        database = json.load(f)
    hoursDict = {}
    for user in database:
        hoursDict[user] = addAllHours(user)
    return hoursDict


def makeThresholdList():
    # This function creates a list of users who have worked more than 40 hours, less than 30 hours,
    # or between 37 and 39 hours
    with open('users.json', 'r') as f:
        database = json.load(f)
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
        database = json.load(f)
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


if __name__ == '__main__':
    # Check if the file exists
    try:
        with open('users.json', 'r') as f:
            pass
    # If the file does not exist create it
    except FileNotFoundError:
        with open('users.json', 'w') as f:
            json.dump({}, f, sort_keys=True, indent=4)

    # Handle user commands
    while True:
        try:
            command = input('Enter a command: ').split()
            command[0] = command[0].lower()
            if command[0] == 'adduser':
                week = input("Enter the week number: ")
                employeeId = input("Enter the employee ID: ")
                # Test
                name = input("Enter employee name: ")
                addUser(weekNum=week, id=employeeId, name=name)
                for day in simpleDays:
                    try:
                        hours = input(f"Enter hours for {day}: ")
                        setHoursPerDay(name, int(hours), day)
                    # Handle TooManyHours
                    except TooManyHours as e:
                        print("Too Many Hours")
                    except ValueError as e:
                        print("Empty or invalid input")

                checkHours(name)

            elif command[0] == 'removeuser':
                removeUser(command[1])

            elif command[0] == 'hours':
                print(makeHoursDict())
            elif command[0] == 'addallhours':
                print(addAllHours(command[1]))
            elif command[0] == 'flush':
                flush()
            elif command[0] == 'listusers':
                listUsers()
            elif command[0] == "fancy":
                makeFancyDisplay()
            elif command[0] == 'dayhours':
                try:
                    setHoursPerDay(command[1], int(command[2]), command[3])
                except UserDoesNotExist:
                    print('User does not exist')
                except InvalidDay as error:
                    print(f'Invalid day entered ({error.day})')
                except TooManyHours as error:
                    print(f'Hours worked ({error.hours}) exceeds 24')
            elif command[0] == "checkhours":
                checkHours(input("Name? "))
            elif command[0] == 'exit':
                break
            elif command[0] == 'help':
                # List of commands and their descriptions
                print('addUser NAME [hours=HOURS] - Add a user with the name NAME and the number of hours HOURS')
                print('removeUser NAME - Remove the user with the name NAME')
                print('flush - Remove all users from the database')
                print('listUsers - List all users in the database')
                print('dayHours NAME HOURS DAY - Set the number of hours HOURS for the user NAME on the day DAY')
                print('exit - Exit the program')
            else:
                raise InvalidCommand(command)
        except InvalidCommand as e:
            print('Invalid command:', e.command)
