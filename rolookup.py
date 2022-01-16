#!/usr/bin/env python3
# -*- coding: utf8 -*-

'''

+-----------------------------------------+
|  PROJECT     : Roblox Username Lookup   |
|  DESCRIPTION : Get infos about RBLX user|
|  RELEASE     : V1                       |
|  AUTHOR      : @F4C3R100                |
+-----------------------------------------+

'''

"""

CHANGELLOG
==========

v1:
---
- Added User Information
- Added Friends Count
- Added Follower Count
- Added Ban And Deleted Check On Friends And Followers
- Added Roblox Badge Check 
- Added User Badge Check (Writing names + url to textfile)

v2:
---
- Added User-Name Check (Registration Check) to fix error on lookup if no name exist
- Added argparse for better usage
- Added exception if no avatar is set
- Added banner
- Added folder for each search
- Added cleaner (remove folders)
- Add Inventory Information 
- Add Creations Information
- Add Last Rooms Played
- Add Single Checks
"""

import requests, json, datetime, dateutil.parser, sys, os, re, glob, argparse

class RobloxLookup:
    def __init__(self, username):
        self.username = username
        if self.username == "__clean__":
            self.cleanDir()
        else:
            self.run()

    def checkUser(self):
        main = requests.get(f"https://auth.roblox.com/v2/usernames/validate?request.username={self.username}&request.birthday=04%2F15%2F02&request.context=Signup")
        if main.json()['message'] == "Username is already in use":
            return True
        elif main.json()['message'] == "Username is valid":
            return False

    def makeDir(self):
        if not os.path.exists(f"{self.username}-info"):
            os.makedirs(f"{self.username}-info")

    def cleanDir(self):
        for _ in os.listdir(os.getcwd()):
            filelist = glob.glob(os.path.join(_, "*"))
            for file in filelist:
                os.remove(file)
            if os.path.isdir(_):
                os.removedirs(_)

    def lookup(self):
        main = requests.get(f"https://www.roblox.com/search/users/results?keyword={self.username}&maxRows=1&startIndex=0")

        if main.status_code == 400 or main.json()["UserSearchResults"] == None:
            sys.exit(f"\033[34m[\033[31m!\033[34m] \033[37mUsername \033[31m{self.username}\033[37m does not exist.")
        else:
            temp = main.json()["UserSearchResults"][0]
            self.info = {"user_id": temp["UserId"], "display_name": temp["DisplayName"], "description": temp["Blurb"].replace("\n", ""), "isOnline": temp["IsOnline"], "profile_url": "https://www.roblox.com"+str(temp["UserProfilePageUrl"])}

    def getAvatar(self):
        main = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?size=60x60&format=png&userIds={self.info['user_id']}")
        if main.json()['data'][0]['imageUrl'] == None:
            print(f"\033[34m[\033[31m!\033[34m] \033[37mNo Avatar Found \033[0m")
        elif main.json()['data'][0]['imageUrl']:
            writeImage = open(f"{self.username}-info/"+str(self.info["display_name"].replace(' ', ''))+".png", "wb")
            writeImage.write(requests.get(str(main.json()["data"][0]["imageUrl"])).content)
            print(f"\033[34m[\033[32m+\033[34m] \033[37mAvatar saved as : \033[32m{str(self.info['display_name'].replace(' ', ''))}.png\033[0m")

    def getDate(self):
        headers = {"Accept": "application/json"}
        main = requests.get(f"https://users.roblox.com/v1/users/{self.info['user_id']}", headers=headers)

        s = dateutil.parser.parse(main.json()['created'])

        creation_date = str(s.day) + "/" + str(s.month) + "/" + str(s.year) + " | " + str(s.hour) + ":" + str(s.minute)

        self.info.update({"creation_date": creation_date})

    def friendInfo(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0','Accept': 'application/json, text/plain, */*','Accept-Language': 'en-US,en;q=0.5','Origin': 'https://www.roblox.com','DNT': '1','Connection': 'keep-alive','Referer': 'https://www.roblox.com/','Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-site','TE': 'trailers'}
        response = requests.get(f'https://friends.roblox.com/v1/users/{self.info["user_id"]}/friends', headers=headers)

        friends = response.json()['data']

        print(f"\033[34m[\033[33m-\033[34m] \033[37mChecking if friends are banned...")
        w = open(f"{self.username}-info/friends.txt", "a+")

        for friend in friends:
            if friend['isBanned'] or friend['isDeleted']:
                print(f"\033[34m[\033[31m!\033[34m] \033[37mYour friend \033[31m{friend['displayName']} \033[37mis banned/deleted.")
            else:
                w.write(str(friend['name'])+"\n")
        w.close()
        response = requests.get(f'https://friends.roblox.com/v1/users/{self.info["user_id"]}/followers?sortOrder=Desc', headers=headers)

        followers = response.json()['data']

        f = open(f"{self.username}-info/followers.txt","a+")
        for follower in followers:
            if follower['isBanned']:
                print(f"\033[34m[\033[31m!\033[34m] \033[37mYour follower \033[31m{follower['displayName']} \033[37mis banned/deleted.")
            else:
                f.write(str(follower['name'])+"\n")
        f.close()
        self.info.update({"friends": str(len(friends)), "followers": str(len(followers))})

    def badgeInfo(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0','Accept': 'application/json, text/plain, */*','Accept-Language': 'en-US,en;q=0.5','Origin': 'https://www.roblox.com','DNT': '1','Connection': 'keep-alive','Referer': 'https://www.roblox.com/','Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-site','Cache-Control': 'max-age=0','TE': 'trailers'}
        response = requests.get(f'https://accountinformation.roblox.com/v1/users/{self.info["user_id"]}/roblox-badges', headers=headers)
        badges = []
        if len(response.json()) == 0:
            f4c3r100 = 'No badges available'
            result = 0
        else:
            for badge in response.json():
                badges.append(badge['name'])
            result = len(badges)
            f4c3r100 = ','.join(badges)
        default_url = f"https://badges.roblox.com/v1/users/{self.info['user_id']}/badges?sortOrder=Desc"

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0','Accept': 'application/json, text/plain, */*','Accept-Language': 'en-US,en;q=0.5','DNT': '1','Connection': 'keep-alive','Referer': f'https://www.roblox.com/users/{self.info["user_id"]}/inventory/','Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','TE': 'trailers'}

        cursor = ''
        page = 0
        archievements = 0
        k = []
        while True:
            archievements+=1
            if cursor == '' and page == 0:
                response = requests.get(f'https://www.roblox.com/users/inventory/list-json?assetTypeId=21&cursor=&itemsPerPage=100&pageNumber=1&userId={self.info["user_id"]}', headers=headers)
            else:
                response = requests.get(f'https://www.roblox.com/users/inventory/list-json?assetTypeId=21&cursor={cursor}&itemsPerPage=100&pageNumber={page}&userId={self.info["user_id"]}', headers=headers)
               
            if response.json()['Data']['nextPageCursor'] == None:
                start = response.json()['Data']['Start']
                end = response.json()['Data']['End']
                archievements += end - start
                break
            else:
                cursor = response.json()['Data']['nextPageCursor']
                start = response.json()['Data']['Start']
                end = response.json()['Data']['End']
                archievements += end - start
                page += 1
            for LL in response.json()['Data']['Items']:
                k.append(LL)
        archievements -= 1

        if archievements == -1:
            archievements = 0
            names = 'No badges available'
        else:
            if len(k) >= 15:
                temp = open(f"{self.username}-info/Archievements-{self.info['user_id']}.txt", "w")
                names = f"{self.username}-info/Archievements-{self.info['user_id']}.txt"
                for archievement in k:
                    temp.write(f"{archievement['Item']['Name']} | {archievement['Item']['AbsoluteUrl']}\n")
                temp.close()
            else:
                names = ', '.join(k)

        self.info.update({'rb_badges_names': f4c3r100, 'rb_badges': result, 'badges': archievements, 'badges_names': names})

    def run(self):
        if self.checkUser():
            print(f"\033[34m[\033[32m*\033[34m] \033[37mUsername exists.")
            self.makeDir()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mUser directory created...")
            print(f"\033[34m[\033[33m-\033[34m] \033[37mGetting information...")
            self.lookup()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mGetting creation date...")
            self.getDate()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mDownloading Avatar...")
            self.getAvatar()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mChecking friends count...")
            self.friendInfo()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mChecking badges...")
            self.badgeInfo()
            print(f"\033[34m[\033[33m-\033[34m] \033[37mInformation about user \033[34m{self.username}:")
            info = f"""\n\033[33m::::::::::::::::::::::::::::::::::::::::::::::::\n\033[33m::\n\033[33m:: \033[37mUser ID \033[34m: \033[32m{self.info['user_id']}\n\033[33m:: \033[37mDisplay Name \033[34m: \033[32m{self.info['display_name']}\n\033[33m:: \033[37mBio / Description \033[34m: \033[32m{self.info['description']}\n\033[33m:: \033[37mIs User Online \033[34m: \033[32m{self.info['isOnline']}\n\033[33m:: \033[37mProfile URL \033[34m: \033[32m{self.info['profile_url']}\n\033[33m:: \033[37mCreation Date \033[34m: \033[32m{self.info['creation_date']}\n\033[33m:: \033[37mFriends \033[34m: \033[32m{self.info['friends']}\n\033[33m:: \033[37mFollowers \033[34m: \033[32m{self.info['followers']}\n\033[33m:: \033[37mRoblox Badges \033[34m: \033[32m{self.info['rb_badges']}\n\033[33m:: \033[37mRoblox Badges (Name)\033[34m: \033[32m{self.info['rb_badges_names']}\n\033[33m:: \033[37mUser Badges \033[34m: \033[32m{self.info['badges']}\n\033[33m:: \033[37mUser Badges(Names) \033[34m: \033[32m{self.info['badges_names']}\n\033[33m::\n\033[33m::::::::::::::::::::::::::::::::::::::::::::::::\n"""
            print(info)
            temp = open(f"{self.username}-info/information.txt", "a+")
            temp.write(re.sub("\\033\[[0-9]{1,2}m", "",info))
            temp.close()
        else:
            print(f"\033[34m[\033[31m!\033[34m] \033[37mUsername not exist.")

def main():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")
    print("""\033[31m██████╗  ██████╗ ██╗      ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██████╗ \n██╔══██╗██╔═══██╗██║     ██╔═══██╗██╔═══██╗██║ ██╔╝██║   ██║██╔══██╗\n██████╔╝██║   ██║██║     ██║   ██║██║   ██║█████╔╝ ██║   ██║██████╔╝\n██╔══██╗██║   ██║██║     ██║   ██║██║   ██║██╔═██╗ ██║   ██║██╔═══╝ \n██║  ██║╚██████╔╝███████╗╚██████╔╝╚██████╔╝██║  ██╗╚██████╔╝██║     \n╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝ \n\n                   \033[32;1;3mRoblox' best user lookup!\033[0m\n\n                        \033[37;1mAuthor : \033[34m@f4c3r100\n                        \033[37mVersion: \033[34mv1\n                       \033[37mTeleGram: \033[34mhttps://t.me/f4c3r100\n                        \n            \033[35mInfo : \033[37mWrite "\033[31;4mexit\033[0;1;37m", "\033[31;4me\033[0;1;37m" or "\033[31;4m99\033[0;1;37m" to quit.\033[0m\n\n""")

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clean", dest="clean", action="store_true", help="Remove old user folders.")
    parser.add_argument("-u", "--user", dest="user", help="Username to lookup for.")
    args = parser.parse_args()
    
    if args.clean:
       RobloxLookup('__clean__')
       sys.exit()

    if args.user:
        username = args.user
        RobloxLookup(username)
    else:
        while True:
            username = input("\033[34m[\033[33m::\033[34m] \033[37mEnter user name : ")
            if username == "exit" or username == "e" or username == "99":
                break
            else:
                RobloxLookup(username)

if __name__ == '__main__':
    main()

