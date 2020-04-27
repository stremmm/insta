
#TO DO:python3 start.py
#error handling - restart from beginning

#if broken, fix lines 236, 268, 285, 294, 304,330, 333, 336, 353, 413, 437

#WHEN UPLOADING TO HEROKU - CHANGE SERVER AND LOOP MINUTES

import os

#import sqlite3
import psycopg2

import pandas as pd
import requests
import time
from time import sleep
import numpy as np
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import asyncio
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from clarifai.rest import ClarifaiApp, Image as ClImage

#like schedule: cutoff at 350/hr. and 450/day. 7 hours total 
likeBurst1 = 1
likeBurst2 = 1
likeBurst3 = 1
likeBurst4 = 1
likeBurst5 = 1
likeBurst6 = 1
likeBurst7 = 1

#for Insta official API
clientid = "fa15d70f3cba403e8cf35c0d7214ad2c"
ACCESS_TOKEN = "7268830997.fa15d70.32a832a7d3f7493c99af79f6355533d0"

oneHour = 60 * 60
twoHour = oneHour * 2
threeHour = oneHour* 3
fourHour = oneHour * 4
fiveHour = oneHour * 5
sixHour = oneHour * 6
sevenHour = oneHour * 7
eightHour = oneHour * 8

#importing spreadsheet w hashtags banned
df = pd.read_excel('cloutbotcategories.xlsx', sheet_name='Sheet1')
#get columns
columns = df.columns
columns2 = np.asarray(columns)
#print("Column headings: ", columns2)
#get rows. delete nan rows
categoriesBanned = (df['BANNED'].dropna()).as_matrix()
catBanned = np.asarray(categoriesBanned)
#print(catBanned)

n = 0

delay = 15 # seconds

#runCode = True

#headless chromedriver config to run on local server
#options = Options()
#options.add_argument('--headless')
#options.add_argument('--disable-gpu')

#headless chromedriver config to run on cloud server
chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

#normail insta login
insta_username = 'cibbott24'
insta_password = 'Cryptobot24'

#start session in chrome on local server
#if want to use headless
#browser = webdriver.Chrome('./assets/chromedriver', chrome_options=options)
#if want to see chrome
#browser = webdriver.Chrome('./assets/chromedriver')

#start session in chrome on CLOUD SERVER
browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)



#starting database with sqlite3
#two options to store:
##1 - in memory - lives in ram. good for testing. starts from scratch
#conn = sqlite3.connect(':memory:')
##2 - in file. creates file or connects to it
#conn = sqlite3.connect('burstDB.db')
#executes sql commands
#c = conn.cursor()
#comment out if running on file db, not memory
#c.execute("""CREATE TABLE heartDB (
        #userName text,
        #timeLiked text
        #)""")
#def insert_user(user, time):
    #context manager. don't need to commit after every insertion
    #with conn:
        #c.execute("INSERT INTO heartDB VALUES (:userName, :timeLiked)", {'userName': user, 'timeLiked': time})
#def query_users():
    #queries don't need a context like inserts, updates, and deletes
    #c.execute("SELECT * FROM heartDB")
    #return c.fetchall()
#def delete_table():
    #context manager. don't need to commit after every insertion
    #with conn:
        #c.execute("DELETE FROM heartDB")

#starting database with postgreSQL - ON LOCAL COMPUTER
#conn = psycopg2.connect(host="localhost", database="heartdb", user="", password="")
#c = conn.cursor()
#print("connected to db")

#starting database with postgreSQL - ON HEROKU
DATABASE_URL = os.environ['postgresql-tapered-55694']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()
print("connected to db")


