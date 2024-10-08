#!/usr/bin/python

import praw
from config_lopen import *
import os
import random
import time
import re
import requests
from bs4 import BeautifulSoup, Comment
from quotes import *
from praw.models import Submission
import pandas as pd
import numpy as np
import json
from nltk.corpus import wordnet as wn
global vorin


try:
    from transformers import pipeline
    sentiment_analysis = pipeline("sentiment-analysis")
except: print("Transformers not imported")

#Bot login
def bot_login():
    r = praw.Reddit(username = userN,
                    password = userP,
                    client_secret = cSC,
                    client_id = cID,
                    user_agent = userAgent)
    return r


#Main function
def run_bot(r, comments_replied_to2, posts_replied_to, comments_skimmed, mod_comments, mod_posts, removed_comments, WholeWord, rank, count, mod_queue_posts):
    #print(rank('TestingStormblessed'))
    saved = [x.id for x in r.user.me().saved(limit = None) if isinstance(x, Submission)]
    cremrunner = pd.read_csv("Ideals.csv", usecols = ["Name", "Order", "Spren", "Oaths"])
    vorin = pd.read_csv("Vorin.csv", usecols = ["Name", "Points"])
    chouta_df = pd.read_csv("Chouta.csv", usecols = ["Name", "Chouta"])

    ### RETIRED ###
    # for crempost in r.subreddit('Cremposting').new(limit = 25):
    #     try:
    #         flair = crempost.link_flair_text.lower()
    #     except:
    #         flair = ""

    #     if not crempost.stickied:
    #         if crempost.id not in saved and ("memeing every chapter" in crempost.title.lower() or "meming every chapter" in crempost.title.lower() or "Wasing the meming".lower() in crempost.title.lower() or "meming every letter" in crempost.title.lower() or "memeing arcanum" in crempost.title.lower()) and crempost.author != r.user.me():
    #             aut = crempost.author

    #             if aut == "JeffSheldrake":
    #                 crempost.reply("[Meming every chapter - Mistborn](https://redd.it/pkrvjy/)")
    #                 meme_post = r.submission(id = 'pkrvjy')

    #             elif aut == "Anacanrock11":
    #                 crempost.reply("[Meming every chapter - Stormlight Archive](https://redd.it/pkrqeg/)")
    #                 meme_post = r.submission(id = 'pkrqeg')

    #             elif aut == "AlThorStormblessed":
    #                 crempost.reply("[Meming every letter of the Stormlight Archive](https://redd.it/r9c2tt/)")
    #                 meme_post = r.submission(id = 'r9c2tt')

    #             elif aut == "bradles0":
    #                 crempost.reply("[Meming Arcanum Unbounded](https://redd.it/rmmepj/)")
    #                 meme_post = r.submission(id = 'rmmepj')

    #             try:
    #                 text = meme_post.selftext
    #                 meme_post.edit(f'* [{crempost.title}](https://www.reddit.com{crempost.permalink})\n\n' + text)

    #                 crempost.save()

    #                 print("Post saved")

    #             except:
    #                 crempost.save()
    #                 print("Some rando post saved.")

    #         if crempost not in mod_posts and ('nsfv' in crempost.title.lower() or 'not safe for vorin' in crempost.title.lower()) and not crempost.over_18:
    #             crempost.mod.nsfw()

    #             mod_posts.append(crempost.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

    #             with open("mod_posts.txt", "a", encoding='cp1252') as f:
    #                 f.write(crempost.id + "\n")

    #         elif crempost not in mod_posts:
    #             mod_posts.append(crempost.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

    #             with open("mod_posts.txt", "a", encoding='cp1252') as f:
    #                 f.write(crempost.id + "\n")

    for post in r.subreddit('Cremposting').hot(limit = 7):
        post_num = random.randint(1, 3)
        if(post_num != 1):
            if not post.stickied and post.id not in posts_replied_to:
                chouta_num = chouta(post.author)
                posts_replied_to.append(post.id)
                with open("posts_replied_to.txt", "a", encoding='cp1252') as f:
                    f.write(post.id + "\n")
            continue

        if not post.stickied and post.id not in posts_replied_to:
            chouta_num = chouta(post.author)
            post_quotes = [
                "This is good crem, gancho!",
                "Great meme, Gon!",
                "This crem deserves some chouta!",
                "This post is as delicious as chouta."]
            chouta_quotes = [
                f"You now have {chouta_num} choutas for your efforts!",
                f"You have {chouta_num} posts I love, gon!",
                f"You have pleased the mighty Lopen {chouta_num} times with your posts!"
            ]

            post.reply(random.choice(post_quotes) + " " + random.choice(chouta_quotes)) #Chooses a random quote from above list
            print("Post found!")

            posts_replied_to.append(post.id)
            with open("posts_replied_to.txt", "a", encoding='cp1252') as f:
                f.write(post.id + "\n")

#Restore removed comments
    for comments in removed_comments[-10:]:
        if comments:
            comment = r.comment(id = comments)
            comment.refresh()
            if not comment.approved_by:
                for key in ["!>", "<!", ">! ", ">!", "!<"]:
                    if key == ">!":
                        thing = "!<"
                    else:
                        thing = ">!"

                    if key in ["!>", "<!"] and key in comment.body and (comment.body.count(key) != comment.body.count('>!>!') or comment.body.count(key) != comment.body.count('!<!<')):
                        pass
                    elif ">! " in comment.body and "\\>!" not in comment.body and "\\!<" not in comment.body:
                        pass
                    elif comment.body.count(key) != comment.body.count(thing):
                        pass
                    else:
                        for my_comment in list(comment.replies):
                            if my_comment.author == r.user.me() and 'spoiler tag' in my_comment.body.lower():
                                my_comment.delete()

                        comment.mod.approve()
                        removed_comments.remove(comments)

                        with open('removed_comments.txt', 'r') as file :
                            filedata = file.read()

                        # Replace the target string
                        filedata = filedata.replace(comments, '')

                        # Write the file out again
                        with open('removed_comments.txt', 'w') as file:
                            file.write(filedata)

                        #print("Comment approved.")

                        break

