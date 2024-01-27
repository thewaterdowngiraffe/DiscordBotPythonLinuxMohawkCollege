import datetime
import subprocess
import datetime
import re
import simpleFunctions
import random
import importlib 
import platform
import sys
sys.path.insert(0, './config/')
import botConfig

PROGRAM_PATH = botConfig.getConfig("PROGRAM_PATH")

intents, responses = None,None
def getTimeOfDay(time):
    time = (int(str(time)[11:13])+24 -5 %24)
    if time < 12:   return "morning"
    elif time < 17: return "evening"
    else :          return "night"
    
async def asyncRunLXCommand(command,return_val = True):
    terminal = subprocess.run(  command,shell=True,capture_output=True)#,stdout=subprocess.PIPE)
    if return_val == True:
        return(terminal.stdout.decode())

def runLXCommand(command,return_val = True):
    result = subprocess.getoutput('{}'.format(command))
    if return_val == True:
        return(result)


def load_FAQ_data(msg = None):
    global PROGRAM_PATH
    importlib.reload(simpleFunctions) #can remove after testing but reloads the file reader function
    #these can be in a file honistly
    sampleCommands=[
        "lsblk",
        "ls -la",
        "ls"
        ]
    sampleCommandDesc= [
        "this will display a list of connected drives and the partitions",
        "this will display the current directory files and folders. the -la will show the item owner and the permissions of each item",
        "this will display the current directory files and folders"
        ]
    chosenCommandnum = random.randint(1,len(sampleCommands))-1

    #keys to find
    find = botConfig.getConfig("keyFind")
    
    replaceWith=None

    if msg == None:
        # this will be the function that if the key is found, it will be replaced with 
        replaceWith=[
                "user",
                "/s", # this may break the regex for a couple of the questions as it checks to see if the bot was @'d
                getTimeOfDay(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                str(int(datetime.date.today().year) - 1991),
                runLXCommand(sampleCommands[chosenCommandnum]), # linux command
                runLXCommand(f"grep -c . {PROGRAM_PATH}driver.py"), # linux command
                runLXCommand(f"grep -c . {PROGRAM_PATH}bot.py"), # linux command
                str(int(runLXCommand("cat /proc/cpuinfo | grep MHz")[-8:-4])/1000), # linux command
                int(re.sub('[A-Za-z\s*:]', '',runLXCommand("grep MemTotal /proc/meminfo")))/1024/1024, # linux command
                re.sub('\s*', '',runLXCommand("df  /  --block-size=G --output=size |grep '   '")), # linux command
                runLXCommand("uptime -p")[3:].replace(","," and",1), # linux command
                (runLXCommand("systemctl status discordBot |grep Active").split(";"))[1].split("ago")[0].replace("h", " hour").replace("min"," minutes "), # linux command
                sampleCommands[chosenCommandnum],
                sampleCommandDesc[chosenCommandnum],
                "\n",
                "\t"
            ]
    else:
        # this will be the function that if the key is found, it will be replaced with 
        replaceWith=[
                msg.author.nick,
                msg.guild.me.id,
                getTimeOfDay(msg.created_at),
                str(int(datetime.date.today().year) - 1991),
                runLXCommand(sampleCommands[chosenCommandnum]), # linux command
                runLXCommand(f"grep -c . {PROGRAM_PATH}driver.py"), # linux command
                runLXCommand(f"grep -c . {PROGRAM_PATH}bot.py"), # linux command
                str(int(runLXCommand("cat /proc/cpuinfo | grep MHz")[-8:-4])/1000), # linux command
                int(re.sub('[A-Za-z\s*:]', '',runLXCommand("grep MemTotal /proc/meminfo")))/1024/1024, # linux command
                re.sub('\s*', '',runLXCommand("df  /  --block-size=G --output=size |grep '   '")), # linux command
                runLXCommand("uptime -p")[3:].replace(","," and",1), # linux command
                (runLXCommand("systemctl status discordBot |grep Active").split(";"))[1].split("ago")[0].replace("h", " hour").replace("min"," minutes "), # linux command
                sampleCommands[chosenCommandnum],
                sampleCommandDesc[chosenCommandnum],
                "\n",
                "\t"
            ]
    if platform.system() == "Linux": 
        pass
    else:
        #tested on a mac with darwin
        chosenCommandnum = random.randint(2,len(sampleCommands))-1 # lsblk is not on mac
        replaceWith=[
            "user",
            "/s", # this may break the regex for a couple of the questions as it checks to see if the bot was @'d
            getTimeOfDay(msg.created_at),
            str(int(datetime.date.today().year) - 1991),
            runLXCommand(sampleCommands[chosenCommandnum]), # linux command
            runLXCommand(f"grep -c . {PROGRAM_PATH}driver.py"), # linux command will work on mac
            runLXCommand(f"grep -c . {PROGRAM_PATH}bot.py"), # linux command   will work on mac
            str(re.sub('[A-Za-z\s*:]', '',runLXCommand("sysctl hw.cpufrequency | grep Hz"))/1000000000), # linux command this may not work if your apple system is up to date
            int(re.sub('[A-Za-z\s*:]', '',runLXCommand("sysctl -n hw.memsize")))/1024/1024/1024, # linux command
            re.sub('[A-Za-z\s*:/]', '',runLXCommand("df -H -T /").split("G", 1)[0]), # linux command, should work on mac
            runLXCommand("uptime -p")[6:].split(",",1)[0], # linux command may work on mac
            "can not calculate on mac", # linux command
            sampleCommands[chosenCommandnum],
            sampleCommandDesc[chosenCommandnum],
            "\n",
            "\t"
        ]
    answers = simpleFunctions.readRegexQuestions(f"{PROGRAM_PATH}config/answers",find = find,replaceWith = replaceWith)
    questions = simpleFunctions.readRegexQuestions(f"{PROGRAM_PATH}config/questions",False)
    return questions, answers


def understand(utterance,botId = "bot"):
    """This method processes an utterance to determine which intent it
    matches. The index of the intent is returned, or -1 if no intent
    is found."""

    global intents # declare that we will use a global variable
    index = 0
    for rxCheck in simpleFunctions.readRegexQuestions(f"{PROGRAM_PATH}config/regexAnswers",find = ["{msg.guild.me.id}"],replaceWith = [botId]):
        if re.findall(rf'{rxCheck}',utterance.lower(),flags=re.IGNORECASE):
            #print(f"trigged regex:\n{rxCheck}") # testing to view called regex
            return index
        index+=1
    try:
        return intents.index(utterance)
    except ValueError:
        return -1
    except AttributeError: # catch other errors 
        return -1
    




def generate(intent,passback = False):
    """This function returns an appropriate response given a user's
    intent."""

    global responses # declare that we will use a global variable

    if intent == -1:
        if passback:
            return -1
        return "Sorry, I don't know the answer to that!"

    return responses[intent]



## Main Function

def checkRegex(prompt,botId = "user"):
    global PROGRAM_PATH
    index = 0
    for rxCheck in simpleFunctions.readRegexQuestions(f"{PROGRAM_PATH}config/regexAnswers",find = ["{msg.guild.me.id}"],replaceWith = [botId]):
        if re.findall(rf'{rxCheck}',prompt.lower(),flags=re.IGNORECASE):
            print(f"trigged regex:\n{rxCheck}")
            return index
        index+=1
    return -1

async def normalMSG(msg):
    global intents
    global responses

    intents,responses = load_FAQ_data(msg)




    #joke / easter egg
    if msg.content.lower() == "rick and morty":
        return ("What is my purpose?")
    if msg.content.lower() == "you pass butter":
        return ("oh my god :(\nhttps://www.youtube.com/watch?v=sa9MpLXuLs0")
    
    msgRet = generate(understand(msg.content.lower(),msg.guild.me.id),True)
    if msgRet == -1:
        return None
    return msgRet

def runProg(var):
    global intents
    global responses
    intent,responses= load_FAQ_data()
    utterance = var.lower()
    intent = understand(utterance)
    return generate(intent)



def main():
    ## Load the questions and responses
    global intents
    global responses
    intent,responses= load_FAQ_data()
    """Implements a chat session in the shell."""
    print("Hello! I know stuff about chat bots. When you're done talking, just say 'goodbye'.")
    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    utterance = ""
    while True:
        utterance = input(">>> ").lower()
        if utterance == "goodbye":
            break;
        intent = understand(utterance)
        response = generate(intent)
        print(response)
        print()

    print("Nice talking to you!")

## Run the chat code
# the if statement checks whether or not this module is being run
# as a standalone module. If it is beign imported, the if condition
# will be false and it will not run the chat method.
if __name__ == "__main__":
    main()