async def sessionlogin(likeSchedule, b):

    #create table if doesn't already exists
    c.execute("""CREATE TABLE IF NOT EXISTS likeDB (
        userName text,
        timeLiked text
        )""")

    #navigate to a webpage
    browser.get('https://www.instagram.com/accounts/login/')

    try:
        #loginPage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, '_ev9xl')))
        loginPage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        print("Navigated to login page")

    except TimeoutException:
        print("Loading login took too much time")
        sleep(10)
   
    #find form inputs username
    input_username = browser.find_elements_by_xpath("//input[@name='username']")

    #enter username
    ActionChains(browser).move_to_element(input_username[0]). \
        click().send_keys(insta_username).perform()
    sleep(3)

    #find form input password
    input_password = browser.find_elements_by_xpath("//input[@name='password']")

    #enter password
    ActionChains(browser).move_to_element(input_password[0]). \
        click().send_keys(insta_password).perform()
    sleep(3)

    #find login button
    login_button = browser.find_elements_by_xpath("//form/span/button[text()='Log in']")
    #click log in button
    ActionChains(browser).move_to_element(login_button[0]).click().perform()

    print("Successfully logged in")
    sleep(10)

    #scrolling
    #find body
    body_elem = browser.find_element_by_tag_name('body')
    #load new images by going up and down
    for _ in range(3):
        body_elem.send_keys(Keys.END)
        sleep(5)
        body_elem.send_keys(Keys.HOME)
        sleep(5)

    startLoop(likeSchedule, b)

    #close conncetion to db
    c.close()
    conn.close()
    browser.close()

def startLoop(likeSchedule, b):

    #loop count setup
    runningCount = 0
    loopCount = 0 
    picCount = 0 

    while loopCount < likeSchedule:
        for i in range(len(b)):   
            sleepTimeout = randint(10, 31)
            print("hashtag", b[i], "+ sleep seconds ", sleepTimeout)
           
            browser.get('https://www.instagram.com/explore/tags/'
                + (b[1:] if b[:1] == '#' else b[i]))

            #try to load hashtag page
            try:
                #explorePage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, '_havey')))
                explorePage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                print("Navigated to explore tags page")

            except TimeoutException:
                print("Loading tags took too much time")
                sleep(10)

            #skip top posts
            main_elemSkipTop = browser.find_element_by_xpath('//main/article/div[2]')

            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)
            print("scrolled down")

            #go to most recent
            link_elems = main_elemSkipTop.find_elements_by_tag_name('a')
            total_links = len(link_elems)
            #should have 24 links to choose from
            print("Total loaded pics (not including top) ", total_links)
            sleep(5)

            #between 0 and 24
            chooseRandomPic = randint(0, (total_links - 1))
            print("Random order # ", chooseRandomPic)

            #click on first a 
            ActionChains(browser).move_to_element(link_elems[chooseRandomPic]).click().perform()
            sleep(10)

            #get usrname of post
            #OK for now
            postUser = browser.find_element_by_class_name('_2g7d5').text
            #postUser = browser.find_element_by_xpath('//div/div/div/a').text
            #/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/a

            sleep(3)

            #print(len(postuser))
            user_name = postUser
            print("Username: ", user_name)
            sleep(3)

            #go to account
            userLink = 'https://www.instagram.com/' + user_name
            browser.get(userLink)

            #looks at user account
            toUserProfile(runningCount, picCount, sleepTimeout, user_name)


        loopCount += 1
        print("Total full loops: ", loopCount, "out of", likeSchedule)

        #print database of all usernames
        fromDB = query_users()
        print(fromDB)



