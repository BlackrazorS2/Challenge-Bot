import json
import discord
from discord.ext import commands
import asyncio
import os
import datetime

################################################################################
#                        Challenge Bot Version 3.0.0                           #
#                                                                              #
# Last Updated: 1/24/2020                                                      #
# Description: Discord bot that hosts and scores inputed challenges and        #
# displays those scores in a leaderboard on a given channel on a server        #
#                                                                              #
################################################################################

TOKEN = 'TOKEN'# Token for the bot, required to run it. To get the token, create an application with the discord website

client = commands.Bot(command_prefix='>>') # command prefix is >>
client.remove_command('help') # removes the default help command to replace it with a custom one

@client.event
async def on_ready(): # as the bot boots up
    await client.change_presence(activity=discord.Game(name='>>help for help!')) # status message is set to show the help command
    print('ready boss!') # prints a message to the terminal indicating that the bot is booted up

@client.command() # when someone types a function name with the prefix >>
async def createCategory(ctx, name): # function that creates a challenge category in which challenges are placed
    try:
        sender = str(ctx.message.author) # defines the sender variable as the username of the sender
        id = str(ctx.message.author.id) # defines the id of the sender
        channel = str(ctx.message.channel) # Identifies where the command was sent from (a channel, a DM, etc)
        if channel == ("Direct Message with %s" % (sender)):  # if the command was sent from a DM:
            if id == 'Admin IDs (who you want to create categories)': # check if command sender was an admin
                await ctx.send("I am under the impression that you are an authorized user...") # confirmation that sender is an admin
                os.mkdir(name) # make a directory with the given category name where all the challenge files will be stored
                with open(name + "/points.json", "w+") as f: # creates the point file for the category and if it already exists, overwrite it
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
async def createChallenge(ctx, category, answer, num, first, second, third, base):
 # arguments are: category name, the answer of the challenge, the number of the challenge, the point value of the first person to
 # answer, the second person to answer, the third person to enter, and the point value for everyone else that answers
    try:
        sender = str(ctx.message.author) # get the username of the user who initiated the command
        id = str(ctx.message.author.id) # get the id of the user who initiated the command
        channel = str(ctx.message.channel) # get the channel that the message was sent from
        if channel == ("Direct Message with %s" % (sender)):  # if the command was sent from a DM:
            if id == 'Admin IDs (who you want to create categories)': # check if the user is an admin
                await ctx.send("I believe I am correct in saying you are an authorized user") # confirmation that user is an admin
                if os.path.exists(category): # check to see if the category exists
                    # if the category exists
                    data = dict() # create an empty dictionary
                    with open(category + '/' + num + ".json", "w+") as f: # create a json file for this challenge in the given category
                        data['answer'] = answer # create the answer key in the dictionary and make the value the given answer
                        data['first'] = first # create the key for the first answer points and add the given value
                        data['second'] = second # create the key for the second answer points and add the given value
                        data['third'] = third # create the key for the third answer points and add the given value
                        data['base'] = base # create the key for the base answer points and add the given value
                        data['complete'] = [] # create the key for the users who have completed the challenge and attaches an empty list as the value
                        json.dump(data, f) # add the populated dictionary to the challenge file
                    await ctx.send(f"Challenge created in category {category}! Have fun!") # notify user that the challenge has been created
                else: # if the category doesn't exist
                    await ctx.send("Sorry but that category doesn't seem to exist. Make sure you check your spelling and arguments.") # notify user
    except: # if a general error occurs
        await ctx.send("An error has occured, check you arguments and try again. :(") # notify user

