"""This game is only for 2 players ! (Will be updated soon !)"""
from discord.ext import commands
import discord, asyncio, random
try:
    from src.secret import time
    from src.secret import color
    from src.secret import color_white
    from src.secret import color_red
    from src.secret import color_green
    from src.secret import myID
    from src.secret import BotID
except ModuleNotFoundError:
    print("Make sure you have all files in your path ! See all files here: https://github.com/Bmbus")
from PIL import Image
import os

def only_dm():
    def lul(ctx):
        return ctx.guild is None
    return commands.check(lul)

class TicTacToe:
    def __init__(self,bot):
        self.bot = bot
        self.field_demo = ["set:1","set:2","set:3",
                           "set:4","set:5","set:6",
                           "set:7","set:8","set:9"]
        self.pic_paste = {"set:1": (0, 0), "set:2": (150, 0), "set:3": (285, 0), "set:4": (0, 146), "set:5": (150, 146), "set:6": (287, 148), "set:7": (0, 296), "set:8": (152, 294), "set:9": (286, 292)}
        self.queue = []
        self.taken_p1 = []
        self.taken_p2 = []
        self.taken = []
        self.server_l = []
        self.channel = []
        self.user_starts_dic = {"player_turn":str}
        self.game_num = 0

    @commands.command(name="ttt") # TODO  queue will be updated soon !
    @only_dm()
    async def tttqueue(self,ctx):
        await self.start(ctx.message.author)

    async def start(self,user):
        try:
            if not user.id in self.queue and len(self.queue) == 0:
                self.queue.insert(1,user.id)
                embed = discord.Embed(title="Tic-Tac-Toe", color=color)
                embed.add_field(name="Successful added to queue !", value="Waiting for opponent...")
                embed.set_footer(text=time)
                self.search_msg = await user.send(embed=embed)
            elif not user.id in self.queue and len(self.queue) == 1 and not user.id == BotID:
                self.queue.insert(2, user.id)
                embed = discord.Embed(title="Tic-Tac-Toe", color=color)
                embed.add_field(name="Successful added to queue !",value=f"Your opponent is <@{self.queue[0]}>\n""Game starts in 3 seconds..")
                embed.set_footer(text=time)
                await user.send(embed=embed)
                self.p1 = self.bot.get_user(self.queue[0])
                self.p2 = self.bot.get_user(user.id)
                embed = discord.Embed(title="Tic-Tac-Toe", color=color)
                embed.add_field(name="Successful added to queue!", value=f"Your opponent is <@{self.queue[1]}>\n""Game starts in 3 seconds..")
                await self.search_msg.edit(embed=embed)
                await self.start_match(self.p1, self.p2)
            elif not user.id in self.queue and len(self.queue) == 2:
                await user.send("Game in progress.. pls wait !")
            elif user.id in self.queue:
                await user.send("`You're already in a game!`")
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def start_match(self,p1,p2):
        try:
            self.server = await self.bot.create_guild(name=f"{p1} vs. {p2}", region=discord.VoiceRegion.eu_central)
            self.server_l.append(self.server.id)
            self.ch1 = await self.server.create_text_channel(name=f"{p1}")
            self.channel.append(self.ch1.id)
            self.ch2 = await self.server.create_text_channel(name=f"{p2}")
            self.channel.append(self.ch2.id)
            for tch in self.server.text_channels:
                invite = await tch.create_invite()
                await p1.send(f"Please join this server in the next 15 seconds: {invite}")
                await p2.send(f"Please join this server in the next 15 seconds: {invite}")
                break
            await asyncio.sleep(15)
            await self.ch1.set_permissions(p2, read_messages=False)
            await self.ch2.set_permissions(p1, read_messages=False)
            embed = discord.Embed(title="Tic-Tac-Toe", description=f"Hello {p1} !", color=color)
            embed.add_field(name="Explanation:", value=f"Type in `set:number` to set your icon!", inline=False)
            embed.add_field(name="Panel design:", value="1 2 3\n"
                                                        "4 5 6\n"
                                                        "7 8 9", inline=False)
            embed.add_field(name="Good luck 🍀🍀", value="The game starts in 10 seconds", inline=False)
            embed.set_author(name="Player_1 - Green")
            await self.ch1.send(embed=embed)
            embed1 = discord.Embed(title="Tic-Tac-Toe", description=f"Hello {p2} !", color=color)
            embed1.add_field(name="Explanation:", value=f"Type in `set:number` to set your icon!", inline=False)
            embed1.add_field(name="Panel design:", value="1 2 3\n"
                                                         "4 5 6\n"
                                                         "7 8 9", inline=False)
            embed1.add_field(name="Good luck 🍀🍀", value="The game starts in 10 seconds", inline=False)
            embed1.set_author(name="Player_2 - Blue")
            await self.ch2.send(embed=embed1)
            await asyncio.sleep(10)
            user_starts = random.choice(self.queue)
            start_embed = discord.Embed(title="The game starts !", color=color, description=f"<@{user_starts}> begins!")
            self.user_starts_dic["player_turn"] = str(user_starts)
            await self.ch1.send(embed=start_embed)
            await self.ch2.send(embed=start_embed)
            self.create_new_field(self.server)
            await self.send_field(self.ch1,self.ch2,self.server)
        except discord.errors.NotFound:
            await self.game_stops(self.server,p1,p2, "someone didn't join the server")
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    def create_new_field(self,server):
        try:
            field_def = Image.open("img/tic-tac-toe.png")
            field_def.save(f"img/{server.id}.png")
        except FileNotFoundError:
            print("I couldn't find the file 'tic-tac-toe.png'! Make sure you have all files downloaded, GitHub: https://github.com/Bmbus")

    async def send_field(self,ch1,ch2,server):
        try:
            field_send = discord.File(fp=f"img/{server.id}.png")
            await ch1.send(file=field_send)
            await ch2.send(file=field_send)
        except discord.errors.NotFound:
            pass
        except FileNotFoundError:
            await self.game_stops(self.server,self.p1,self.p2, "I couldn't find the file")
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def on_message(self,message):
        try:
            if message.channel.id in self.channel and message.author.id in self.queue:
                if message.content in self.field_demo:
                    if message.content not in self.taken and str(message.author.id) == self.user_starts_dic["player_turn"] and str(self.p1.id) == self.user_starts_dic["player_turn"]:
                        await self.bot_calc(message.content,self.server,True,message.channel)
                        self.user_starts_dic["player_turn"] = str(self.p2.id)
                        await self.ch2.send(f"{self.p2.mention} it's your turn !")
                    elif message.content not in self.taken and str(message.author.id) == self.user_starts_dic["player_turn"] and str(self.p2.id) == self.user_starts_dic["player_turn"]:
                        await self.bot_calc(message.content,self.server,False,message.channel)
                        self.user_starts_dic["player_turn"] = str(self.p1.id)
                        await self.ch1.send(f"{self.p1.mention} it's your turn !")
                    elif str(message.author.id) != self.user_starts_dic["player_turn"]:
                        await message.channel.send(f'Its not your turn, please wait for <@{self.user_starts_dic["player_turn"]}>')
                    elif message.content in self.taken:
                        await message.channel.send("This number is already taken, please take an other !")
        except discord.errors.NotFound:
            pass
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def bot_calc(self,user_input,server,p1_starts_:bool,ch):
        try:
            input = str(user_input).split(":")
            p1_pic = Image.open("img/player_one.png")
            p2_pic = Image.open("img/player_two.png")
            if p1_starts_:
                if int(input[1]) == 1:
                    self.taken_p1.append(1)
                    self.taken.append("set:1")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic,self.pic_paste["set:1"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 2:
                    self.taken_p1.append(2)
                    self.taken.append("set:2")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:2"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 3:
                    self.taken_p1.append(3)
                    self.taken.append("set:3")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:3"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 4:
                    self.taken_p1.append(4)
                    self.taken.append("set:4")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:4"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 5:
                    self.taken_p1.append(5)
                    self.taken.append("set:5")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:5"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 6:
                    self.taken_p1.append(6)
                    self.taken.append("set:6")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:6"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 7:
                    self.taken_p1.append(7)
                    self.taken.append("set:7")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:7"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 8:
                    self.taken_p1.append(8)
                    self.taken.append("set:8")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:8"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 9:
                    self.taken_p1.append(9)
                    self.taken.append("set:9")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p1_pic, self.pic_paste["set:9"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) > 9:
                    await self.ch1.send("Invalid input ! Try a number from `1 - 9`!")
                await self.check_won()
            else:
                if int(input[1]) == 1:
                    self.taken_p2.append(1)
                    self.taken.append("set:1")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic,self.pic_paste["set:1"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 2:
                    self.taken_p2.append(2)
                    self.taken.append("set:2")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:2"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 3:
                    self.taken_p2.append(3)
                    self.taken.append("set:3")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:3"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 4:
                    self.taken_p2.append(4)
                    self.taken.append("set:4")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:4"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 5:
                    self.taken_p2.append(5)
                    self.taken.append("set:5")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:5"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 6:
                    self.taken_p2.append(6)
                    self.taken.append("set:6")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:6"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 7:
                    self.taken_p2.append(7)
                    self.taken.append("set:7")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:7"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 8:
                    self.taken_p2.append(8)
                    self.taken.append("set:8")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:8"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) == 9:
                    self.taken_p2.append(9)
                    self.taken.append("set:9")
                    field_load = Image.open(f"img/{server.id}.png")
                    field_load.paste(p2_pic, self.pic_paste["set:9"])
                    field_load.save(f"img/{server.id}.png")
                    await self.send_calc()
                elif int(input[1]) > 9:
                    await self.ch2.send("Invalid input ! Try a number from `1 - 9`!")
                await self.check_won()
        except discord.errors.NotFound:
            pass
        except IndexError:
            pass
        except ValueError:
            pass
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def send_calc(self):
        try:
            field_send = discord.File(fp=f"img/{self.server.id}.png")
            await self.ch1.send(file=field_send)
            await self.ch2.send(file=field_send)
        except FileNotFoundError:
            await self.game_stops(self.server,self.p1,self.p2,"I couldn't find the file")
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def check_won(self):
        try:
            if 1 in self.taken_p1 and 2 in self.taken_p1 and 3 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 1 in self.taken_p1 and 4 in self.taken_p1 and 7 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 1 in self.taken_p1 and 5 in self.taken_p1 and 9 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 2 in self.taken_p1 and 5 in self.taken_p1 and 8 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 3 in self.taken_p1 and 5 in self.taken_p1 and 7 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 3 in self.taken_p1 and 6 in self.taken_p1 and 9 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1, self.p2, self.ch1, self.ch2,False)
            elif 4 in self.taken_p1 and 5 in self.taken_p1 and 6 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1,self.p2,self.ch1,self.ch2,False)
            elif 7 in self.taken_p1 and 8 in self.taken_p1 and 9 in self.taken_p1:
                self.delete_img()
                await self.won(self.p1,self.p2,self.ch1,self.ch2,False)
            # player2 taken
            elif 1 in self.taken_p2 and 2 in self.taken_p2 and 3 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 1 in self.taken_p2 and 4 in self.taken_p2 and 7 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 1 in self.taken_p2 and 5 in self.taken_p2 and 9 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 2 in self.taken_p2 and 5 in self.taken_p2 and 8 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 3 in self.taken_p2 and 5 in self.taken_p2 and 7 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 3 in self.taken_p2 and 6 in self.taken_p2 and 9 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 4 in self.taken_p2 and 5 in self.taken_p2 and 6 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            elif 7 in self.taken_p2 and 8 in self.taken_p2 and 9 in self.taken_p2:
                self.delete_img()
                await self.won(self.p2, self.p1, self.ch2, self.ch1,False)
            #draw
            elif len(self.taken) == 9:
                self.delete_img()
                await self.won(self.p1,self.p2,self.ch1,self.ch2,True)
        except discord.errors.NotFound:
            pass
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def game_stops(self,server,p1,p2,reason:str):
        try:
            emded = discord.Embed(title="The game stops !", color=color_red,
                                  description=f"The game stops, because {reason} !\n""Please try again later!")
            emded.add_field(name="Check if you downloaded all files/folders",value="GitHub: https://github.com/Bmbus",inline=False)
            emded.set_author(name="Error-message",url="https://github.com/Bmbus")
            emded.set_footer(text=time)
            await p1.send(embed=emded)
            await p2.send(embed=emded)
            await asyncio.sleep(10)
            await self.delete_img()
            await self.delete_all(server)
        except discord.errors.NotFound:
            pass
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    def delete_img(self):
        try:
           os.remove(f"img/{self.server.id}.png")
        except FileNotFoundError:
            pass

    async def won(self,player_won, player_lose, player_won_ch, player_lose_ch,draw:bool):
        try:
            if draw:
                drawembed = discord.Embed(title="DRAWN", color=color_white, description="Nobody won the game!\n""Try again")
                await player_won_ch.send(embed=drawembed)
                await player_lose_ch.send(embed=drawembed)
                await asyncio.sleep(10)
                await self.delete_all(self.server)
            else:
                wonembed = discord.Embed(title=f"{player_won} won the game !", color=color_green)
                wonembed.add_field(name="Say 'GG' !", value="The server will be deleted in 10 sec!", inline=False)
                loseembed = discord.Embed(title=f"{player_lose} lose !", color=color_red)
                loseembed.add_field(name="Say 'GG' !", value="The server will be deleted in 10 seconds!", inline=False)
                await player_lose_ch.send(embed=loseembed)
                await player_won_ch.send(embed=wonembed)
                await asyncio.sleep(10)
                self.delete_img()
                await self.delete_all(self.server)
        except discord.errors.NotFound:
            pass
        except Exception as error:
            self.delete_img()
            await self.send_error(error)

    async def send_error(self,error):
        try:
            emded = discord.Embed(title="The game stops !", color=color_red, description="Please try again later !")
            emded.add_field(name="There is an error:", value=error)
            emded.add_field(name="Check if you downloaded all files/folders", value="GitHub: https://github.com/Bmbus",inline=False)
            emded.set_author(name="Error-message", url="https://github.com/Bmbus")
            emded.set_footer(text=time)
            await self.p1.send(embed=emded)
            await self.p2.send(embed=emded)
            self.delete_img()
            await self.delete_all(self.server)
        except discord.errors.NotFound:
            pass

    async def delete_all(self,server):
        try:
            del self.queue[:]
            del self.server_l[:]
            del self.taken_p1[:]
            del self.taken_p2[:]
            del self.channel[:]
            del self.taken[:]
            await server.delete()
        except discord.errors.NotFound:
            pass