def toUserProfile(runningCount, picCount, sleepTimeout, user_name):
    #make sure page has loaded
    try:
        #OK for now. any class will do
        usernamePage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, '_4rbun')))
        #usernamePage = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '//ul/li[2]/a/span')))
        #//*[@id="react-root"]/section/main/article/header/section/ul/li[2]/a/span
        #//*[@id="react-root"]/section/main/article/div[1]/div/div[1]/div[1]/a/div/div[2]

        print("Navigated to users page")

    except TimeoutException:
        print("Loading users took too much time")
        sleep(10)

    #like criteria setup
    minPosts = 5     
    maxFollowers = 4000
    minFollowings = 40

    #post count
    posts = browser.find_elements_by_class_name('_fd86t')[0].text
    #posts = browser.find_elements_by_XPATH('//span[@id = "react-root"]//ul/li[1]/span/span')[0].text
    #//*[@id="react-root"]/section/main/article/header/section/ul/li[1]/span/span
    sleep(3)
    postCount = int(posts.replace(",",""))
    print("posts ", postCount)
    sleep(1)

    #followers
    followers = browser.find_elements_by_class_name('_fd86t')[1]
    #followers = browser.find_elements_by_XPATH('//span[@id = "react-root"]//ul/li[1]/span/span')[1]
    sleep(1)
    followerTitle = followers.get_attribute('title')
    sleep(1)
    followerCount = int(followerTitle.replace(",",""))
    print("Followers ", followerCount)
    sleep(1)

    #follows
    follows = browser.find_elements_by_class_name('_fd86t')[2].text
    #follows = browser.find_elements_by_XPATH('//span[@id = "react-root"]//ul/li[1]/span/span')[2].text
    sleep(1)
    followingCount = int(follows.replace(",",""))
    print("Following ", followingCount)
    sleep(3)

    if ((postCount >= minPosts) and (followerCount <= maxFollowers) and (followingCount >= minFollowings)):
        #go back to most recent pic posted and like it if the tags are ok
        print("passed post/follow criteria")

        #need - running count
        tagsAndComments(runningCount, user_name)

    else:
        print("failed post/follow criteria")
        #return to loop without liking picture

    picCount +=1

    print("Total looks this round: ", picCount)
    time.sleep(sleepTimeout)  


def tagsAndComments(runningCount, user_name):
    #go back to most recent pic
    main_elem = browser.find_elements_by_class_name('_mck9w')[0]
    #//*[@id="react-root"]/section/main/article/div[1]/div/div[1]/div[1]/a/div/div[1]

    link_elems1 = main_elem.find_elements_by_tag_name('a')
    total_links1 = len(link_elems1)
    print("Total loaded pics on profile ", total_links1)
    ActionChains(browser).move_to_element(link_elems1[0]).click().perform()
    sleep(10)

    #load user hashtags
    hashtags = browser.find_element_by_class_name('_ezgzd').text
    sleep(5)

    hashtagPara = hashtags.replace(",", "").replace("#", "").replace(".","").replace("-","").replace("@","").replace("_","").replace("|","")
    #print(len(hashtagPara))
    #print(hashtagPara)
    sleep(5)

    hashtagWords = hashtagPara.split()
    #print(hashtagWords)

    #if no comment, will be out of range
    try:  
        hashtagsComment = browser.find_elements_by_class_name('_ezgzd')[1].text
        #hasht = hashtags.find_elements_by_tag_name('a').text
        sleep(5)
        hashtagParaComment = hashtagsComment.replace(",", "").replace("#", "").replace(".","").replace("-","").replace("@","").replace("_","").replace("|","")
        #print(len(hashtagParaComment))
        #print(hashtagParaComment)
        sleep(5)
        hashtagWordsComment = hashtagParaComment.split()
        #print(hashtagWordsComment)
        isComment = True
        print("first comment?", isComment)

    except NoSuchElementException:
        isComment = False
        print("first comment?", isComment)
        #try to continue anyway

    except IndexError:
        isComment = False
        print("first comment?", isComment)
        #try to continue anyway



    #if there is a first comment
    if isComment == True:
        if (any(x in hashtagWords for x in catBanned)) and (any(x in hashtagWordsComment for x in catBanned)):
            print("failed hashtag criteria")

        else:
            print("passed hashtag criteria")

            clarifai(runningCount, user_name)

    #if no first comment
    elif isComment == False:
        if any(x in hashtagWords for x in catBanned):
            print("failed hashtag criteria")

        else:

            print("passed hashtag criteria")

            clarifai(runningCount, user_name)



