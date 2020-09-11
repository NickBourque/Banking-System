# Write your code here
import random
import sqlite3


global log_out
global conn
global cur


def initialize_db():
    global conn
    global cur
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("DROP TABLE card")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS card ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "number TEXT,"
                "pin TEXT,"
                "balance INTEGER DEFAULT 0"
                ");")
    conn.commit()


def prompt_for_input():
    print("\n1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    return input()


def second_prompt():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')
    return input()


def is_card_valid(card_number):
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return (sum % 10) == 0


def create_account():
    random.seed()
    card_valid = False
    while not card_valid:
        card_num = '400000' + str(random.randint(0, 9999999999)).zfill(10)
        card_valid = is_card_valid(card_num)
    pin = str(random.randint(0, 9999)).zfill(4)
    cur.execute("INSERT INTO card (number, pin)"
                "VALUES (" + card_num + ", " + pin + ");")
    conn.commit()

    print('\nYour card has been created')
    print('Your card number:')
    print(card_num)
    print('Your card PIN:')
    print(pin)


def check_balance(card_num):
    bal = cur.execute("SELECT balance FROM card WHERE number = " + card_num + " LIMIT 1;").fetchone()[0]
    print('Balance:' + bal)


def add_income(card_num):
    print('Enter income:')
    bal = cur.execute("SELECT balance FROM card WHERE number = " + card_num + " LIMIT 1;").fetchone()[0]
    income = input()
    bal = bal + int(income)
    cur.execute("UPDATE card SET balance = " + str(bal) + " WHERE number = " + card_num + ";")
    conn.commit()


def do_transfer(card_num):
    print('Transfer')
    print('Enter card number:')
    bal = cur.execute("SELECT balance FROM card WHERE number = " + card_num + " LIMIT 1;").fetchone()[0]
    transfer_to = input()
    transfer_to_exists = len(cur.execute("SELECT * FROM card WHERE number = " + transfer_to + ";").fetchall()) > 0

    if transfer_to == card_num:
        print('You can''t transfer money to the same account!')
    elif not is_card_valid(transfer_to):
        print('Probably you made a mistake in the card number. Please try again!')
    elif not transfer_to_exists:
        print('Such a card does not exist.')
    elif bal == 0:
        print('Not enough money!')
    else:
        print('Enter how much money you want to transfer:')
        transfer_amount = input()
        if int(transfer_amount) > bal:
            print('Not enough money!')
        else:
            cur.execute("UPDATE card SET balance = balance - " + transfer_amount + " WHERE number = " + card_num + ";")
            cur.execute("UPDATE card SET balance = balance + " + transfer_amount + " WHERE number = " + transfer_to + ";")
            conn.commit()


def close_account(card_num):
    global log_out
    log_out = True
    cur.execute("DELETE FROM card WHERE number = " + card_num + ";")
    conn.commit()
    print('The account has been closed!')


def logout():
    global log_out
    print('You have successfully logged out!')
    log_out = True


def start_session():
    print('Enter your card number:')
    card_num = input()
    print('Enter your PIN:')
    pin = input()

    if len(cur.execute("SELECT * FROM card WHERE number = " + card_num + " AND pin = " + pin + ";").fetchall()) > 0:
        global log_out
        log_out = False

        print('You have successfully logged in!\n')
        global end_session
        while not log_out and not end_session:
            y = second_prompt()

            if y == '1':
                check_balance(card_num)
            elif y == '2':
                add_income(card_num)
            elif y == '3':
                do_transfer(card_num)
            elif y == '4':
                close_account(card_num)
            elif y == '5':
                logout()
            elif y == '0':
                end_session = True
    else:
        print('Wrong card number or PIN!\n')


# Run the program
initialize_db()
end_session = False

while not end_session:
    x = prompt_for_input()
    if x == '1':
        create_account()
    elif x == '2':
        start_session()
    else:
        end_session = True

print('Bye!')
