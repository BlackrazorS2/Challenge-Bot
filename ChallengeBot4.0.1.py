import json
import discord
from discord.ext import commands
import asyncio
import os
import datetime

################################################################################
#                        Challenge Bot Version 4.0.1                           #
#                                                                              #
# Last Updated: 12/30/2020                                                      #
# Description: Discord bot that hosts and scores inputed challenges and        #
# displays those scores in a leaderboard on a given channel on a server        #
#                                                                              #
# External Packages required:                                                  #
#   discord.py -- install with "pip install discord.py"                        #
#                                                                              #
################################################################################

# should really be in a class
TOKEN = 'TOKEN'# Token for the bot, required to run it. To get the token, create an application with the discord website
passive_channel = None
global time
time = 10 # time passive leaderboard waits before refreshing

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='>>', intents=intents) # command prefix is >>
client.remove_command('help') # removes the default help command to replace it with a custom one

def adminCheck(id):
    """Checks if a given user is an admin"""
    if id == 'admin1' or id == "admin2" or id == "admin3" or id == "admin4": # check if command sender was an admin    
        return True
    else:
        return False

@client.event
async def on_ready(): # as the bot boots up
    await client.change_presence(activity=discord.Game(name='>>help for help!')) # status message is set to show the help command
    print('ready boss!') # prints a message to the terminal indicating that the bot is booted up

@client.command() # when someone types a function name with the prefix >>
async def createCategory(ctx, name): # function that creates a challenge category in which challenges are placed
    """Makes a directory to serve as a category for other challenges

    Arguments: \n
        name -- name of the category
    """
    try:
        sender = str(ctx.message.author) # defines the sender variable as the username of the sender
        id = str(ctx.message.author.id) # defines the id of the sender
        channel = str(ctx.message.channel) # Identifies where the command was sent from (a channel, a DM, etc)
        if channel == (f"Direct Message with {sender}"):  # if the command was sent from a DM:
            if adminCheck(id) == True: # check if command sender was an admin
                await ctx.send("I am under the impression that you are an authorized user...") # confirmation that sender is an admin
                if not os.path.isdir("categories/"):
                    os.mkdir("categories/")
                os.mkdir(f"categories/{name}") # make a directory inside the categories folder with the given category name where all the challenge files will be stored
                with open(f"categories/{name}/points.json", "w+") as f: # creates the point file for the category and if it already exists, overwrite it
                    init = dict() # creates an empty dictionary so insert into the json file as a base
                    json.dump(init, f) # write the dictionary into json and place it into the file
                await ctx.send("Category made! Have fun!") # confirm to user that category is created
            else: # if the user is not on the admin list
                await ctx.send("You're not authorized to use this command!") # notify user
        else: # if the user is not using the command in a direct message with the bot
            await ctx.send("This is not a direct message!") # notify user
    except: # if any other error occurs
       await ctx.send("An error has occured, check you arguments and try again. :(") # notify user

@client.command()
async def createChallenge(ctx, category, name, answer, base, *placements):
    """Creates a challenge in the given category
    
    Arguments: \n
        category    -- The name of the category this challenge is supposed to be in
        name        -- The name of the challenge. Place in quotations for multiple words (i.e. "Challenge Name Here" or Challenge)
        answer      -- The correct flag for this challenge
        base        -- The default point value of the challenge (when all special positions are done)
        *placements -- Special point values for order of completion. Goes in decending order (i.e. 1st, 2nd, 3rd, 4th...)
    
    Example coroutine call: \n
        >>createChallenge main chctf{answer} ChallengeName 100 500 400 300 200
        command-^  category-^  answer-^      name-^    base-^  ^-placements-^
    """
    try:
        sender = str(ctx.message.author) # get the username of the user who initiated the command
        id = str(ctx.message.author.id) # get the id of the user who initiated the command
        channel = str(ctx.message.channel) # get the channel that the message was sent from
        if channel == (f"Direct Message with {sender}"):  # if the command was sent from a DM:
            if adminCheck(id) == True: # check if the user is an admin
                await ctx.send("Authorized!") # confirmation that user is an admin
                if os.path.exists(f"categories/{category}"): # check to see if the category exists
                    # if the category exists
                    data = dict() # create an empty dictionary
                    with open(f"categories/{category}/{name}.json", "w+") as f: # create a json file for this challenge in the given category
                        data['answer'] = answer # create the answer key in the dictionary and make the value the given answer
                        data['base'] = base
                        data['complete'] = [] # create the key for the users who have completed the challenge and attaches an empty list as the value
                        for i, place in enumerate(placements, 1):
                            data[f"placement {i}"] = place
                        json.dump(data, f) # add the populated dictionary to the challenge file
                    await ctx.send(f"Challenge created in category {category}! Have fun!") # notify user that the challenge has been created
                else: # if the category doesn't exist
                    await ctx.send("Sorry but that category doesn't seem to exist. Make sure you check your spelling and arguments.") # notify user
    except: # if a general error occurs
        await ctx.send("An error has occured, check you arguments and try again. :(") # notify user

