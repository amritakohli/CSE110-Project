import discord
import re
import pyrebase
import json
from urllib import request
from discord.ext import commands
from config import fireConfig

firebase = pyrebase.initialize_app(fireConfig)
db = firebase.database()

FOLDER_STR = 'Rules'
DEFAULT_RULES_NAME = 'DefaultRules'

# bot functions. the '@' line is important where it is used.
def setup(bot):
    bot.add_cog(RuleBot(bot))

class RuleBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['rule', 'Rule', 'Rules', 'listrule', 'listRules', 'listr', 'listR', 'showrule', 'showRule', 'showrules', 'showRules'], help='Lists rules on a server. Run with no commands for all rules, or with a rule number for a specific rule!')
    async def rules(self, ctx, a = None):
        if not db.child(ctx.guild.id).child(FOLDER_STR).get().val():
            ruleDict = self.default_Dict()
        else:
            ruleDict = {k: v for k, v in enumerate(db.child(ctx.guild.id).child(FOLDER_STR).get().val())}
        if not a:
            masterString = ''
            for key in ruleDict:
                curString = str(key) + ". "+ ruleDict[key]["title"] + ": " + ruleDict[key]["desc"] + '\n'
                if len(masterString) + len(curString) >= 700:
                    await ctx.send(masterString)
                    masterString = curString
                else:
                    masterString += curString
            if(masterString):
                await ctx.send(masterString)

                
        else:
            if not a.isnumeric():
                await ctx.send("Error: Not a valid rule number." + '\n' + "Please enter a non-negative number to view a specific rule, or no number to view all rules.")
            elif int(a) >= len(ruleDict):
                await ctx.send("Error: We do not have that many rules!")
            else:
                await ctx.send(a + ". "+ ruleDict[int(a)]["title"] + ": " + ruleDict[int(a)]["desc"]) 

    @commands.command(aliases = ['addrule', 'newrule', 'newRule', 'addr', 'addR', 'newr', 'newR'], help='Adds a new rule to the server. Format: !addRule "<RuleTitle>" <RuleDesc>')
    async def addRule(self, ctx, *, args = None):
        content = ctx.message.content
        newTitle = "**" + content.split('"')[1].strip() + "**"
        newDesc = content[content.rindex('"')+1:].strip()
        
        if not args:
            await ctx.send("Please enter a rule title and rule description with the format:\n!addrule \"title\" description")
        elif content.count('\"') != 2 or args[0] != '"':
            await ctx.send("Please enclose only the rule title in parentheses. There must be two parentheses in a command. The format to add a new rule is:\n!addrule \"title\" description")
        elif args[0] == '"' and args[1] == '"':
            await ctx.send("The rule must have a title. Please use the following format to add a new rule:\n!addrule \"title\" description")
        else:
            if not db.child(ctx.guild.id).child(FOLDER_STR).get().val():
                defDict = self.default_Dict()
                db.child(ctx.guild.id).child(FOLDER_STR).update(defDict)
            index = len(db.child(ctx.guild.id).child(FOLDER_STR).get().val())
            db.child(ctx.guild.id).child(FOLDER_STR).child(index).child("title").set(newTitle)
            db.child(ctx.guild.id).child(FOLDER_STR).child(index).child("desc").set(newDesc)
            await ctx.send("Rule added successfully!")

    @commands.command(aliases = ['deleterule', 'delrule', 'delRule', 'delr', 'delR', 'deleter', 'deleteR'], help='Deletes rule from the server. Format: !delRule <RuleNum>')
    async def deleteRule(self, ctx, a = None):
        if not db.child(ctx.guild.id).child(FOLDER_STR).get().val():
                defDict = self.default_Dict()
                db.child(ctx.guild.id).child(FOLDER_STR).update(defDict)
        if not a:
            await ctx.send("Please enter a rule number to delete. If you do not know the number for a rule, enter !rules to see all the rules with their numbers.")
        elif not a.isnumeric():
            await ctx.send("Please enter a rule number to delete.")
        elif int(a) == 0:
            await ctx.send("Cannot delete rule 0: the welcome message.")
        elif int(a) >= len(db.child(ctx.guild.id).child(FOLDER_STR).get().val()):
            await ctx.send("Invalid rule number.")
        else:
            delDict = {k: v for k, v in enumerate(db.child(ctx.guild.id).child(FOLDER_STR).get().val())}
            if int(a) == len(db.child(ctx.guild.id).child(FOLDER_STR).get().val())-1:
                del delDict[int(a)]
            else:
                for i in range(int(a), len(delDict)-1):
                    delDict[i] = delDict.pop(i+1)
            db.child(ctx.guild.id).child(FOLDER_STR).set(delDict)
            await ctx.send("Rule deleted successfully.")

    @commands.command(aliases = ['swaprule','swaprules', 'swapRules', 'switchrules', 'switchRule', 'swap', 'switch'], help='Switches two rules on the list.  Format: !swap <RuleOne> <RuleTwo>')
    async def swapRule(self, ctx, a = None, b = None):
        if not db.child(ctx.guild.id).child(FOLDER_STR).get().val():
                defDict = self.default_Dict()
                db.child(ctx.guild.id).child(FOLDER_STR).update(defDict)
        length = len(db.child(ctx.guild.id).child(FOLDER_STR).get().val())
        if not a or not b:
            await ctx.send("Error: Please enter two rule numbers to swap.")
        elif not a.isnumeric():
            await ctx.send("Error: First value to swap is not numeric.")
        elif not b.isnumeric:
            await ctx.send("Error: Second value to swap is not numeric.")
        elif int(a) == 0 or int(b) == 0:
            await ctx.send("Error: Cannot swap rule 0: the welcome message")
        elif int(a) >= length:
            await ctx.send("Error: First value is too big! We don't have that many rules")
        elif int(b) >= length:
            await ctx.send("Error: Second value is too big! We don't have that many rules")
        else:
            swapDict = {k: v for k, v in enumerate(db.child(ctx.guild.id).child(FOLDER_STR).get().val())}
            swapDict[int(a)], swapDict[int(b)] = swapDict[int(b)], swapDict[int(a)]
            db.child(ctx.guild.id).child(FOLDER_STR).set(swapDict)
            await ctx.send("Rules swapped successfully")

    def default_Dict(self):
        return {k: v for k, v in enumerate(db.child(DEFAULT_RULES_NAME).get().val())}