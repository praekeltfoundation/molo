import csv
import random
import string
import sys

if len(sys.argv) < 2:
    raise Exception, 'First argument to {0} must be a CSV file'.format(sys.argv[0])

filename = sys.argv[1]

sanitised_users = []


def obfuscate_username(username):
    '''
    Keep the same string structure (characters, length) but substitute
    all ASCII characters and digits for random ones for anonymity.
    '''
    sanitised_username = ''

    for character in username:
        if character in string.ascii_lowercase:
            sanitised_username += random.choice(string.ascii_lowercase)
        elif character in string.ascii_uppercase:
            sanitised_username += random.choice(string.ascii_uppercase)
        elif character in string.digits:
            sanitised_username += random.choice(string.digits)
        else:
            sanitised_username += character

    return sanitised_username

def obfuscate_date_of_birth(year, month, day):
    '''
    Keep users the same age but give them a random month and day
    of birth for anonymity.
    '''
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    return year, month, day

def sanitise_field(name, value):
    if value == '':
        return value

    if name ==  'username':
        return obfuscate_username(value)

    if name == 'date_of_birth':
        year, month, day = value.split('-')
        year, month, day = obfuscate_date_of_birth(year, month, day)

        return '{}-{:02d}-{:02d}'.format(year, month, day)

    if name in ['id', 'is_active', 'date_joined', 'last_login', 'gender']:
        return value

    raise Exception, 'Field {0} can not be sanitised'.format(name)


with open(filename, 'r') as input_file:
    header = csv.reader(input_file).next()
    input_file.seek(0)
    users = list(csv.DictReader(input_file))

for user in users:
    sanitised_user = []
    for element in header:
        sanitised_user.append(sanitise_field(element, user[element]))

    sanitised_users.append(sanitised_user)

with open(filename, 'w') as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(header)
    for user in sanitised_users:
        csv_writer.writerow(user)