@client.command()
async def challenge(ctx, category, name, answer): # fuction allows user to submit and answer for a challenge for points
    """Submits challenge with using given answer
    
    Arguments: \n
        category -- category name
        name     -- name of challenge, make sure to put in quotations if it is multi-worded ("Challenge name")
        answer   -- answer to the challenge
    """
    try:
        sender = str(ctx.message.author) # get the username of the sender
        id = str(ctx.message.author.id) # get the id of the user
        channel = str(ctx.message.channel) # get the channel of the sent message
        if channel == (f"Direct Message with {sender}"): # verify that the message was sent in a direct message
            if os.path.exists(f"categories/{category}"): # if the category given exists
                with open(f"categories/{category}/{name}.json", 'r+') as f: # open the json file for that challenge
                    data = json.load(f) # load the json object into a python object
                completed_previously = False # assume that the user has not completed the challenge before
                #answer_right = False # assume that the answer the user has given is false
                for completor in data['complete']: # iterate over the users listed to have completed the challenge already
                    if completor == id: # if the id of the user matches the id of a user in the list
                        completed_previously = True # note that the user has completed the challenge previously
                    else: # if the id of the current user does not match any other user in the list
                        continue # keep completed_previously as false
                with open(f"categories/{category}/points.json", 'r') as points: # open the points json file
                    scores = json.load(points) # load the json object as a python object
                if completed_previously == False: # if the user has not completed this challenge
                    if answer == data['answer']: # if the answer given matches the answer of the challenge
                        completion_num = len(data['complete'])+1 # figure out what place the user came in in terms of answering
                        placements = list(data.keys())
                        del placements[0:2] #trim list to placmements only
                        placed = False
                        for placement in placements:
                            if placement[len(placement)-2:] == completion_num:
                                placed = True
                                points = int(data[f"placement {completion_num}"])
                                break
                            else:
                                continue
                        if not placed:
                            # use base score
                            points = int(data["base"])
                        
                        # adding score to file
                        if id in scores:
                            scores[id] += points
                        else:
                            scores[id] = points
                        
                        await ctx.send(f"Challenge completed! Your position in answering this challenge: {completion_num}")
                        data['complete'].append(id)
                        with open(f"categories/{category}/{name}.json", 'w') as f, open(f"categories/{category}/points.json", "w") as g: # open the challenge json file
                            json.dump(data, f)
                            json.dump(scores, g)


                    else: # if the given answer does not match the challenge's answer
                        await ctx.send("Incorrect :( Try again next time!") # notify user
                else: # if the user has already completed this challenge
                    await ctx.send("You've already done this challenge!") # notify user
            else: # if the category is not found
                await ctx.send("The category you specified does not exist. Please check your spelling and try again.") # notify user
        else: # if the message was not sent in a direct message
            await ctx.send("This command is for Direct Messages only! Please go use this command in a direct messsage.") # notify user
    except: # if a general error occurs
        await ctx.send("An error has occured, check you arguments and try again. :(") # notify user

@client.command()
async def startBoard(ctx, refreshtime=10):
    """Turns on the passive leaderboard in the channel the command was sent in, can only be used by admins"""
    id = str(ctx.message.author.id) # defines the id of the sender
    if adminCheck(id):
        global passive_channel
        channel = ctx.message.channel.id # Identifies where the command was sent from (a channel, a DM, etc)
        print(f"Channel set too {channel}")
        passive_channel = channel
        print(passive_channel)
        time = refreshtime
        await ctx.send("Starting leaderboard!")