def clarifai(runningCount, user_name):
    #need img_link
    clarifai_api = ClarifaiApp(api_key='a88172a02f3e4036b5b13bdee391e7f3')
    img_link = browser.find_element_by_xpath('//img[@class = "_2di5p"]') \
        .get_attribute('src')

    #print(img_link)

    #general model
    #model = clarifai_api.models.get('general-v1.3')

    #nsfw model
    model = clarifai_api.models.get('e9576d86d2004ed1a38ba0cf39ecb4b1')

    image = ClImage(url=img_link)
    #only predicts image, not videos
    result = model.predict([image])
    #print(result)

    sfwValue = float(result['outputs'][0]['data']['concepts'][0]['value'])
    print(sfwValue)


    if sfwValue >= 0.80:

        print("passed clarifai")
        #finding hearts when on picture - ready to use. 
        #hearts = browser.find_elements_by_xpath("//a[@role='button']/span[@class='_8scx2']")
        hearts = browser.find_elements_by_class_name('coreSpriteHeartOpen')
        #/html/body/div[4]/div/div[2]/div/article/div[2]/section[1]/a[1]/span

        print(len(hearts))
        sleep(5)
        ActionChains(browser).move_to_element(hearts[0]).click().perform()
        
        print("liked photo")
        sleep(5)
        
        runningCount +=1
        print("Total likes this round: ", runningCount)

        #INSERT USERNAME AND TIME TO DATABASE using sqlite3
        #timeNow = time.ctime(int(time.time()))
        #insert_user(user_name, timeNow)

        #query all to make list
        #allUsers = query_users()
        #print(allUsers)

        #delete all usernames in db and check to make sure they cleared
        #delete_table()

        #anyLeft = query_users()
        #print(anyLeft)

        #INSERT USERNAME AND TIME TO DATABASE using postgreSQL
        timeNow = time.ctime(int(time.time()))
        insert_user(user_name, timeNow)

    else:
        print("failed clarifai")



def insert_user(user, time):
    with conn:
        c.execute("INSERT INTO likedb (userName, timeLiked) VALUES (%s, %s)", (user,time))

#query all users 
def query_users():
        c.execute("SELECT * FROM likedb")
        return c.fetchall()

#query specific user
def query_users2(username):
        c.execute("SELECT * FROM likedb WHERE username = %s", (username,));
        return c.fetchall()

#delete entire table
def delete_table():
    with conn:
        c.execute("DELETE FROM likedb")

#delete specific username
def delete_table2(username):
    with conn:
        c.execute("DELETE FROM likedb WHERE username = %s", (username,));


#general self info
async def generalInfo ():

    PARAMSGeneral = {'ACCESS_TOKEN': ACCESS_TOKEN}
    URLGeneral = "https://api.instagram.com/v1/users/self/?access_token="+ACCESS_TOKEN

    r1 = requests.get(url = URLGeneral, params = PARAMSGeneral)
    data1 = r1.json()

    dataGeneral = data1['data']
    username = dataGeneral['username']
    #print("username: ", username)
    dataCounts = dataGeneral['counts']
    media = dataCounts['media']
    #print("Media :", media)
    follows = dataCounts['follows']
    #print("Follows: ", follows)
    followed_by = dataCounts['followed_by']
    #print("Followers: ", followed_by)
    