@client.command()
async def challenge(ctx, category, num, answer): # fuction allows user to submit and answer for a challenge for points
    try:
        sender = str(ctx.message.author) # get the username of the sender
        id = str(ctx.message.author.id) # get the id of the user
        channel = str(ctx.message.channel) # get the channel of the sent message
        if channel == ("Direct Message with %s" % (sender)): # verify that the message was sent in a direct message
            if os.path.exists(category): # if the category given exists
                with open(category + '/' + num + ".json", 'r+') as f: # open the json file for that challenge
                    data = json.load(f) # load the json object into a python object
                completed_previously = False # assume that the user has not completed the challenge before
                answer_right = False # assume that the answer the user has given is false
                for completor in data['complete']: # iterate over the users listed to have completed the challenge already
                    if completor == id: # if the id of the user matches the id of a user in the list
                        completed_previously = True # note that the user has completed the challenge previously
                    else: # if the id of the current user does not match any other user in the list
                        continue # keep completed_previously as false
                with open(category + '/points.json', 'r+') as points: # open the points json file
                    scores = json.load(points) # load the json object as a python object
                    if completed_previously == False: # if the user has not completed this challenge
                        if answer == data['answer']: # if the answer given matches the answer of the challenge
                            answer_right = True # set answer_right to be true
                            completion_num = len(data['complete']) # figure out what place the user came in in terms of answering

                            if completion_num == 0: # if list of completed users is empty (the user answered first)
                                await ctx.send("You answered first! +" + str(data['first']) + "points!") # notify user
                                if id in scores: # if the user already has a score in this category
                                    scores[id] += int(data['first']) # add the point value of this challenge to their score
                                else: # if the user has not answered a challenge before
                                    scores[id] = int(data['first']) # add a key of the user's id to the points dictionary with a value of the point value of this challenge
                            elif completion_num == 1: # if the user came in second
                                await ctx.send("You answered second! +" + str(data['second']) + "points!") # notify user
                                if id in scores: # if the user already has a score in this category
                                    scores[id] += int(data['second']) # add the point value to this score
                                else: # if this is the user's first challenge
                                    scores[id] = int(data['second']) # make the point value their score
                            elif completion_num == 2: # if the user came in third
                                await ctx.send("You answered third! +" + str(data['third']) + "points!") # notify user
                                if id in scores: # if the user already has a score in this category
                                    scores[id] += int(data['third']) # add the point value to their score
                                else: # if this is the user's first challenge
                                    scores[id] = int(data['third']) # make the point value their score
                            else: # if the user is any other place
                                await ctx.send("Challenge completed! +" + str(data['base']) + "points!") # notify user they completed the challenge
                                if id in scores: # if the user already has a score
                                    scores[id] += int(data['base']) # add the value of the challenge to their score
                                else: # if this is the user's first challenge
                                    scores[id] = int(data['base']) # make the point value their score
                        else: # if the given answer does not match the challenge's answer
                            await ctx.send("Incorrect :( Try again next time!") # notify user
                    else: # if the user has already completed this challenge
                        await ctx.send("You've already done this challenge!") # notify user
                with open(category + '/points.json', "w") as points: # open the json points file
                    json.dump(scores, points) # dump the new dictionary in the file in place of the old one (update scores)
                with open(category + '/' + num + ".json", 'w+') as f: # open the challenge json file
                    if completed_previously == False: # if the user has not done the challenge
                        if answer_right == True: # if the answer was correct
                            data['complete'].append(id) # add the user's id to the completion list in the challenge file
                    json.dump(data, f) # dump the python object as the json object
            else: # if the category is not found
                await ctx.send("The category you specified does not exist. Please check your spelling and try again.") # notify user
        else: # if the message was not sent in a direct message
            await ctx.send("This command is for Direct Messages only! Please go use this command in a direct messsage.") # notify user
    except: # if a general error occurs
        await ctx.send("An error has occured, check you arguments and try again. :(") # notify user