@client.command()
async def stopBoard(ctx):
    """Turns off the passive leaderboard, can only be used by admins"""
    id = str(ctx.message.author.id) # defines the id of the sender
    if adminCheck(id):
        global passive_channel
        passive_channel = None
        await ctx.send("Stopping leaderboard!")

async def passive_leaderboard(): # this fuction is a leaderboard that passively updates every 4 hours
    while True: 
        await client.wait_until_ready() # make sure the client has finished all other tasks to prevent errors
        if passive_channel != None:
            channel = client.get_channel(passive_channel) # get the channel given to host the leaderboard
            server = client.get_guild(499023413986328578) # gets a guild(server) object with the given id
            try:
                deletion = [] # make a list where messages will be prepped to be deleted
                async for message in channel.history(): # clears message history in channel before posting leaderboard
                    deletion.append(message) # append any messages in the channel to the deletion list
                await channel.delete_messages(deletion) # delete all messages in the list
                base_string = "You can submit scores and get on the leaderboard using the ``>>challenge`` command\n \n" # the string that will contain leaderboard scores


                # objective: get points file with its category and sort it

                for root, dirs, files in os.walk("categories/"): # walk through every challenge directory which are contained in the currect directory
                    for file in files: 
                        if file == ("points.json"): # open the points folder for each category
                            path = os.path.join(root, file) # form the absolute path for the points file
                            with open(path) as f:
                                scores = json.load(f) # load the points json file
                            sorted_scores = sorted(scores.items(), key=lambda x: float(x[1]), reverse=True) # use the sorted method to sort the dictionary into a list of tuples in desceding order
                            base_string = base_string + "Category: " + root[11:] + "\n"


                            for order, score in enumerate(sorted_scores, 1): # for each score in the dictionary
                                id = score[0] # collect the id of each score
                                points = score[1] # collect the point value for that person
                                try:
                                    username = server.get_member(int(id)).nick # collect the nickname of each id
                                except:
                                    username = server.get_member(int(id)).display_name # just get the username
                                if username == None: # if the user doesn't have a nickname
                                    username = server.get_member(int(id)).display_name # just get the username
                                if order == 1: # if the user is first in the list assign labels and a medal emote
                                    place = ":first_place:" 
                                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                                    order += 1 # increase the value of order for the next person in the list
                                elif order == 2: # if the user in second assign label and a medal emote
                                    place = ":second_place:" 
                                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                                    order += 1 # increase the value of order for the next person in the list
                                elif order == 3: # if the user is third assign label and a medal emote
                                    place = ":third_place:"
                                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                                    break
                                    # additional placements not needed since the passive leaderboard only tracks the top 3 in each category
                                    # the complete leaderboards are displayed in the normal leaderboard command
                                else:
                                    place = "ERROR"
                        else:
                            continue
                # set up the embed which contains the leaderboard
                emb = discord.Embed(description=f"{base_string}\nTime of last update: ``{str(datetime.datetime.now())}``", color=0x00fffd)
                emb.set_author(name="Challenge Leaderboard - Top Scorers", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
                await channel.send(embed=emb)
            except Exception as e:
                await channel.send(f"An error has occurred with the passive leaderboard with exception: {e} (also we need a face for this one) ")
        await asyncio.sleep(time)

@client.command()
async def leaderboard(ctx, category): # called leaderboard function which displays the full leaderboard for a given category
    try: 
        server = client.get_guild(499023413986328578) # gets a guild(server) object with the given id
        base_string = f"You can submit scores and get on the leaderboard using the ``>>challenge`` command\n \nCategory: {category}\n \n"
        if os.path.exists(f"categories/{category}"): # if the given category exists
            with open(f"categories/{category}/points.json") as f: # open the category's points file and load it into a python object
                data = json.load(f)
            sorted_scores = sorted(data.items(), key=lambda x: float(x[1]), reverse=True) # use the sorted method to sort the dictionary into a list of tuples in desceding order    
            
            # same as the passive leaderboard function with implementation for users who are placed after 3rd

            order = 1
            for score in sorted_scores:
                id = score[0]
                points = score[1]
                user = server.get_member(int(id))
                if user == None:
                    continue
                username = server.get_member(int(id)).nick
                if username == None:
                    username = server.get_member(int(id)).display_name
                if order == 1:
                    place = ":first_place:"
                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                    order += 1
                elif order == 2:
                    place = ":second_place:"
                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                    order += 1
                elif order == 3:
                    place = ":third_place:"
                    base_string = base_string + place + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                    order += 1
                else:
                    place = str(order) + ". "
                    order +=1
                    #base_string = base_string + str(place) + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
                    base_string += f"{str(place)}{str(username)}: {str(points)}\n \n"
            emb = discord.Embed(description=base_string, color=0x00fffd)
            emb.set_author(name=f"Challenge Leaderboard: {category}", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("Chosen category doesn't seem to exist! Please check your spelling and try again. :(")
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")
    

@client.command()
async def cat(ctx): #lists all categories available
    """Lists all available categories by looking through the 'categories' directory and list the number of challenges in each"""
    try:
        message = "```ini\n"
        for count, item in enumerate(os.listdir("categories/"), 1):
            if os.path.isdir(f"categories/{item}"):
                numChal = len(os.listdir(f"categories/{item}"))-1
                message += f"[{count}.] {item} - {numChal} challenges\n"

        message+="```"
        emb = discord.Embed(description=message, color=0x00fffd)
        emb.set_author(name="Available Challenge Categories", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"An error has occured, check you arguments and try again {e}. :(")

@client.command()
async def completions(ctx, category, name): # displays which users have completed a given challenge in a given category
    try:
        base_string = "```ini\n"
        if os.path.exists(f"categories/{category}"): # if the category exists
            with open(f"categories/{category}/{name}.json") as f: # open the challenge json file and load it into a python object
                data = json.load(f)
            
            for order, person in enumerate(data['complete'], 1): # for each id listed in the complete value of the dictionary
                user = ctx.guild.get_member(int(person))
                print(user)
                if user == None:
                    continue
                user=user.nick # get the user's nickname
                if user == None:
                    user = ctx.guild.get_member(int(person)).display_name # get the user's username if they do not have a nickname
                base_string += f"[{str(order)}.] {str(user)}\n" # add the id into the base string along with the order
            emb = discord.Embed(description=f"{base_string}```", color=0xffff00)
            emb.set_author(name=f"Completions for Challenge {str(name)}", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("I can't find the category! Please make sure the one you typed is correct :(")
    except Exception as e:
        await ctx.send(f"An error has occured, check you arguments and try again ({e}). :(")

@client.command()
async def info(ctx, category, name): # displays how many points a given challenge is worth. Includes first, second, third, and base placement bonuses
    try:
        if os.path.exists(f"categories/{category}"):
            with open(f"categories/{category}/{name}.json") as f:
                data = json.load(f)

            message = "```ini\n"
            base = data.get("base")
            del data["answer"] # leave only placements
            del data["base"]
            del data["complete"]
            for i, item in enumerate(data, 1):
                message += f"[{i}:] {data.get(item)}\n"
            message += f"[Base:] {base}```"

            emb = discord.Embed(description=message, color=0x0000ff)
            emb.set_author(name=f"Point Framework for Challenge {str(name)}", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("The catagory you have selected does not currently exist. Please check your spelling and try again :(")
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")

@client.command()
async def stats(ctx, username):
    """Displays statistics for a mentioned user
    
    Stats: \n
        Total challenges completed
        Total points earned
        Most answered Category
        Avg challenges completed per category (challenges/category)
        Challeges completed per category (main - 3, hackmas- 2)
        Avg points earned per challenge
        Avg answering position (1st, 4th, etc)
        
    """

    if "<@" in username and ">" in username: # checks for the components of a mention
        # do the program
        # collect data
        data = {"points": 0,
                "position": []
                }
        """challenges_complete = 0
        total_points = 0
        challenges_per_cat = {} # dictionary with keys of categories having values of a list of challenges completed
        answer_pos = [] # list of positions as integers, makes easy for averaging"""
        id_str = username[3:len(username)-1] # should trim <@ and >
        print(id_str)
        for item in os.listdir("categories/"):
            for challenge in os.listdir(f"categories/{item}"):
                data[item] = []
                if challenge == "points.json": # get total points
                    with open(f"categories/{item}/points.json") as f:
                        points_data = json.load(f)
                    try:
                        points = points_data.get(id_str)
                    except:
                        points = 0
                    if points == None:
                        points = 0
                    puntas = data["points"]
                    puntas += points
                    data["points"] = puntas
                else: # get other challenge data
                    with open(f"categories/{item}/{challenge}") as f:
                        challInfo = json.load(f)
                    if id_str in challInfo["complete"]:
                        data[item].append(challenge[:len(challenge)])
                        data["position"].append(challInfo["complete"].index(id_str)+1)
        # processing data
        totalComplete = 0
        mostAnswered = None
        cats = []
        print(data)
        for key in data.keys():
            if key != "points" and key != "position": # the categories
                totalComplete += len(data[key])
                print(totalComplete)
                cats.append(key)
                print(cats)
                if mostAnswered == None or len(data[key]) > len(data[mostAnswered]):
                    mostAnswered = key
                else:
                    pass
        avgCompPerCat = totalComplete/len(data)-2
        numChalls = 0 
        for category in cats:
            numChalls += len(data[category])
        # put except ZeroDivisionError here
        pointsPerChall = data["points"]/numChalls
        sumPlacements = 0
        for item in data["position"]:
            sumPlacements += int(item)
        avgPlace = sumPlacements/len(data["position"])
        challComps = "Categories\n  "
        for cat in cats:
            challComps += f"{cat}: {data[cat]}\n" 
        await ctx.send(f"Total chall: {totalComplete}\nTotal Point: {data.get('points')}\nMost Answered Cat: {mostAnswered}\nAvg Compl per cat: {avgCompPerCat}\nChallenges completed: {challComps}\nAvg points per chall: {pointsPerChall}\nAvg aswr pos: {avgPlace}") 
    else:
        await ctx.send("Not a valid mention! type @Username to do a mention!")

    pass

@client.command()
async def patchNotes(ctx):
    """Displays a list of patch notes"""
    # should figure out how to get pages working for this, new page for every patch
    pass

@client.command()
async def help(ctx): 
    """lists all the commands and their arguments for users"""
    try:
        helpString = ("" + '\n' + ">>createCategory <name> - creates a new category in which challenges can be stored" + '\n' + \
            ' ' + '\n' +\
        ">>createChallenge <category> <answer> <num> <first> <second> <third> <base> - creates challenges in a given category. If you're not authorized, you can't use this" + '\n' + \
            ' ' + '\n' +\
        '>>challenge <category> <challenge num> <flag> - Submits an answer to a challenge. Requires the challenge number which was included with the original posting of it.' + '\n' +\
            ' ' + '\n' + \
        '>>cat - lists all available categories and the number of challenges in each of them.' + '\n' + \
            ' ' + '\n' + \
        '>>leaderboard <category> - pulls up the leaderboard in a given category. Note this is different than the leaderboard that passively updates' + '\n' + \
            ' ' + '\n' +\
        ">>info <category> <challenge number> - displays the point framework for that challenge (.i.e what first, second, third, and everyone else get)" + '\n' + \
            ' ' + '\n' + \
        ">>completions <category> <challenge number> - displays the people who have completed a given challenge. This should only be used in server." + '\n' + \
            ' ' + '\n' + \
        ">>patchnotes - displays patch notes. Currently holds nothing." + '\n' + \
            ' ' + '\n' + \
        ">>stats >mention> - displays stats for a given user, currently does not work." + '\n' + \
            ' ' + '\n' + \
        ">>startBoard [refreshtime] - starts the passive leaderboard refreshing after a given time. Defaults to 10 seconds\n" + \
            ' ' + '\n' + \
        ">>stopBoard - stops the passive leaderboard\n" + \
            ' ' + '\n' + \
        '>>help - brings up this menu!')
        emb = discord.Embed(description=helpString, color=0x39e600)
        emb.set_author(name="Help Menu!", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
        await ctx.send(embed=emb)
    except:
        await ctx.send("An error occured, definitly on my end.")


client.loop.create_task(passive_leaderboard())
client.run(TOKEN)
