import praw
import credentials
import time
import re

# omedetou bot

def is_sub_milestone(submission):
    """ Returns if the submission is a valid subscriber milestone submission """

    if not isinstance(submission, praw.models.reddit.submission.Submission):
        raise Exception(f"Invalid type: {type(submission).__name__}")

    if submission.link_flair_text != "Milestone":
        return False

    print(submission.title)
    if not re.search("\d[\d+.,]+[\dkKmM]", submission.title) and not re.search("\d[mM]{1} subs", submission.title):
        # Probably not subscriber announcement or title was not well constructed enough.
        return False
    return True

def already_commented_on(submission, commented_submission_ids):
    """ Returns if already commented on submission """
    return submission.id in commented_submission_ids

def say_omedetou(submission):
    """ Well, says omedetou... """

    if not isinstance(submission, praw.models.reddit.submission.Submission):
        raise Exception(f"Invalid type: {type(submission).__name__}")

    expression = re.search("\d[\d+.,]+[\dkKmM]", submission.title)
    if not expression:
        # TODO make it find "...X MILLION SUBS..." too 
        expression = re.search("\d[mM]{1} subs", submission.title) # I'm just bad with regex, so I had to add 
        if not expression:                                         # "million subs" with another regex
            return
    
    expression = expression.group(0)
    subscribers = expression.split()[0]
    exc_count = 0

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
        
    if exc_count <= 0:
        print("Something went wrong.")
        return

    try:
        print(submission.id, "おめでとう"+"！"*exc_count)
        submission.reply("おめでとう"+"！"*exc_count)
    except:
        raise Exception("Couldn't reply")




commented_submission_ids = [] # holds 100 submission ids

if __name__ == "__main__":
    subreddit = praw.Reddit(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        username=credentials.username,
        password=credentials.password,
        user_agent=credentials.user_agent
    ).subreddit("hololive")

    while True:
        try:
            for submission in subreddit.stream.submissions():
                if is_sub_milestone(submission) and not already_commented_on(submission, commented_submission_ids):
                    say_omedetou(submission)
                    if len(commented_submission_ids) == 100:
                        commented_submission_ids.pop(0)
                    commented_submission_ids.append(submission.id)
        except KeyboardInterrupt:
            print("Keyboard interrupt.")
            break
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            time.sleep(10)