async def passive_leaderboard(): # this fuction is a leaderboard that passively updates every 4 hours
    await client.wait_until_ready() # make sure the client has finished all other tasks to prevent errors
    channel = client.get_channel(CHANNEL_ID) # get the channel given to host the leaderboard
    server = client.get_guild(SERVER_ID) # gets a guild(server) object with the given id
    try:
        while True: 
            deletion = [] # make a list where messages will be prepped to be deleted
            async for message in channel.history(): # clears message history in channel before posting leaderboard
                deletion.append(message) # append any messages in the channel to the deletion list
            await channel.delete_messages(deletion) # delete all messages in the list
            base_string = 'You can submit scores and get on the leaderboard using the ``>>challenge`` command' + '\n' + ' ' + '\n' # the string that will contain leaderboard scores
            top_dir = os.path.dirname(os.path.abspath(__file__)) # get the absolute path to this file
            for subdir, dirs, files in os.walk(top_dir): # walk through every challenge directory which are contained in the currect directory
                for file in files: 
                    if file == ("points.json"): # open the points folder for each category
                        path = os.path.join(subdir, file) # form the absolute path for the points file
                        with open(path) as f:
                            scores = json.load(f) # load the points json file
                        sorted_scores = sorted(scores.items(), key=lambda x: float(x[1]), reverse=True) # use the sorted method to sort the dictionary into a list of tuples in desceding order

                        order = 1 # variable that tracks the order of each score
                        base_string = base_string + "Category: " + subdir[86:] + "\n" # this is computer specific: Change the string cuttoff to whatever gets rid of the file path
                        for score in sorted_scores: # for each score in the dictionary
                            id = score[0] # collect the id of each score
                            points = score[1] # collect the point value for that person

                            username = server.get_member(int(id)).nick # collect the nickname of each id
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
            emb = discord.Embed(description=base_string + '\n' + "Time of last update: ``" + str(datetime.datetime.now()) + '``', color=0x00fffd)
            emb.set_author(name="Challenge Leaderboard - Top Scorers", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await channel.send(embed=emb)
            await asyncio.sleep(14400) # waits 4 hrs before updating leaderboard again
    except:
        await channel.send("An error has occurred with the passive leaderboard :[=] ")
@client.command()
async def leaderboard(ctx, category): # called leaderboard function which displays the full leaderboard for a given category
    try: 
        server = client.get_guild(server_id) # gets a guild(server) object with the given id
        base_string = 'You can submit scores and get on the leaderboard using the ``>>challenge`` command' + '\n' + ' ' + '\n'
        if os.path.exists(category): # if the given category exists
            with open(category + "/points.json") as f: # open the category's points file and load it into a python object
                data = json.load(f)
            sorted_scores = sorted(data.items(), key=lambda x: float(x[1]), reverse=True) # use the sorted method to sort the dictionary into a list of tuples in desceding order    
            
            # same as the passive leaderboard function with implementation for users who are placed after 3rd

            order = 1
            base_string = base_string + "Category: " + category + "\n" + ' ' + '\n'
            for score in sorted_scores:
                id = score[0]
                points = score[1]

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
                    base_string = base_string + str(place) + str(username) + ": " + str(points) + '\n' + ' ' + '\n'
            emb = discord.Embed(description=base_string, color=0x00fffd)
            emb.set_author(name="Challenge Leaderboard: " + category, icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("Chosen category doesn't seem to exist! Please check your spelling and try again. :(")
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")
    

@client.command()
async def cat(ctx): #lists all categories available
    try:
        top_dir = os.path.dirname(os.path.abspath(__file__))
        # make it list how many challenges are in each category
        base_string = ""
        cats = os.listdir(top_dir)
        for direc in cats:
            if direc == "ChallengeBot3.0.0.py": # skip over this file so it does not show up in the list
                continue
            #base_string += direc[86:] + '\n'
            base_string += direc[86:] + '\n'
            #await ctx.send(direc)
            files = os.listdir(direc)
            count = 0
            for item in files:
                if item == "points.json": # skip over the points.json file so it is not counted toward the number of challenges
                    continue
                else:
                    count += 1
                    
            base_string += direc + ': ' + str(count) + '\n'
                
        emb = discord.Embed(description=base_string, color=0x00fffd)
        emb.set_author(name="Available Challenge Categories", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
        await ctx.send(embed=emb)
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")
@client.command()
async def completions(ctx, category, num): # displays which users have completed a given challenge in a given category
    try:
        base_string = '```ini' + '\n' + ''
        if os.path.exists(category): # if the category exists
            with open(category + '/' + num + ".json") as f: # open the challenge json file and load it into a python object
                data = json.load(f)
            order = 1
            for person in data['complete']: # for each id listed in the complete value of the dictionary
                name = ctx.guild.get_member(int(person)).nick # get the user's nickname
                if name == None:
                    name = ctx.guild.get_member(int(person)).display_name # get the user's username if they do not have a nickname
                base_string += "[" + str(order) + ".] " + str(name) + '\n' # add the id into the base string along with the order
                order += 1
            emb = discord.Embed(description=base_string + '```', color=0xffff00)
            emb.set_author(name="Completions for Challenge" + str(num), icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("I can't find the category! Please make sure the one you typed is correct :(")
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")

@client.command()
async def info(ctx, category, num): # displays how many points a given challenge is worth. Includes first, second, third, and base placement bonuses
    try:
        if os.path.exists(category):
            with open(category + '/' + num + '.json') as f:
                data = json.load(f)
            message = ("```ini" + '\n' + "[1st:] " + data['first'] + "\n" + "[2nd:] " + data['second'] + "\n" + "[3rd:] " + data['third'] + '\n' + "[Base:] " + data['base'] + '```')
            emb = discord.Embed(description=message, color=0x0000ff)
            emb.set_author(name="Point Framework for Challenge" + str(num), icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
            await ctx.send(embed=emb)
        else:
            await ctx.send("The catagory you have selected does not currently exist. Please check your spelling and try again :(")
    except:
        await ctx.send("An error has occured, check you arguments and try again. :(")

@client.command()
async def help(ctx): # lists all the commands and their arguments for users
    try:
        helpString = ("```css" + '\n' + ">>createCategory [name] - creates a new category in which challenges can be stored" + '\n' + \
            ' ' + '\n' +\
        ">>createChallenge [category] [answer] [num] [first] [second] [third] [base] - creates challenges in a given category. If you're not authorized, you can't use this" + '\n' + \
            ' ' + '\n' +\
        '>>challenge [category] [challenge num] [flag] - Submits an answer to a challenge. Requires the challenge number which was included with the original posting of it.' + '\n' +\
            ' ' + '\n' + \
        '>>cat - lists all available categories and the number of challenges in each of them.' + '\n' + \
            ' ' + '\n' + \
        '>>leaderboard [category] - pulls up the leaderboard in a given category. Note this is different than the leaderboard that passively updates' + '\n' + \
            ' ' + '\n' +\
        ">>info [category] [challenge number] - displays the point framework for that challenge (.i.e what first, second, third, and everyone else get)" + '\n' + \
            ' ' + '\n' + \
        ">>completions [category] [challenge number] - displays the people who have completed a given challenge. This should only be used in server." + '\n' + \
            ' ' + '\n' + \
        '>>help - brings up this menu!```')
        emb = discord.Embed(description=helpString, color=0x39e600)
        emb.set_author(name="Help Menu!", icon_url="https://cdn.discordapp.com/avatars/626721881117949962/d8d4afa0652a2fc80fe7763a5314844a.webp?size=128")
        await ctx.send(embed=emb)
    except:
        await ctx.send("An error occured, definitly on my end.")


client.loop.create_task(passive_leaderboard())
client.run(TOKEN)