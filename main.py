from MALFriendBot.database import Database
from MALFriendBot.Client import MALFriendClient
from dotenv import load_dotenv
import os
import sys
import argparse
load_dotenv()
userTable = Database()

parser = argparse.ArgumentParser(description="MyAnimeList Friend Bot")
parser.add_argument('--headless', action='store_true', help='Disable Chrome Visibility')
parser.add_argument('-n', type=int, default=20, help='Number of Friends you wish to add.')
parser.add_argument("--message", type=str, default=None, help="Message to send to prospective friends")
parser.add_argument("--username", type=str, default=os.getenv("MALusername"), help="Username Login for MAL")
parser.add_argument("--password", type=str, default=os.getenv("MALpassword"), help="password Login for MAL")
parser.add_argument("-a", action='store_false', help="Skip Setting Check")
args = parser.parse_args()
if args.a:
    print(f"Settings:\nFriends to add: {args.n}\nmessage: {args.message}\nheadless: {args.headless}")
    settingcheck = input("Press Enter to Start. Other input will cancel\n")
    if settingcheck != "":
        sys.exit(0)
    os.system('cls')
    

client = MALFriendClient(headless=args.headless)

userUsername = args.username
userPassword = args.password

login = client.mallogin(username=userUsername, password=userPassword)
if login != 0:
    client.closeclient()
    print("Login Failed. Login Information likely wrong")
    sys.exit()
friends = 0
while friends <= args.n:
    users = client.getusers()
    users = userTable.user_check(users)
    if len(users) == 0:
        continue
    for username in users[:10]:
        if client.adduser(username, message=args.message):
            friends += 1
            if friends >= args.n:
                friends += 1
                break
            if friends % 5 == 0:
                print(f"{args.n-friends} friends left to go")

print("All Friends added. Closing")
client.closeclient()
userTable.close
sys.exit(0)

    
