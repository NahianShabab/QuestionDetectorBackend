# This script is used for bootstrapping a new user. This 
# bypasses normal checking, to allow for at least one user
# to be created before auth is implemented
# This is not part of normal backend loop
# Run this wisely!

import database
from models import UserCreate,is_valid_user_role,_USER_VALID_ROLES
from utils.email_validity import is_valid_email
import argparse
import re
import asyncio









if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username',required=True)
    parser.add_argument('--password',required=True)
    parser.add_argument('--first-name',required=True)
    parser.add_argument('--last-name',required=False)
    parser.add_argument('--user-role',required=True)
    parser.add_argument('--email',required=False)
    args = parser.parse_args()
    # print(args.email)
    if args.email is not None:
        if(is_valid_email(args.email)):
            # print('Valid Email')
            email_exists = asyncio.run(database.user_email_exists(args.email))
            if email_exists:
                print('A user with this Email already exists')
                exit()
            pass
        else:
            print('Invalid email')
            exit(0)
    if not is_valid_user_role(args.user_role):
        print('Invalid User Role.',end=' ')
        print(f'It must be one of these: {_USER_VALID_ROLES}')
    if len(args.password)<8:
        print('Password must be at least 8 Characters long')
        exit()
    if not args.username.isalnum():
        print('username must be alphanumeric')
        exit()
    if args.last_name is not None and not args.last_name.isalnum():
        print('Last name must be alphanumeric')
        exit()
    if not args.first_name.isalnum():
        print('First name must be alphanumeric')
        exit()
    username_exists = asyncio.run(database.username_exists(args.username))
    if username_exists:
        print('Username is taken')
        exit()
    print('Creating User: ',args)
    user = UserCreate(username=args.username,user_role=args.user_role,first_name=args.first_name,\
                      last_name=args.last_name,email=args.email,password=args.password)
    asyncio.run(database.create_user(user))
    print('User Created')
    
    