#Inbox
    for comment in list(r.inbox.comment_replies(limit = 20)) + list(r.inbox.submission_replies(limit = 10)):
        if comment.new:
        #Sentience
            for word in ['sentient', 'sentience']:
                if word in comment.body.lower() and "not " + word not in comment.body.lower():
                    sentient = ["Gon, I am definitely not sentient!",
                                "Of course I am not sentient!",
                                "Totally not sentient, lol!",
                                "Storm off, I am a bot, not a sentient being!",
                                "Who said I am sentient gon? Must be one of those Lighteyes."]
                    comment.reply(random.choice(sentient))
                    comment.mark_read()

                    print("Definitely not sentient!")

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

        #Good bot/cakeday
            if ("good bot" in comment.body.lower() or "cake day" in comment.body.lower() or "cakeday" in comment.body.lower()):
                good_bot = [
                    "Thanks, gancho!",
                    "I do my best, gon!",
                    "Why, you are welcome!",
                    "That's what a one-armed Herdazian is for!",
                    "That is what I do, gon!",
                    f"Good {comment.author}"
                ]

                comment.reply(random.choice(good_bot)) #Chooses a random quote from above list
                comment.mark_read()

                print("Good bot!")

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

        #Bad bot
            if "bad bot" in comment.body.lower():
                bad_bot = [
                    "**Makes the Lopen gesture!**",
                    f"Storm off, {comment.author}!",
                ]

                comment.reply(random.choice(bad_bot)) #Chooses a random quote from above list
                comment.mark_read()

                print("Bad bot!")

                comments_replied_to2.append(comment.id)
                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

        #Harsher
            if "harsher" in comment.body.lower() and ("wit" in comment.parent().body.lower() or "insult" in comment.parent().body.lower()) and str(comment.subreddit.display_name).lower() == "cremposting" and len(comment.body) < 20:
                comment.reply(random.choice(insult_quotes) + "\n\n^(Harsher insult!)") #Chooses a random quote from above list
                comment.mark_read()

                print("Harsher insult!")

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

    #Mentions
        for mention in r.inbox.mentions(limit=3):
            if mention.new:
                mention.reply(random.choice(lopen_quotes))

                comments_replied_to2.append(mention.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(mention.id + "\n")

                mention.mark_read()


    #Main code
    if count:
        n = 20
    else:
        n = 200

    for comment in r.subreddit('Cremposting').comments(limit = n):
        comment.refresh()
        #Randomness to make sure Lopen doesn't reply to every comment with these words

        pancake_num = random.randint(1, 4)
        gancho_num = random.randint(1, 3)
        x_com = comment
        y_com = comment

        if str(comment.author).lower() not in ["b0trank"]:

        #Spoiler
            for key in ["!>", "<!", ">! "]:
                if comment.id not in mod_comments:
                    if key in comment.body and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                        if key in ["!>", "<!"] and (comment.body.count(key) != comment.body.count('>!>!') or comment.body.count(key) != comment.body.count('!<!<')):
                            extra = f"You have used {key} by mistake, which is wrong. Use \>!(Text here)\!< instead for correct spoiler tags!"
                        elif key == ">! " and "\\>!" not in comment.body:
                            extra = f"There is a space between your spoiler tag and text! Remove it to fix the spoiler!"
                        else:
                            extra = ""

                        if extra:
                            disclaimer = "\n\n^(If you are explaining the correct usage of tags, type \\\!< and \\\>! so I don't get confused. Alternatively, use > ! and ! < for explanations.)"

                            comment.reply(extra + disclaimer) #Chooses a random quote from above list

                            comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                            print("Untagged spoiler found!")

                            my_comment = [comment for comment in r.user.me().comments.new(limit = 1)][0]
                            my_comment.mod.distinguish()

                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                            mod_comments.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                            with open("mod_comments.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                elif key in comment.body and comment.id not in removed_comments and r.user.me().is_mod and int(time.time() - comment.created_utc)/60 > 10:

                    if (key in ["!>", "<!"] and (comment.body.count(key) != comment.body.count('>!>!') or comment.body.count(key) != comment.body.count('!<!<'))) or (key == ">! " and "\\>!" not in comment.body):
                        extra = ""
                        for my_comment in list(comment.replies):
                            if my_comment.author == r.user.me() and 'spoiler tag' in my_comment.body.lower():
                                extra = my_comment.body
                                my_comment.delete()

                        comment.reply(f"Hey gon, this comment has been removed due to bad spoiler tags. {extra} Edit your original comment for it to be reinstated, or repost it with fixed tags.\n\n^(This action was performed automatically. If you think this was done incorrectly, contact u/(Whatever storming username AlThorStormblessed is using).)")
                        comment.mod.remove()

                        print("Comment removed")

                        my_comment = [comment for comment in r.user.me().comments.new(limit = 1)][0]
                        my_comment.mod.distinguish()

                        removed_comments.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                        with open("removed_comments.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

            for key in [">!", "!<"]:
                if comment.id not in mod_comments:
                    for element in comment.body.split("\n\n"):
                        if key in element and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                            if key == ">!":
                                thing = "!<"
                            else:
                                thing = ">!"

                            if element.count(key) == element.count(thing):
                                pass
                            else:
                                if element.count(key) > element.count(thing):
                                    tag = thing
                                else:
                                    tag = key

                                disclaimer = "\n\n^(If you are explaining the correct usage of tags, type \\\!< and \\\>! so I don't get confused. Alternatively, use > ! and ! < for explanations.)"

                                comment.reply(f"You are missing at least one {tag} in that comment (spoiler tags do not work across paragraphs, so make sure to check for that as well)! Fix it so others don't get spoiled!" + disclaimer)

                                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                                print("Untagged spoiler found!")

                                my_comment = [comment for comment in r.user.me().comments.new(limit = 1)][0]
                                my_comment.mod.distinguish()

                                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                    f.write(comment.id + "\n")

                                mod_comments.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                                with open("mod_comments.txt", "a", encoding='cp1252') as f:
                                    f.write(comment.id + "\n")

                                break

                else:
                    for element in comment.body.split("\n\n"):
                        if key in element and comment.id not in removed_comments and r.user.me().is_mod and int(time.time() - comment.created_utc)/60 > 10:
                            if key == ">!":
                                thing = "!<"
                            else:
                                thing = ">!"

                            if element.count(key) == element.count(thing):
                                pass
                            else:
                                for my_comment in list(comment.replies):
                                    if my_comment.author == r.user.me() and 'spoiler tag' in my_comment.body.lower():
                                        extra = my_comment.body
                                        my_comment.delete()

                                comment.reply(f"Hey gon, this comment has been removed due to bad spoiler tags. {extra} Edit your original comment for it to be reinstated, or repost it with fixed tags.\n\n^(This action was performed automatically. If you think this was done incorrectly, contact u/(Whatever storming username AlThorStormblessed is using).)")
                                comment.mod.remove()

                                my_comment = [comment for comment in r.user.me().comments.new(limit = 1)][0]
                                my_comment.mod.distinguish()

                                print("Comment removed")

                                removed_comments.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                                with open("removed_comments.txt", "a", encoding='cp1252') as f:
                                    f.write(comment.id + "\n")

                                break

            if(comment.id in comments_replied_to2 or comment.author == r.user.me()):
                continue


    #Lopen messaging service
            LMS = []
            keys = [
                "!kaladin", "!shallan", "!adolin", "!stormfather", "!stormdaddy", "!taln", "!syl", "!pattern",
                "!stick", "!dalinar", "!dadinar", "!rock", "!numuhukumakiaki'aialunamor", "!jasnah", "!nightblood"
            ]

            # Dictionary to map keys to their corresponding quotes and messages
            responses = {
                "!kaladin": kaladin_quotes,
                "!shallan": shallan_quotes,
                "!adolin": adolin_quotes,
                "!stormfather": stormfather_quotes,
                "!stormdaddy": stormfather_quotes,
                "!taln": taln_quotes,
                "!syl": syl_quotes,
                "!pattern": pattern_quotes,
                "!stick": ["I am a stick."],
                "!dalinar": dalinar_quotes,
                "!dadinar": dalinar_quotes,
                "!rock": rock_quotes,
                "!numuhukumakiaki'aialunamor": rock_quotes,
                "!jasnah": jasnah_quotes,
                "!nightblood": nightblood_quotes
            }

            messages = {
                "!kaladin": "\n\n^(These words of Kaladin's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!shallan": "\n\n^(These words of Shallan's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!adolin": "\n\n^(These words of Adolin's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!stormfather": "\n\n^(These words of Stormfather's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!stormdaddy": "\n\n^(These words of Stormfather's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!taln": "\n\n^(These words of Taln's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!syl": "\n\n^(These words of Syl's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!pattern": "\n\n^(These words of Pattern's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!stick": "\n\n^(These words of Stick's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!dalinar": "\n\n^(These words of Dalinar's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!dadinar": "\n\n^(These words of Dalinar's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!rock": "\n\n^(These words of Rock's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!numuhukumakiaki'aialunamor": "\n\n^(These words of Rock's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!jasnah": "\n\n^(These words of Jasnah's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "!nightblood": "\n\n^(These words of Nightblood's were brought by the Lopen Messaging Service, by the cousins, for the cousins)"
            }

            for key in keys:
                if key in comment.body.lower() and ('>' + key) not in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    LMS.append(key)

            if LMS:
                lms_key = random.choice(LMS)
                mess = random.choice([
                    messages[lms_key],
                    "\n\n^(-{}, brought by Lopen's cousins)".format(lms_key.capitalize()),
                    "\n\n^(Speak further to {} by mentioning {} in your comments. Anytime, anywhere. LMS)".format(lms_key.capitalize(), lms_key)
                ])

                list_of = "\n\n^(Use !list in your comments to view entire list LMS characters!)"

                comment.reply(random.choice(responses[lms_key]) + mess + list_of)

                comments_replied_to2.append(comment.id)
                print("LMS service used!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

            if "!list" in comment.body.lower()  and comment.body.lower().count("!list") > comment.body.lower().count(">!list") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                list_of = "Hey, Gancho, these are the people whom you can communicate with through the Lopen Messaging Service as of now!\n\
\n\
* Kaladin\n\
\n\
* Shallan\n\
\n\
* Adolin\n\
\n\
* Stormfather/Stormdaddy (coz why not?)\n\
\n\
* Taln\n\
\n\
* Syl\n\
\n\
* Pattern\n\
\n\
* Dalinar/Dadinar\n\
\n\
* Stick\n\
\n\
* Rock/Numuhukumakiaki'aialunamor\n\
\n\
* Jasnah (no, she isn't going to crush you with her thighs)\n\
\n\
* Wit (summoned as either ! Wit (quote to commentor) or ! Wit [...] insult (insult parent commentor)\n\
\n\
* Nightblood"

                comment.reply(list_of)

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                print("Comment found!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

            if "!function" in comment.body.lower()  and comment.body.lower().count("!function") > comment.body.lower().count(">!function") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                comment.reply(functions)

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                print("Comment found!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

        #Witty stuff
            if "!wit" in comment.body.lower() and ">!wit" not in comment.body.lower() and comment.id not in comments_replied_to2:
                #Quotes
                if not WholeWord("insult")(comment.body) and comment.author != r.user.me():

                    mess = random.choice(["\n\n^(These words of Wit's was brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                        "\n\n^(-Wit, brought by Lopen's cousins)",
                        "\n\n^(Speak further to Wit by mentioning ! Wit in your comments. Anytime, anywhere. LMS)"])

                    list_of = "\n\n^(Use !list in your comments to view entire list LMS characters!)"

                    comment.reply(random.choice(wit_quotes) + mess + list_of)

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                    print("Wit replied!")

                else:
                    if WholeWord("lopen")(comment.body):
                        insult_num = random.randint(1, 2)

                    else:
                        insult_num = 1

                    if insult_num == 1:
                        post = True

                        if vorin["Name"].str.contains(str(comment.author)).any():
                            if rank(comment.author) != "Heretic":
                                post = False

                                Vorin = [
                                    "You dare try to insult a child of the Almighty? Shame!",
                                    "This cr*mposter is protected by the Great Vorin Church. You may not insult them!",
                                    f"Do you not recognise {rank(comment.parent().author)} {comment.parent().author}? You shall insult them?"
                                ]

                                comment.reply(random.choice(Vorin)) #Chooses a random quote from above list

                                comments_replied_to2.append(comment.id)
                                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                    f.write(comment.id + "\n")

                        if post:
                            fail_or_insult = random.randint(1, 5)

                            wit_insult = [
"The sum total of stupid people is somewhere around the population of the planet. Plus one. You count twice.",
"I would never call you an imbecile, because then I would have to explain what that is, and I doubt any of us have the requisite time.",
f"You see, {comment.parent().author}, you make it too easy. An uneducated, half-brained serving boy with a hangover could make mock of you. I am left with no need to exert myself, and your very nature makes mockery of my mockery. And so it is that through sheer stupidity you make me look incompetent.",
"I needed an objective frame of reference by which to judge the experience of your company. Somewhere between four and five blows, I place it.",
f"{comment.parent().author}, I salute you. You are what lesser cretins like (Whatever storming username AlThorStormblessed is using) aspire to be.",
f"I point out truths when I see them, {comment.parent().author}. Each man has his place. Mine is to make insults. Yours is to be in-sluts.",
"So, dear sir, when I say that you are the very embodiment of repulsiveness, I am merely looking to improve my art.",
"You look so ugly, it seems that someone tried — and failed — to get the warts off your face through aggressive application of sandpaper.",
"You are less a human being, and more a lump of dung with aspirations. If someone took a stick and beat you repeatedly, it could only serve to improve your features.",
"Your face defies description, but only because it nauseated all the poets. You are what parents use to frighten children into obedience.",
"I’d tell you to put a sack over your head, but think of the poor sack!",
"Theologians use you as proof that God exists, because such hideousness can only be intentional.",
f"Ahh {comment.parent().author}! You remind me of someone very dear to me. My horse.",
"You storming personification of a cancerous anal discharge.",
                            ]

                            mess = random.choice(["\n\n^(This insult of Wit's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                                "\n\n^(-Wit, brought by Lopen's cousins)",
                                "\n\n^(Speak further to Wit by mentioning ! Wit in your comments. Anytime, anywhere. LMS)"])

                            list_of = "\n\n^(Use !list in your comments to view entire list LMS characters!)"

                            if fail_or_insult == 1:
                                comment.reply(random.choice(wit_fail) + "\n\n" + random.choice(wit_insult).replace('comment.parent().author', 'comment.author') + mess + list_of)

                            else:
                                if comment.parent().id not in comments_replied_to2:
                                    comment.parent().reply(random.choice(wit_insult).replace('x_com', 'comment.parent().author') + mess + list_of) #Chooses a random quote from above list
                                    comments_replied_to2.append(comment.parent().id)

                                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                        f.write(comment.parent().id + "\n")

                                    print("Comment insulted!")

                                else:
                                    comment.reply(random.choice(wit_fail_2) + mess + list_of) #Chooses a random quote from above list

                comments_replied_to2.append(comment.id)

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")


            if "!shart" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                try:
                    sent_list = comment.parent().body.split()
                except:
                    sent_list = comment.parent().title.split()

                for word in range(len(sent_list)):
                    num = random.randint(1, 4)
                    if num == 2:
                        word2 = sent_list[word].replace(">!", "").replace("!<", "")
                        sent_list[word] = sent_list[word].replace(word2, "shart")

                if sent_list.count('shart') == 0:
                    sent_list[random.randint(0, len(sent_list))] = 'shart'

                comment.reply("Shartified:\n\n" + ' '.join(sent_list) + extra)
                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                print("Sentence sharted!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

            if "!spook" in comment.body.lower() and comment.body.lower().count("!spook") > comment.body.lower().count(">!spook") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():

                text = comment.parent().body
                if len(text) < 400:
                    new_text = []
                    for word in text.split():
                        if word.lower() in ["you'd", "i'd", "we'd", "she'd", "he'd", "it'd", "they'd", "there's", "it's", "it'll", "there'll", "you're", "you'll", "he'll", "he's", "she'll", "she's", "they'll", "they're", "we'll", "we're", "i've", "i'll", "i'm", "they've", "we've", "you've", "what's", "what'll"]:
                            new_text.append(word[:-2])
                            word = 'is'
                        if word.lower() in 'was am is were are will shall has have should would could'.split():
                            if 'Wasing' not in new_text:
                                new_text = ["Wasing"] + new_text
                        elif word.lower()[-2:] == 'ed':
                            new_text.append(word[:-2] + 'ing of')
                        elif word.lower()[-3:] == 'ing':
                            new_text.append(word + ' of')
                        elif word.lower() in ["you're", "i'm", 'myself', 'yourself', 'himself', 'herself', 'itself', 'themselves', 'yourselves', 'ourselves', 'he', 'she', 'i', 'you', 'they', 'me', 'you', 'her', ' him', 'it', 'them', 'us', ' hers', 'his', 'mine', 'yours', 'its', 'ours', 'theirs', 'whom', 'that', 'who', 'which', 'all', 'any', 'anybody', 'everybody', 'everyone', 'another', 'this', 'that', 'these', 'those', 'who', 'which', 'what', 'myself', 'yourself', 'himself', 'herself', 'itself', 'themselves', 'yourselves', 'ourselves']:
                            pass
                    ##    elif word.lower() in []:
                    ##        pass
                        elif word.lower() in [word2 for synset in wn.all_synsets('v') for word2 in synset.lemma_names() if '_' not in word]:
                            if word.lower()[-1] == 'e' and word.lower() not in ['be', "die", "lie"]:
                                new_text.append(word[:-1] + 'ing of')
                            else:
                                new_text.append(word + 'ing of')

                        else:
                            new_text.append(word)
                        try:
                            if set(['.', '?', '!']).intersection(new_text[-2]):
                                new_text[-1] = new_text[-1].capitalize()
                        except:
                            pass

                    new_text[0] = new_text[0].capitalize()
                    new_text = ' '.join(new_text).replace('of of', 'of')

                    comment.reply(new_text)
                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                    print("Sentence spookified!")

                else:
                    comment.reply("That comment is too long for me, hehehe. Tryy again?")
                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                    print("Sentence not spookified!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

            if "!swear" in comment.body.lower() and comment.body.lower().count("!swear") > comment.body.lower().count(">!swear") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():

                user = comment.parent().author
                com_list = [comment.body.lower() for comment in user.comments.new(limit = None)]
                comments = " ".join(com_list)

                num = 0
                for swear in ["storms", "safehand", "femboy", "rusts", "rust and ruin", "merciful domi", "syladin",
                        "storming", "shat", "ashes", "starvin", "ash's eyes", "airsick", "nale's nut", "taln's stones",
                        "by the survivor", "kelek's breath", "god beyond", "chull dung", "crem", "colors"]:
                    num += comments.count(swear)

                text = f"In OP's last {len(com_list)} comments, there were {num} Cosmere swear words used."

                comment.reply(text)
                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                print("Swears counted!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")


        #Vorin Church
            if "!join" in comment.body.lower() and comment.body.lower().count("!join") > comment.body.lower().count(">!join") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                radiant = False

                if set(["cremrunner", "shartweaver", "memecaller", "hiighbreaker", "willyshaper", "rafowatcher", "edgydancer", "mudflinger", "stonedward", "cumbringer"]).intersection(comment.body.lower()):
                    comment.reply("!join is function to join the Great Vorin Church. If you want to join a Crem-Order, simply type !(Order name), for eg, !cremrunner. Else, if you want to join the Church, remove the Order name from your above comment and make another attempt.")
                    comments_replied_to2.append(comment.id)

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                else:

                    post = True
                    heretic = False
                    if vorin["Name"].str.contains(str(comment.author)).any() and vorin[vorin["Name"] == str(comment.author)]["Points"].any() < -100:
                        heretic = True
                        comment.reply(f"Heretic {comment.author} must *not* be allowed into the Holy Vorin Church!")
                        comments_replied_to2.append(comment.id)

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Heretic found!")

                        post = False

                        break


                    elif vorin["Name"].str.contains(str(comment.author)).any():
                        comment.reply(f"{rank(comment.author)} {comment.author} has already been inducted into the Holy Vorin Church!")
                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Devotee found!")

                        post = False
                        break


                    if post and comment.id not in comments_replied_to2:
                        comment.reply(f"Devotee {comment.author} has joined the Great Vorin Church! Your rank has been assigned as Darkborn!\n\n\
^(We have a strict set of guidelines, which, if not followed, will lead to permanent excommunication from the Vorin Church. Type !guide to read the rules!)\n\n\
^(To find the many different niceties the Vorin Church beings, type out !pros in your comments. We have many nice features!)")
                        comments_replied_to2.append(comment.id)

                        vorin = vorin.append({"Name" : str(comment.author), "Points" : 0}, ignore_index=True)

                        vorin.to_csv("Vorin.csv", index = False)
                        vorin = pd.read_csv("Vorin.csv", usecols = ["Name", "Points"])

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("New member saved")

            if vorin["Name"].str.contains(str(comment.author)).any():
                curr_rank = rank(comment.author)
                points = 0
                for key in ["storms", "safehand", "femboy", "rusts", "rust and ruin", "merciful domi", "syladin",
                            "storming", "shat", "ashes", "starvin", "ash's eyes", "airsick", "nale's nut", "taln's stones",
                            "by the survivor", "kelek's breath", "god beyond", "chull dung", "crem", "colors", "almighty is dead"]:
                    if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                        points -= 25

                for key in ["almighty", "herald", "vorin"]:
                    if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                        points += 100

                if WholeWord("jasnah")(comment.body) and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                    points -= 300

                points = vorin["Points"][vorin.index[vorin['Name'] == comment.author]] + points
                vorin["Points"][vorin.index[vorin['Name'] == comment.author]] = points
                vorin.to_csv("Vorin.csv", index = False)
                vorin = pd.read_csv("Vorin.csv", usecols = ["Name", "Points"])

                comments_skimmed.append(comment.id)
                with open("comments_skimmed.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

                if curr_rank != rank(comment.author) and rank(comment.author) != "Heretic":
                    comment.reply(f"Due to recent activities, your Vorin rank has changed from **{curr_rank} to {rank(comment.author)}**")
                    comments_replied_to2.append(comment.id)
                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Heretic found!")

                elif curr_rank != rank(comment.author) and rank(comment.author) == "Heretic":
                    comment.reply(f"Due to recent activities, you have been ***excommunicated*** from the Great Vorin Church. Never show your heretic face here again!")
                    comments_replied_to2.append(comment.id)
                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Heretic found!")

                if "!hail" in comment.body.lower() and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                    if rank(comment.author) != "Heretic" and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed:
                        if rank(comment.author) in ["Holy Emperor", "Herald"]:
                            comment.reply(f"All hail the glory of the Almighty, the {rank(comment.author)} of Stormlight, {comment.author}!")
                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                        else:
                            comment.reply("Who are you again??")
                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                        print("Herald hailed!")

                if "!guide" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    if rank(comment.author) != "Heretic":
                        comment.reply(f"Ah, {rank(comment.author)} {comment.author}. You wish to seek our guidelines! Here they are:\n\n\
1. The Great Vorin Church does not permit the use of any swear words, except the name of the Almighty and the Great Heralds. Swearing shall result in reduction in rating and possible reduction in rank, even excommunication.\n\n\
2. Any defiling of Herald names, as and when we detect it, shall result in excommunication.\n\n\
3. No man shall dare read or write on this subreddit. Only through female scribes or ardents shall written word be transmitted (we are working on figuring out how to catch such heretics.)\n\n\
4. Censor the name of J\*snah Kh\*lin, or use a title. Such heretics must not be tolerated. This will result in reduction in rating and possible reduction in rank, even excommunication..\n\n\
5. For more information about ranking, type !rank.")
                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Guidelines!")

                for key in ["!cat", "!dog", "!cow", "!crab"]:
                    if key in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                        if rank(comment.author) != "Heretic":
                            if (rank(comment.author) in ["Brightness", "High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) != 2) or rank(comment.author) == "Lighteyes":
                                if key == "!cat":
                                    animal_image = random.choice(cat)
                                elif key == "!dog":
                                    animal_image = random.choice(dog)
                                elif key == "!cow":
                                    animal_image = random.choice(cow)
                                elif key == "!crab":
                                    animal_image = random.choice(crab)
                                intro = random.choice(intro_list)
                                comment.reply(f"[{intro}]({animal_image})")

                            elif rank(comment.author) in ["Brightness", "High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) == 2:
                                author = comment.body.split()[1]
                                comment = y_com
                                print(author)
                                try:
                                    for comment_other in r.redditor(author).comments.new(limit = None):
                                        if author.lower() != "mistborn" and comment_other.subreddit.display_name.lower() == "cremposting" and comment_other.id not in comments_replied_to2:
                                            if key == "!cat":
                                                animal_image = random.choice(cat)
                                            elif key == "!dog":
                                                animal_image = random.choice(dog)
                                            elif key == "!cow":
                                                animal_image = random.choice(cow)

                                            elif key == "!crab":
                                                animal_image = random.choice(crab)

                                            intro_list_2 = [
f"Here is a really cute image {comment.author} found for you!",
f"{comment.author} sends you this really nice image!",
f"Here is something really cute {comment.author} has sent you!!!",
f"{comment.author} thinks that you should look atcomment.author this little thing!"
]
                                            intro = random.choice(intro_list_2)
                                            comment_other.reply(f"[{intro}]({animal_image})")
                                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                                f.write(comment_other.id + "\n")
                                            comment.reply("The image has been sent!")
                                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                                f.write(comment.id + "\n")

                                        elif author.lower() == "mistborn":
                                            comment.reply(f"We daren't disturb the Almighty, {comment.author}, even for cute images like such.")

                                    else:
                                        if comment.id not in comments_replied_to2:
                                            comment.reply("No recent eligible comment found. Try someone else instead, or wait for them to make a new comment.")
                                except:
                                    comment.reply("Image delivery has failed, O Bright One.")

                            else:
                                comment.reply("You are too lowly ranked to use this function. Be a good Vorin, follow the guidelines and praise the Almighty and the Heralds, and perhaps we will grant you this power!")

                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                            print("Cute image sent!")

                        else:
                            comment.reply("You are a Heretic! No priveleges for you, unless you repent!")

                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                            print("Heretic found!")

                if "!rickroll" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    if rank(comment.author) != "Heretic":
                        if (rank(comment.author) in ["High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) != 2):
                            comment.reply("O Bright One, you need to type just '!rickroll [username]' without the u/. Anything else will just confuse us.")
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                        elif rank(comment.author) in ["High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) == 2:
                            author = comment.body.split()[1]
                            comment = y_com
                            try:
                                for comment_other in r.redditor(author).comments.new(limit = None):
                                    if author.lower() != "mistborn" and comment_other.subreddit.display_name.lower() == "cremposting" and comment_other.id not in comments_replied_to2:

                                        link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

                                        intro_list_2 = [
f"Here is a really cute image {comment.author} found for you!",
f"{comment.author} sends you this really nice image!",
f"Here is something really cute {comment.author} has sent you!!!",
f"{comment.author} thinks that you should look atcomment.author this little thing!"
]
                                        intro = random.choice(intro_list_2)

                                        comment_other.reply(f"[{intro}]({link})")
                                        comments_replied_to2.append(comment_other)
                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment_other.id + "\n")
                                        comment.reply("The 'image' has been sent!")
                                        comments_replied_to2.append(comment)
                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment.id + "\n")

                                    elif author.lower() == "mistborn":
                                        comment.reply(f"You really want to rickroll Brandon Sanderson? The Almighty shall not be disturbed!")

                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment.id + "\n")
                                else:
                                    if comment.id not in comments_replied_to2:
                                        comment.reply("No recent eligible comment found. Try someone else instead, or wait for them to make a new comment.")
                            except:
                                comment.reply("Function has failed, O Bright One.")

                        elif comment.id not in comments_replied_to2:
                            comment.reply("You are too lowly ranked to use this function. Be a good Vorin, follow the guidelines and praise the Almighty and the Heralds, and perhaps we will grant you this power!")

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Rickroll sent!")

                    else:
                        comment.reply("You are a Heretic! No priveleges for you, unless you repent!")

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Heretic found!")


            if "!rank" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic":
                        comment.reply(f"The Vorin ranking system is very complex. Devotees gain higher ranks by being good Vorins, and fall in rankings by breaking guidelines. Steep falls can result in excommunication, at least till such behavious is rectified, in which case they may re-join.\n\n\
Your rank for now is ***{rank(comment.author)}*** \n\n\
The ranking is as follows:\n\n\
1. Herald: Everything Holy Emperors have\n\n\
2. Holy Emperor: Everything High-nobles have, ability to !hail themselves for all to recognise.\n\n\
3. High-noble: Everything the Bright-lords and -ladies have, ability to send insults to anyone of properly low rank, ability to !rickroll anyone on the sub.\n\n\
4. Brightness: Everything the lower Lighteyes have, protection from all insults, including Vorin insults, ability to send below images to anyone.\n\n\
5. Lighteyes: Everything the Darkborn have, ability to summon !dog, !cat, !crab, and !cow images, for the days you are worse for wear.\n\n\
6. Darkborn: Protected from Lopen and Wit insults, gain access to !Vorin insults and !Vorin compliments\n\n\
7. Heretics: removed from the Church, no priveleges.\n\n\
Powers may not have been unlocked yet, if something doesn't work as expected, please bear patience.")

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Guidelines!")

                    else:
                        comment.reply(f"You are a st*rming heretic!")
                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                else:
                    comment.reply("You are not part of the Vorin Church. Type '!join' to be welcomed by us and praise the Almighty!")
                    comments_replied_to2.append(comment.id)
                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

            if "!pros" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic":
                        comment.reply(f"Ah, {rank(comment.author)}  {comment.author}. The features of the Vorin Church are many! There they are:\n\n\
1. No one may insult you, neither the fool Wit, nor the one-armed Herdazian. You will be safe from insults from all but the Church itself.\n\n\
2. You have unlocked the Great Vorin Insult. Type !vorinsult to any heretic or Vorin, and we shall insult them with special, holy insults.\n\n\
3. You can gain or lose rank by praying by the Almighty's name, or by breaking the guidelines respectively. You can reach dizzying heights in the Vorin Church!\n\n\
4. Many new functions shall be granted as you rise in rank!")
                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Advantages!")

            if "!pros" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic":
                        comment.reply(f"St*rm you. There are no st*rming cons to the Great Vorin Church, so stop asking.")
                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Advantages!")

            if ("!vorinsult" in comment.body.lower() or "!vorin insult" in comment.body.lower()) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                post = True
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic" and rank(comment.parent().author) not in ["Brightness", "High-noble", "Holy Emperor", "Herald"]:
                        post = False
                        parent = comment.parent()

                        if parent.id not in comments_replied_to2:
                            extra = f"\n\n ^(This insult was requested by Devotee {comment.author})"
                            parent.reply(random.choice(vorin_insult_quotes) + extra) #Chooses a random quote from above list
                            comments_replied_to2.append(parent.id)
                            print("Comment insulted!")

                            comment.reply(random.choice(vorin_success_quotes)) #Chooses a random quote from above list

                        else:
                            comment.reply(random.choice(vorin_fail_quotes)) #Chooses a random quote from above list

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                    elif rank(comment.author) != "Heretic":
                        high_quotes = [
                            f"{comment.parent().author} is too highly ranked for even us to insult. You can, however, compliment them.",
                            f"You dare try to insult {rank(comment.parent().author)} {comment.parent().author}?",
                            f"Pray, for the insult has not reached them!",
                            f"St*rm off, {comment.author}. We won't insult such a distinguished member of our Church."
                        ]

                        comment.reply(random.choice(high_quotes)) #Chooses a random quote from above list

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")
                        post = False

                if post and comment.id not in comments_replied_to2:
                    comment.reply("Only the members of the Great Vorin Church can use this feature. If you are not a heretic, type !join to be welcomed by us!")
                    comments_replied_to2.append(comment.id)
                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

            if ("!vorin compliment" in comment.body.lower() or "!praise" in comment.body.lower()) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                post = True
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic":
                        post = False

                        parent = comment.parent()

                        if parent.id not in comments_replied_to2:
                            extra = f"\n\n ^(This compliment was requested by Devotee {comment.author})"
                            parent.reply(random.choice(vorin_compliment_quotes) + extra) #Chooses a random quote from above list
                            comments_replied_to2.append(parent.id)
                            print("Comment complimented!")

                            comment.reply(random.choice(vorin_success_quotes_2)) #Chooses a random quote from above list

                        else:
                            comment.reply(random.choice(vorin_fail_quotes_2)) #Chooses a random quote from above list

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                if post:
                    comment.reply("Only the members of the Great Vorin Church can use this feature. If you are not a heretic, type !join to be welcomed by us!")
                    comments_replied_to2.append(comment.id)
                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

            if "!insult" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                if vorin["Name"].str.contains(str(comment.author)).any():
                    if rank(comment.author) != "Heretic":
                        if (rank(comment.author) in ["High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) != 2):
                            comment.reply("O Bright One, you need to type just '!insult [username]' without the u/. Anything else will just confuse us.")
                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                        elif rank(comment.author) in ["High-noble", "Holy Emperor", "Herald"] and len(comment.body.split()) == 2:
                            author = comment.body.split()[1]
                            try:
                                for comment_other in r.redditor(author).comments.new(limit = 15):
                                    if author.lower() != "mistborn" and comment_other.subreddit.display_name.lower() == "cremposting" and comment_other.id not in comments_replied_to2:

                                        extra = f"\n\n ^(This insult was requested by {comment.author})"
                                        comment_other.reply(random.choice(vorin_insult_send) + extra)
                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment_other.id + "\n")
                                        comment.reply("The insult has been sent!")
                                        comments_replied_to2.append(comment.id)
                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment.id + "\n")

                                    elif author.lower() == "mistborn":
                                        comment.reply(f"You really want to insult Brandon Sanderson? The Almighty shall not be disturbed!")
                                        comments_replied_to2.append(comment.id)
                                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                            f.write(comment.id + "\n")

                                else:
                                    if comment.id not in comments_replied_to2:
                                        comment.reply("No recent eligible comment found. Try someone else instead, or wait for them to make a new comment.")
                            except:
                                comment.reply("Insult has failed, O Bright One.")

                        elif comment.id not in comments_replied_to2:
                            comment.reply("You are too lowly ranked to use this function. Be a good Vorin, follow the guidelines and praise the Almighty and the Heralds, and perhaps we will grant you this power!")

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Distance insult sent!")

                    else:
                        comment.reply("You are a Heretic! No priveleges for you, unless you repent!")
                        comments_replied_to2.append(comment.id)

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Heretic found!")

        #Lopen joke
            for key in ["lopen joke", "lopen jokes", "one armed herdazian", "one-armed herdazian", "one-armed-herdazian", "one armed herdaz", "one-armed-herdaz"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():

                    comment.reply(random.choice(lopen_joke_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")


                    print("Comment found!")

                    break

        #Lopen insult
            for key in ["insult", "insults"]:
                if WholeWord(key)(comment.body) and (WholeWord("lopen")(comment.body) or WholeWord("gancho")(comment.body)) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    post = True
                    if vorin["Name"].str.contains(str(comment.author)).any():
                        if rank(comment.author) != "Heretic":
                            post = False

                            Vorin = [
                                "You dare try to insult a child of the Almighty? Shame!",
                                "This cr*mposter is protected by the Great Vorin Church. You may not insult them!",
                                f"Do you not recognise Devotee {comment.parent().author}? You shall insult them!"
                            ]

                            comment.reply(random.choice(Vorin)) #Chooses a random quote from above list

                            comments_replied_to2.append(comment.id)
                            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                                f.write(comment.id + "\n")

                            print("Comment not insulted")

                    if post:

                        parent = comment.parent()

                        if parent.id not in comments_replied_to2:
                            extra = f"\n\n ^(This insult was requested by {comment.author})"
                            parent.reply(random.choice(insult_quotes) + extra) #Chooses a random quote from above list
                            comments_replied_to2.append(parent.id)
                            print("Comment insulted!")

                            comment.reply(random.choice(success_quotes)) #Chooses a random quote from above list

                        else:
                            comment.reply(random.choice(fail_quotes)) #Chooses a random quote from above list
                            pass

                        comments_replied_to2.append(comment.id)
                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

        #Lopen compliment
            if WholeWord("compliment")(comment.body) and (WholeWord("lopen")(comment.body) or WholeWord("gancho")(comment.body)) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():

                parent = comment.parent()

                if "compliment me" not in comment.body.lower():
                    if parent.id not in comments_replied_to2:
                        extra = f"\n\n ^(This compliment was requested by {comment.author})"
                        parent.reply(random.choice(compliment_quotes) + extra) #Chooses a random quote from above list
                        comments_replied_to2.append(parent.id)
                        print("Comment complimented!")

                        comment.reply(random.choice(comp_success_quotes)) #Chooses a random quote from above list

                    else:
                        comment.reply(random.choice(comp_fail_quotes)) #Chooses a random quote from above list
                        pass

                else:
                    extra = f"\n\n ^(Hope you feel nice, {comment.author}!)"
                    comment.reply(random.choice(compliment_quotes) + extra)
                    print("Comment complimented!")


                comments_replied_to2.append(comment.id)

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

        #gancho
            for key in ["gancho", "moolie", "gon", "penhito", r.user.me(), "the lopen", "ganchos"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    try:
                        result = sentiment_analysis(quote)[0]
                        sentiment = result['label']

                        if sentiment == "POSITIVE":
                            comment.reply(random.choice(lopen_pos_quotes))
                        else:
                            comment.reply(random.choice(lopen_neg_quotes))
                             #Chooses a random quote from above list
                    except:
                        comment.reply(random.choice(lopen_quotes))

                    finally:
                        comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                        print("Comment found!")

                        break

        #Stick
            if "you could be fire" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                stick_quotes = [
                        "I am a stick."
                     ]

                mess = random.choice(["\n\n^(These words of Stick's were brought by the Lopen Messaging Service, by the cousins, for the cousins)",
                "\n\n^(-Stick, brought by Lopen's cousins)",
                "\n\n^(Speak further to Stick by mentioning !Stick in your comments. Anytime, anywhere. LMS)"])

                list_of = "\n\n^(Use !list in your comments to view entire list LMS characters!)"

                comment.reply(random.choice(stick_quotes) + mess + list_of) #Chooses a random quote from above list

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

                print("Comment found!")

        #Correction
            for key in ["lopen", "Lopen"]:
                if key in comment.body  and not "the lopen" in comment.body.lower().replace("*", "") and not "thelopen" in comment.body.lower() and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me() and gancho_num == 2:
                    correction_quotes = [
                        "That would be *The Lopen* for you, moolie!",
                        f"How dare you disrespect The Lopen, King of Alethkar, by merely calling him '{key}'?",
                        f"{key}? Just {key}? Here, I am giving you the Lopen gesture!"
                    ]
                    comment.reply(random.choice(correction_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Comment found!")

                    break

        #cousin
            for key in ["cousin", "cousins"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                    cousin_quotes = [
                        "You can never have enough cousins, gon!",
                        "A man can never have enough cousins!",
                        "My cousin's never failed me.",
                        "You bother one of us, you bother us all!"
                    ]
                    comment.reply(random.choice(cousin_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Comment found!")

                    break

        #pancakes-2
            for key in ["pancake", "pancakes"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and comment.id not in comments_skimmed and not comment.author == r.user.me():
                    pan2cakes_quotes = [
                        "Yeah, pancakes are alright, but have you tasted chouta?",
                        "Gon, pancakes are not *that* great! Have some chouta!",
                        "Chouta before pancakes, gon!"
                    ]
                    comment.reply(random.choice(pan2cakes_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Comment found!")

                    break

        #chouta
            for key in ["chouta"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_skimmed and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    chouta_quotes = [
                        "Chouta. Herdazian food, gon. Good stuff.",
                        "Chouta is love. Chouta is life.",
                        "Chouta are the best thing you can ever have, gon!",
                        "Journey before Chouta, gancho!",
                        "Penhito, the only acceptable use of chouta in a sentence is to praise it!"
                    ]
                    comment.reply(random.choice(chouta_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

                    print("Comment found!")

        #Rua
            for key in ["rua"]:
                if WholeWord(key)(comment.body) and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                    rua_quotes = [
                        "***Lopen Gesture***"
                    ]
                    comment.reply(random.choice(rua_quotes)) #Chooses a random quote from above list

                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")


                    print("Comment found!")

        #Sazed, I think
            if ", i think." in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
                sazed_quotes = [
                    "Hey, gon, is this you Sazed?",
                    "Saze gancho! Good to see you here!",
                    "Wow, my gon Sazed is here!"
                ]

                comment.reply(">, I think. \n\n" + random.choice(sazed_quotes)) #Chooses a random quote from above list

                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

                print("Sazed found!")

            if comment.id not in comments_skimmed and not comment.author == r.user.me():
                comments_skimmed.append(comment.id) #Adds skimmed comments to list
                with open("comments_skimmed.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

    for comment in r.subreddit("Cremposting+Stormlight_Archive+Cosmere+Mistborn+brandonsanderson+Lopen_bot_test+OkGanchoLowlander").comments(limit = min([n*4, 500])):
        if(comment.id in comments_replied_to2 or comment.author == r.user.me()):
            continue

        comment.refresh()
        #Coppermind function
        if "!coppermind" in comment.body.lower() and comment.body.lower().count("!coppermind") > comment.body.lower().count(">!coppermind") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
            text = comment.body.lower()
            text = text.split("!coppermind")[-1]

            if 'no tag' in text.lower():
                text = text.lower().split("no tag")[0].split()
                tag1 = ''
                tag2 = ''

            else:
                text = text.lower().split()
                tag1 = '>!'
                tag2 = '!<'

            try:
                try:
                    n = int(text[-1])
                    search = "_".join(text[:-1])

                except:
                    n = 5
                    search = text[0]

                punc = '''!()-[]{};:'"\,<>./?@#$%^&*~'''

                for ele in search:
                    if ele in punc:
                        search = search.replace(ele, "")

                if n > 5:
                    n = 5

                doc= f'https://coppermind.net/wiki/{search}'
                res = requests.get(doc)
                soup = BeautifulSoup(res.content, "html.parser")
                rows =soup.find('div',attrs={"class" : "mw-parser-output"})

                try:
                    if "disambiguation" in text[0]:
                        comment.reply(f'{search} may refer to multiple pages.\n\n\
Visit {doc} to find what you want.')
                        comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                        print("Coppermind tapper found!")

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")

                    else:
                        text_list = []
                        for p in rows.find_all('p'):
                            text_list.append(f'{tag1}{p.get_text()}{tag2}')
                            if not text_list[-1]:
                                del text_list[-1]

                        text = "***Warning Gancho: The below paragraph(s) may contain major spoilers for all books in the Cosmere!***\n\n" + "\n\n".join([f"{x}".replace("\n", "").strip() for x in text_list[:n+1]]) + tag2 + f"\n\n^[The article can be viewed here!]({doc})"

                        comment.reply(text)
                        comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                        print("Coppermind tapper found!")

                        with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                            f.write(comment.id + "\n")
                except:
                    comment.reply(f"The article {search} does not seem to exist. Check if you have made a spelling mistake, or if there is another name that might work.")
                    comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                    print("Coppermind tapper found!")

                    with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                        f.write(comment.id + "\n")

            except:
                comment.reply(f"Gon, u/(Whatever storming username AlThorStormblessed is using) must have missed something in the code, or your keywords are off, because I couldn't find anything. [How about you take a quick look around Coppermind yourself?](https://coppermind.net/wiki/Coppermind:Welcome)")
                comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
                print("Coppermind tapper found!")

                with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                    f.write(comment.id + "\n")

    #WOB function
        if "!wob" in comment.body.lower() and comment.body.lower().count("!wob") > comment.body.lower().count(">!wob") and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
            text = comment.body.lower()
            text = text.split("!wob")[-1]

            if 'no tag' in text.lower():
                text = text.lower().split("no tag")[0].split()
                tag1 = ''
                tag2 = ''

            else:
                text = text.lower().split()
                tag1 = '>!'
                tag2 = '!<'
            '''try:'''
            try:
                n = int(text[-1])
                search = "+".join(text[:-1])

            except:
                n = 5
                search = "+".join(text)

            punc = '''!()[]{};:'"\,<>./?@#$%^&*~'''

            for ele in search:
                if ele in punc:
                   search = search.replace(ele, "")

            if n > 8:
                n = 8

            doc= f'https://wob.coppermind.net/adv_search/?query={search}'
            res = requests.get(doc)
            soup = BeautifulSoup(res.content, "html.parser")
            rows =soup.find_all('div',attrs={"class" : "entry-content"})[:n]
            ##      print(*rows, sep = "\n\n")

            text_list = []
            for tag in rows:
       ##                print(text_list)
                for p in tag.find_all(['p', 'h4']):
                    for symbol in ["<em>", "</em>", "<strong>", "</strong>"]:
                        if symbol in p:
                            p = p.replace(symbol, "**")

                    if 'h4' not in str(p):
                        text_list.append(f'{tag1}{p.get_text().replace("u/", "").replace("<p>", "").replace("</p>", "")}{tag2}')
                    else:
                        text_list.append(p.get_text().replace("<p>", "").replace("</p>", "").replace("u/", ""))
                    if not text_list[-1]:
                        del text_list[-1]
                text_list.append(f"\*"*20)

            if len("\n\n".join([f"{x}".replace("\n", "").strip() for x in text_list])) > 9000:
                special_tag = f'{tag2}\n\n[Incomplete WOB....]'
            else:
                special_tag = ''

            text = "***Warning Gancho: The below paragraph(s) may contain major spoilers for all books in the Cosmere!***\n\n" + "\n\n".join([f"{x}".replace("\n", "").strip() for x in text_list])[:9000] + special_tag + f"\n\n^([All the WOBs can be viewed here!]({doc}))".replace("u/", "")

            while "<a" in text:
                html = text.split("<a")[1].split(r"</a>")[0]
                link = ""
                for apos in ["\"", "\'"]:
                    for thing in [f'href = {apos}', f'href={apos}']:
                        if not link:
                            try:
                                link = html.split(f'{thing}')[1].split(f"{apos}>")[0]
                                body = html.split(f"{apos}>")[1].strip()
                                break
                            except:
                                pass
                new_link = f'[{body}]({link})'
                text = text.replace("<a" + html + "</a>", new_link)

            while ">! " in text:
                text = text.replace(">! ", ">!")

            while "[\"" in text:
                text = text.replace("[\"", "[")

            while "\"](" in text:
                text = text.replace("\"](", "](")

            comment.reply(text)
            print("WOB stuff")
            comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                f.write(comment.id + "\n")

        if 'wob.coppermind.net' in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():

            text = comment.body.lower()

            if '](' in comment.body:
                text = text.split('](')[1]

                doc_list = ['https://wob.coppermind.net/api/entry/' + doc2.split('#e')[1].split(')')[0] for doc2 in text if 'wob.coppermind.net' in doc2]

            else:
                try:
                    doc_list = ['https://wob.coppermind.net/api/entry/' + doc2.split('#e')[1] for doc2 in text.split() if 'wob.coppermind.net' in doc2]
                except:
                    print(comment.id)
                    doc_list = []

            try:
                if doc_list:
                    text_list = []

                    for doc in doc_list:
                        res = requests.get(doc)
                        soup = BeautifulSoup(res.content, "html.parser")

                        dic = json.loads(str(soup))

                        for n in range(len(dic['lines'])):
                            for line in dic['lines'][n].values():
                                for symbol in ["<em>", "</em>", "<strong>", "</strong>"]:
                                    if symbol in line:
                                        line = line.replace(symbol, "**")

                                if "<p>" in line:
                                    text_list.append(f'>!{line.replace("<p>", "").replace("</p>", "").replace("u/", "")}!<')
                                else:
                                    text_list.append(line.replace("u/", ""))

                        text_list.append("\*"*20)

                    if text_list:
                        if len("\n\n".join([f"{x}".replace("\n", "").strip() for x in text_list])) > 9000:
                            special_tag = f'!<\n\n[Incomplete WOB....]'
                        else:
                            special_tag = ''

                        text = "***Warning Gancho: The below paragraph(s) may contain major spoilers for all books in the Cosmere!***\n\n" + "\n\n".join([f"{x}".replace("\n", "").strip() for x in text_list])[:9000] + special_tag
                        text = text.replace("u/", "")

                        while "<a" in text:
                            html = text.split("<a")[1].split(r"</a>")[0]
                            link = ""
                            for apos in ["\"", "\'"]:
                                for thing in [f'href = {apos}', f'href={apos}']:
                                    if not link:
                                        try:
                                            link = html.split(f'{thing}')[1].split(f"{apos}>")[0]
                                            body = html.split(f"{apos}>")[1].strip()
                                            break
                                        except:
                                            pass
                            new_link = f'[{body}]({link})'
                            text = text.replace("<a" + html + "</a>", new_link)

                        while ">! " in text:
                            text = text.replace(">! ", ">!")

                        comment.reply(text)
                        print("WOB stuff")

            except Exception as e:
                print(e, "\nWOB stuff didn't work.")

            comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again

            with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
                f.write(comment.id + "\n")

    # for comment in r.subreddit('Wetlanderhumor').comments(limit = 50):
    #     comment.refresh()

    #     if "!meme" in comment.body.lower() and comment.id not in comments_replied_to2 and not comment.author == r.user.me():
    #         text = comment.body
    #         text = text.split("!meme")[-1]
    #         text = text.split()

    #         try:
    #             punc = '''!()-[]{};:'"\,<>./?@#$%^&*~'''

    #             for ele in text:
    #                 if ele in punc:
    #                     text = text.replace(ele, "")

    #             num = int(text[0])

    #             meme_text = r.submission(id='ppfuy7').selftext.split("\n") + r.submission(id='ppfx07').selftext.split("\n") + r.submission(id='pzswww').selftext.split("\n") + r.submission(id='u2lcop').selftext.split("\n")

    #             post_links = []
    #             for element in meme_text:
    #                 element2 = element
    #                 for ele in element2:
    #                     if ele in punc:
    #                         element2 = element2.replace(ele, " ")

    #                 if str(num) in element2.split():
    #                     post_links.append(element)


    #             text_links = "\n\n".join(post_links)

    #             if text_links:
    #                 comment.reply("Hey, gon, I think this is what you are looking for\n\n" + text_links)

    #         except:
    #             comment.reply("Make sure you are using  the correct format, which is '!meme (part no.)' to produce a result.")

    #         comments_replied_to2.append(comment.id)  #Simply adds the comment.id replied to to a list so the bot doesn't reply to it again
    #         print("Meme sent!")

    #         with open("comments_replied_to2.txt", "a", encoding='cp1252') as f:
    #             f.write(comment.id + "\n")

    print("Sleeping for a bit")
    time.sleep(30)  #Cool-down period

#Function to save comments replied to
def get_saved_comments():
    if not os.path.isfile("comments_replied_to2.txt"):
        comments_replied_to2 = []

    else:
        with open("comments_replied_to2.txt", "r", encoding='cp1252') as f:
            comments_replied_to2 = f.read()
            comments_replied_to2 = comments_replied_to2.split("\n")
    return comments_replied_to2

def get_saved_posts():
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    else:
        with open("posts_replied_to.txt", "r", encoding='cp1252') as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
    return posts_replied_to

def get_skimmed_comments():
    if not os.path.isfile("comments_skimmed.txt"):
        comments_skimmed = []

    else:
        with open("comments_skimmed.txt", "r", encoding='cp1252') as f:
            comments_skimmed = f.read()
            comments_skimmed = comments_skimmed.split("\n")
    return comments_skimmed

def get_mod_posts():
    if not os.path.isfile("mod_posts.txt"):
        mod_posts = []

    else:
        with open("mod_posts.txt", "r", encoding='cp1252') as f:
            mod_posts = f.read()
            mod_posts = mod_posts.split("\n")
    return mod_posts

def get_mod_comments():
    if not os.path.isfile("mod_comments.txt"):
        mod_comments = []

    else:
        with open("mod_comments.txt", "r", encoding='cp1252') as f:
            mod_comments = f.read()
            mod_comments = mod_comments.split("\n")
    return mod_comments

def get_mod_queue_posts():
    if not os.path.isfile("mod_queue_posts.txt"):
        mod_queue_posts = []
    else:
        with open("mod_queue_posts.txt", "r", encoding='cp1252') as f:
            mod_queue_posts = f.read()
            mod_queue_posts = mod_queue_posts.split("\n")
    return mod_queue_posts

def get_removed_comments():
    if not os.path.isfile("removed_comments.txt"):
        removed_comments = []
    else:
        with open("removed_comments.txt", "r", encoding='cp1252') as f:
            removed_comments = f.read()
            removed_comments = removed_comments.split("\n")
    return removed_comments

#Splits comment replied to into whole words
def WholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def rank(author):
    vorin = pd.read_csv("Vorin.csv", usecols = ["Name", "Points"])
    ranks = {
            -100 : "Darkborn",
            50 : "Lighteyes",
            500: "Brightness",
            2000: "High-noble",
            5000: "Holy Emperor",
            10000: "Herald"
            }

    if not vorin["Name"].str.contains(str(author)).any():
        return "Darkborn"
    if vorin["Points"][vorin.index[vorin['Name'] == author]].item() < -100:
        return "Heretic"

    for x in ranks:
        if vorin["Points"][vorin.index[vorin['Name'] == author]].item() >= x:
            Storm_rank =  ranks[x]
        else:
            break

    return Storm_rank

def chouta(author):
    chouta = pd.read_csv("Chouta.csv", usecols = ["Name", "Chouta"])
    if not chouta["Name"].str.contains(str(author)).any():
        chouta = chouta.append({"Name" : author, "Chouta" : 1}, ignore_index=True)
    else:
        chouta["Chouta"][chouta.index[chouta['Name'] == author]] += 1

    chouta.to_csv("Chouta.csv", index = False)
    chouta = pd.read_csv("Chouta.csv", usecols = ["Name", "Chouta"])
    return chouta["Chouta"][chouta.index[chouta['Name'] == author]].item()


#Running the functions
r = bot_login()
comments_replied_to2 = get_saved_comments()[-200:]
comments_skimmed = get_skimmed_comments()[-500:]
posts_replied_to = get_saved_posts()[-50:]
mod_posts = get_mod_posts()[-10:]
mod_comments = get_mod_comments()[-20:]
removed_comments = get_removed_comments()[-20:]
mod_queue_posts = get_mod_queue_posts()

count = 0

while True:
    try:
        run_bot(r, comments_replied_to2, posts_replied_to, comments_skimmed, mod_comments, mod_posts, removed_comments, WholeWord, rank, count, mod_queue_posts)
        count = 1
    except Exception as e:
        try:
            print(comment.id)
        except:
            pass
        finally:
            print(e)
            count = 1
            time.sleep(240)
