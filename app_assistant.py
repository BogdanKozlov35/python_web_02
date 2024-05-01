from abc import ABC, abstractmethod
from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import pickle
import sys

class Messanger(ABC):

    @abstractmethod
    def send_message(self, message) -> None:
        pass

class TerminalMessanger(Messanger):
    def send_message(self, message) -> None:
        print(message)

class WebMessanger(Messanger):
    def send_message(self, message) -> None:
        print(f"we dont have web interface yet")


class Field(ABC):

    def __init__(self, value):
        self.value = value

    @abstractmethod
    def __str__(self):
        pass

class Name(Field):
    def __str__(self):
        return str(self.value)

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number")

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, '%d.%m.%Y').date()
            if date > datetime.now().date():
                raise ValueError("Invalid date. Birthday cannot be in the future.")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")

    def __str__(self):
        return str(self.value)

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper

class RecordInterface(ABC):

    @abstractmethod
    def add_phone(self, phone_number):
        pass

    @abstractmethod
    def add_birthday(self, birthday):
        pass

    @abstractmethod
    def find_phone(self, phone_number):
        pass

    @abstractmethod
    def remove_phone(self, phone_number):
        pass

    @abstractmethod
    def __str__(self):
        pass

class Record(RecordInterface):

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        else:
            return None

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if str(phone) != phone_number]

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record
    @input_error
    def find(self, name):
        return self.data.get(name)
    @input_error
    def delete(self, name):
        del self.data[name]

    @input_error
    def birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value
                birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() >= 5:
                        delta = (7 - birthday_this_year.weekday())
                        birthday_this_year += timedelta(days=delta)

                    congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')
                    upcoming_birthdays.append({"name": name, "congratulation_date": congratulation_date_str})

        return f" birthdays nearest 7 days: {upcoming_birthdays}"

@input_error
def add_contact(args):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def add_birthday(args):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."
@input_error
def show_birthday(args):
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name}: {record.birthday.value}"
        else:
            return f"No birthday set for {name}."
    else:
        return f"Contact '{name}' not found."
@input_error
def all_contact():
    lines = []
    for name, record in book.data.items():
        phones = '; '.join(str(phone) for phone in record.phones)
        if record.birthday:
            birthday = record.birthday.value
        else:
            birthday = ""
        lines.append(f"| {name:<20} | {phones:<50} | {birthday:<20} |")
    header = "| {:<20} | {:<50} | {:<20} |".format("Name", "Phones", "Birthday")
    separator = "-" * len(header)
    return "\n".join([separator, header, separator] + lines + [separator])
@input_error
def edit_phone(args):
    name, phone_number, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found")
    phone = record.find_phone(phone_number)
    if phone:
        record.remove_phone(phone_number)
        record.add_phone(new_phone)
        return "Phone number updated."
    else:
        return "Phone number not found for this contact."

def phone_username(args):
    name, *_ = args
    record = book.find(name)
    if record:
        phones = ' ;'.join(str(phone) for phone in record.phones)
        return phones
    else:
        return "Contact not found."

# def save_data(book, filename="addressbook.pkl"):
#     with open(filename, "wb") as f:
#         pickle.dump(book, f)
#
# def load_data(filename="addressbook.pkl"):
#     try:
#         with open(filename, "rb") as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         return AddressBook()
class Saver(ABC): # you can add json for instance
    @abstractmethod
    def save_data(self):
        pass

class SaveDataPkl(Saver):
    def __init__(self, filename="addressbook.pkl"):
        self.filename = filename

    def save_data(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.book, f)
class Loader(ABC): # you can add json for instance
    @abstractmethod
    def load_data(self):
        pass
class LoadDataPkl(Loader):
    def __init__(self, filename="addressbook.pkl"):
        self.filename = filename

    def load_data(self):
        try:
            with open(self.filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook

# Створення нової адресної книги
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


# if __name__ == "__main__":
def main():

    available_command = """Available commands:
       - add <name> <phone>: Add a new contact with the given name and phone number.
       - change <name> <old_phone> <new_phone>: Change the phone number for the contact with the given name.
       - phone <name>: Get the phone numbers for the contact with the given name.
       - all: Show all contacts.
       - add-birthday <name> <birthday>: Add a birthday for the contact with the given name.
       - show-birthday <name>: Show the birthday for the contact with the given name.
       - birthdays: Show upcoming birthdays.
       - close/exit: Close the application.
       - command: Show available commands.
    """

    print(f"Welcome to the assistant bot!\n {available_command}")
    user_interface = input("""
    Choose your interface:"
    1 = Terminal
    2 = Web
    >>> """)

    if user_interface == "1":
        messager = TerminalMessanger()

    elif user_interface == "2":

        print(f"we dont have web interface yet")
        messager = WebMessanger()
        main()

    else:
        messager = None
        print("unknown user interface")
        main()

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            saver = SaveDataPkl()
            saver.book = book
            saver.save_data()
            print("Good bye!")
            break
        elif command == "hello":
            messager.send_message("How can I help you?")
        elif command == "command":
            messager.send_message(f"Welcome to the assistant bot!\n {available_command}")
        elif command == "add":
            messager.send_message(add_contact(args))
        elif command == "change":
            name, phone_number, new_phone, *_ = args
            messager.send_message(edit_phone(args))
        elif command == "phone":
            # user phone number
            name, *_ = args
            messager.send_message(phone_username(name))
        elif command == "all":
            messager.send_message(all_contact())
        elif command == "add-birthday":
            messager.send_message(add_birthday(args))
        elif command == "show-birthday":
            messager.send_message(show_birthday(args))
        elif command == "birthdays":
            messager.send_message(book.birthdays())
        else:
            messager.send_message("Invalid command.")

if __name__ == "__main__":

    loader = LoadDataPkl()
    book = loader.load_data()

    main()