#recent post
async def recentMediaInfo ():
    #result = await generalInfo()
    await generalInfo()

    count = 1
    PARAMSRecent = {'ACCESS_TOKEN': ACCESS_TOKEN, 'count': count}
    URLRecent = "https://api.instagram.com/v1/users/self/media/recent/?access_token="+ACCESS_TOKEN

    r2 = requests.get(url = URLRecent, params = PARAMSRecent)
    data2 = r2.json()


    for uploadTime in data2['data']:
        #print("Upload time: ", uploadTime['created_time'])
        lastUploadTime = int((uploadTime['created_time']))


    currentTime = int(time.time())
    #print("Current Time: ",currentTime)

    differenceTime = currentTime - lastUploadTime
    print("Difference in time: ", differenceTime)

    


    if currentTime <= (lastUploadTime + sevenHour):
        print("Uploaded in last 7 hour")
        #this will cause likes to begin going
        #runCode = False


        #importing spreadsheet
        #df = pd.read_excel('cloutbotcategories.xlsx', sheet_name='Sheet1')

        #get columns
        #columns = df.columns
        #columns2 = np.asarray(columns)
        #print("Column headings: ", columns2)

        #get rows. delete nan rows
        categoriesFashion = (df['FASHION'].dropna()).as_matrix()
        catFashion = np.asarray(categoriesFashion)
        #print("Category Rows: ", catFashion)

        #get rows. delete nan rows
        categoriesTravel = (df['TRAVEL'].dropna()).as_matrix()
        catTravel = np.asarray(categoriesTravel)
        #print("Category Rows: ", catTravel)

        #get rows. delete nan rows
        categoriesHealth = (df['PHOTOGRAPHY'].dropna()).as_matrix()
        catHealth = np.asarray(categoriesHealth)
        #print("Category Rows: ", catHealth)

        #get rows. delete nan rows
        categoriesPhotography = (df['HEALTH'].dropna()).as_matrix()
        catPhotography = np.asarray(categoriesPhotography)
        #print("Category Rows: ", catPhotography)

        #get rows. delete nan rows
        categoriesArt = (df['ART/DESIGN'].dropna()).as_matrix()
        catArt = np.asarray(categoriesArt)
        #print("Category Rows: ", catArt)

        categoriesDesign = (df['HOME DESIGN'].dropna()).as_matrix()
        catDesign = np.asarray(categoriesDesign)
        #print("Category Rows: ", catDesign)

        categoriesFood = (df['FOOD'].dropna()).as_matrix()
        catFood = np.asarray(categoriesFood)
        #print("Category Rows: ", catFood)


        if differenceTime <= oneHour:
            n = likeBurst1
            print("First hour. Like = ", n)
            #set timeout 1 hr - how long it takes to cycle through - 35 mins to get to 100 with 5 tags

            await sessionlogin(n, catTravel)
            #time.sleep(thirtyMinute)

        elif ((differenceTime >= oneHour) and (differenceTime <= twoHour)):
            n = likeBurst2
            print("Second hour. Like = ", n)
            await sessionlogin(n, catPhotography)
            #time.sleep(thirtyMinute)

        elif ((differenceTime >= twoHour) and (differenceTime <= threeHour)):
            n = likeBurst3
            print("Three hour. Like = ", n)
            await sessionlogin(n, catFashion)
            #time.sleep(thirtyMinute)

        elif((differenceTime >= threeHour) and (differenceTime <= fourHour)):
            n = likeBurst4
            print("Four hour. Like = ", n)
            await sessionlogin(n, catHealth)
            #time.sleep(thirtyMinute)

        elif((differenceTime >= fourHour) and (differenceTime <= fiveHour)):
            n = likeBurst5
            print("Five hour. Like = ", n)
            await sessionlogin(n, catArt)
            #time.sleep(thirtyMinute)

        elif((differenceTime >= fiveHour) and (differenceTime <= sixHour)):
            n = likeBurst6
            print("Six hour. Like = ", n)
            await sessionlogin(n, catDesign)
            #time.sleep(thirtyMinute)

        elif((differenceTime >= sixHour) and (differenceTime <= sevenHour)):
            n = likeBurst7
            print("Seven hour. Like = ", n)
            await sessionlogin(n, catFood)
            #time.sleep(fortyFiveMinute)


        else:
            print("Code is done running. switching back to background mode")
            #runCode = True
            return;
        return;
            
    else:
        print("uploaded over 7 hours ago")
        #will retry in an hour
        #runCode = True
        return;


#run every hour
while True:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(recentMediaInfo, 'interval', minutes=60, id = 'myJobID')
    scheduler.start()

    try: 
        asyncio.get_event_loop().run_forever()
        #loop = asyncio.get_event_loop()

        
        #loop = asyncio.ensure_future()
        #loop.run_until_complete(recentMediaInfo())

        loop.close()
        scheduler.remove_job('myJobID')

    except (KeyboardInterrupt, SystemExit):
        pass


#while (runCode == True):
    #recentMediaInfo()
    #time.sleep(fifteenMinute)

#while (runCode == False):
    #schedule.run_pending()
    #recentMediaInfo()
