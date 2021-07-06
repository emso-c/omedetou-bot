import praw
import credentials
import time
import re
import os
import random
from datetime import datetime
import logging


logging.basicConfig(filename='logs.log', level=logging.CRITICAL, 
    format='[%(asctime)s]%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def is_sub_milestone(submission) -> bool:
    """ Returns if the submission is a valid subscriber milestone submission """

    if not isinstance(submission, praw.models.reddit.submission.Submission):
        logger.debug(f"Invalid submission type: {type(submission).__name__}")
        return False

    if submission.link_flair_text != "Milestone":
        return False

    if not re.search("\d[\d+.,]+[\dkKmM] subs", submission.title) and not re.search("\d[mM]{1} subs", submission.title):
        # Probably not a subscriber announcement or title was not well constructed enough.
        return False
    logger.debug(f"{submission.id} is a valid subsriber milestone submission.")
    return True
    
def say_omedetou(submission):
    """ Well, says omedetou... """
    
    logger.info(f"Saying omedetou: {submission.title} ({submission.id})")
    expression = re.search("\d[\d+.,]+[\dkKmM] subs", submission.title)
    if not expression:
        expression = re.search("\d[mM]{1} subs", submission.title) # I'm just bad with regex, so I had to add 
        if not expression:                                         # "xM subs" with another regex
            logger.error("Title is not in a valid format")
            return
    
    expression = expression.group(0)
    subscribers = expression.split()[0]
    exc_count = 0

    logger.debug(f"{expression=}")
    logger.debug(f"{subscribers=}")

    if subscribers[-1] in ['m', 'M'] or subscribers.count('0') == 6:
        exc_count = int(subscribers[0])
        if (subscribers.count('0') == 6 and subscribers[0] == '1') or \
            (subscribers[-1] in ['m', 'M'] and subscribers[0] == '1'):
            exc_count = 10
    
    elif subscribers[-1] in ['k', 'K'] or subscribers.count('0') in [4, 5]:
        exc_count = int(subscribers[0])
        if (subscribers.count('0') == 5 and subscribers[0] == '1') or \
            (subscribers[-1] in ['k', 'K'] and subscribers[0] == '1'):
            exc_count = 10
        
    logger.debug(f"{exc_count=}")
    if exc_count <= 0:
        logger.error(f"Something went terribly wrong, {exc_count=}")
        return

    try:
        logger.debug(f"おめでとう{'！'*exc_count}")
        submission.reply("おめでとう"+"！"*exc_count)
    except:
        logger.error(f"Couldn't reply, {exc_count=}")
        return

def init_if_not_exists(filename):
    """ creates file if not exists """
    if not os.path.exists(filename):
        try:
            with open(filename, 'w') as f:
                logger.info(f'{filename} initialized')
                pass
        except Exception as e:
            logger.error(f"Couldn't initialize {filename}")
            raise FileNotFoundError

def save_submission_id(submission_id, filename):
    """ saves submission id to the specified fodler """
    
    init_if_not_exists(filename)
    try:
        with open(filename, 'a') as f:
            f.write(submission_id+'\n')
            logger.info(f"{submission_id} has been saved")
    except Exception as e:
        logger.error(f"Couldn't save submission id: {e}")

def already_commented_on(submission_id, filename) -> bool:
    """ Returns if already commented on submission """
    
    init_if_not_exists(filename)
    try:
        with open(filename, 'r') as f:
            submission_ids = [s.strip() for s in f.readlines()]
            if submission_id in submission_ids:
                logger.debug(f"Already commented on {submission_id}")
                return True
    except Exception as e:
        logger.error(f'Couldn\'t determine if already commented on {submission_id}: {e}')
        return True  # Don't risk it
    return False

def placeholder(characters=['.',':'], size=10):
    return ''.join([random.choice(characters) for _ in range(size)]) 

if __name__ == "__main__":
    subreddit = praw.Reddit(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        username=credentials.username,
        password=credentials.password,
        user_agent=credentials.user_agent
    ).subreddit("hololive")
    logger.info("logged in")

    fname = 'submissions.txt'
    while True:
        try:
            for submission in subreddit.stream.submissions():
                print(placeholder(), end='\r')
                if is_sub_milestone(submission) and not already_commented_on(submission.id, fname):
                    say_omedetou(submission)
                    save_submission_id(submission.id, fname)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print()
            logger.error(e)
        finally:
            try:
                logger.info(f"Sleeping...  ({datetime.now().strftime('%Y.%m.%d-%H:%M:%S')})")
                time.sleep(1800)  # good night
            except KeyboardInterrupt:
                break