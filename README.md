# installation

1. Click `download` or use command `git clone https://github.com/Aqua-4/auto-insta.git`
2. Open `setup.sh` OR `sh setup.sh`
3. Run `pip install -r requirements.txt` to install all dependent libraries
4. Run `python download_driver.py` or download suitable driver from `https://chromedriver.chromium.org/downloads`
5. `python account_setup.py` - and follow instructions
6. To update the database run `python sync_db.py` - this will store your current instagram audience
7. Start the bot by running `python start_bot.py`

* To reset password or to reset chrome path run `python account_setup.py`
* to update software open git bash & run `git pull`


___________________________________________________________
# roadmap
## APPROACH:

### Where do i store password?

1. ask for passwd at bot_init
   1. encrypt and store into DB
2. Create yaml or Config file for storing password
   1. Hard to keep this in sync with GIT


### follow_mod:

*  args(hashtag,numOfpeopletoFollow)

1. use a hahtag as an argument and start followong the people
2. 


## RULES:

1. cannot unfollow all the people that i just followed a day ago.
    1. workaround-

# Insta Mobile

## APPROACH & FUNCTION:

1. start at midnight
2. post random image from *img_post_gain folder* glob("*.jpg")
3. check the activity every certain amount of time
4. double the time to recheck 
5. create a dict for the activity 
6. seperate dict for like and comment
7. log the activity into a file
8. perform the activity 
9. delete the post after a certain duration -- to find the SHELF LIFE of post


## MSG STR:

1. Follow @parashar_sangle and i will follow back 
2. Comment IFB, done, active x4 times
3. like my previous posts and then comment "likeme" so that i can go and like your latest post
4. Follow all commenters
   