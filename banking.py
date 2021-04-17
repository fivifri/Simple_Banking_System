import random
import sqlite3 as sql


con = sql.connect('card.s3db')
with con:
    users = con.cursor()
    users.execute('''CREATE TABLE IF NOT EXISTS card (
                         id INTEGER,
                         number TEXT,
                         pin TEXT,
                         balance INTEGER DEFAULT 0);''')
    con.commit()


def main_menu():
    command = int(input('1. Create an account\n2. Log into account\n0. Exit\n'))
    if command == 1:
        new_user()
    elif command == 2:
        card = input('\nEnter your card number:\n')
        pin = int(input('Enter your PIN:\n'))
        log_in(card, pin)
    elif command == 0:
        print('\nBye!')
    else:
        print('please enter correct data')


def user_menu(card):
    command = int(input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n'))
    print('')
    if command == 1:
        print('Balance:', current_balance(card), '\n')
        user_menu(card)
    elif command == 2:
        balance_change(int(input('Enter income:\n')), card)
        print('Income was added!\n')
        user_menu(card)
    elif command == 3:
        do_transfer(card)
    elif command == 4:
        close_account(card)
    elif command == 5:
        print('You have successfully logged out!\n')
        main_menu()
    elif command == 0:
        print('Bye!')
    else:
        print('please enter correct data')


def do_transfer(card):
    recipient = input('Transfer\nenter card number:\n')
    if recipient == card:
        print("You can't transfer money to the same account!")
    elif luhn(recipient[:15]) != recipient[-1]:
        print("Probably you made a mistake in the card number. Please try again!")
    elif not card_is_exist(recipient):
        print("Such a card does not exist.")
    else:
        income = int(input("Enter how much money you want to transfer:\n"))
        if income > current_balance(card):
            print('Not enough money!')
        else:
            balance_change(income, recipient)
            balance_change(-income, card)
            print('Success!')
    print('')
    user_menu(card)


def close_account(card):
    users.execute(f"DELETE FROM `card` WHERE number='{card}'")
    con.commit()
    print('The account has been closed!')
    main_menu()


def current_balance(card):
    users.execute(f"SELECT Balance FROM `card` WHERE number = '{card}'")
    return users.fetchall()[0][0]


def balance_change(income, card):
    users.execute(f"UPDATE `card` SET balance='{income + current_balance(card)}' WHERE number='{card}'")
    con.commit()


def generating_first_digits():
    card = ('400000' + str(random.randint(0, 999999999)) + '0' * 8)[:15]
    return card + luhn(card)


def luhn(card):
    card = list(map(int, card))
    for i in range(0, 15, 2):
        card[i] *= 2
        if card[i] > 9:
            card[i] -= 9
    control_number = sum(card)
    return str(abs((control_number % 10) - 10) % 10)


def card_is_exist(card):
    users.execute(f"SELECT EXISTS (SELECT * FROM `card` WHERE number = '{card}' LIMIT 1);")
    return users.fetchall()[0][0]


def new_user():
    card = generating_first_digits()
    while card_is_exist(card):
        card = generating_first_digits()
    pin = int((str(random.randint(0, 9999)) + '0' * 3)[:4])
    users.execute("SELECT COUNT (*) FROM `card`")
    users.execute(f"""INSERT INTO `card` (id, number, pin) VALUES 
                      ('{users.fetchall()[0][0] + 1}', '{str(card)}', '{str(pin)}')""")
    con.commit()
    print(f'\nYour card has been created\nYour card number:\n{card}\nYour card PIN:\n{pin}\n')
    main_menu()


def log_in(card, pin):
    if card_is_exist(card):
        users.execute(f"SELECT pin FROM `card` WHERE number = '{card}'")
        if int(users.fetchall()[0][0]) == pin:
            print('\nYou have successfully logged in!\n')
            user_menu(card)
        else:
            print('\nWrong card number or PIN!\n')
            main_menu()
    else:
        print('\nWrong card number or PIN!\n')
        main_menu()


main_menu()
