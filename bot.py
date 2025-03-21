import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定機器人權限
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True  # 需要這個權限來獲取成員暱稱

# 建立機器人實例
bot = commands.Bot(command_prefix='!', intents=intents)

# 儲存投票結果的字典
poll_messages = {}

@bot.event
async def on_ready():
    print(f'{bot.user} 已上線！')
    # 啟動定時發送投票的任務
    daily_game_poll.start()

# 設定每天晚上 7:30 發送投票
@tasks.loop(time=datetime.time(hour=19, minute=30))
async def daily_game_poll():
    channel_id = int(os.getenv('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)
    
    if channel:
        await send_poll(channel)

# 新增手動觸發投票的命令
@bot.command(name="poll")
async def manual_poll(ctx):
    await send_poll(ctx.channel)
    await ctx.message.add_reaction('👍')  # 反應表示指令成功執行

# 發送投票的共用函數
async def send_poll(channel):
    # 建立投票訊息
    embed = discord.Embed(
        title="今天有沒有要玩?",
        description="請點擊下方按鈕投票",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"投票於 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 建立按鈕
    view = GamePollView()
    
    # 發送投票訊息
    poll_msg = await channel.send(embed=embed, view=view)
    
    # 儲存訊息以便稍後統計
    poll_messages[poll_msg.id] = {
        'message': poll_msg,
        'view': view
    }
    
    # 設定 1 小時後關閉投票
    await asyncio.sleep(3600)  # 1小時 = 3600秒
    await close_poll(poll_msg.id)

# 定義投票的視圖和按鈕
class GamePollView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.yes_votes = set()
        self.no_votes = set()
    
    @discord.ui.button(label="要", style=discord.ButtonStyle.green, custom_id="vote_yes")
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 如果使用者原本選了"不要"，將其從不要清單中移除
        if interaction.user.id in self.no_votes:
            self.no_votes.remove(interaction.user.id)
        
        # 將使用者加入到要清單中
        self.yes_votes.add(interaction.user.id)
        
        await update_results(interaction)
    
    @discord.ui.button(label="不要", style=discord.ButtonStyle.red, custom_id="vote_no")
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 如果使用者原本選了"要"，將其從要清單中移除
        if interaction.user.id in self.yes_votes:
            self.yes_votes.remove(interaction.user.id)
        
        # 將使用者加入到不要清單中
        self.no_votes.add(interaction.user.id)
        
        await update_results(interaction)

# 更新投票結果
async def update_results(interaction):
    view = None
    for poll_id, poll_data in poll_messages.items():
        if poll_data['message'].id == interaction.message.id:
            view = poll_data['view']
            break
    
    if view:
        yes_count = len(view.yes_votes)
        no_count = len(view.no_votes)
        
        # 獲取投票者名稱 (使用伺服器暱稱)
        yes_voters = []
        no_voters = []
        
        for user_id in view.yes_votes:
            member = interaction.guild.get_member(user_id)
            if member:
                yes_voters.append(member.display_name)
        
        for user_id in view.no_votes:
            member = interaction.guild.get_member(user_id)
            if member:
                no_voters.append(member.display_name)
        
        # 更新嵌入消息
        embed = interaction.message.embeds[0]
        
        # 清晰顯示所有已投票的使用者名稱
        yes_voters_list = "無" if not yes_voters else ", ".join(yes_voters)
        no_voters_list = "無" if not no_voters else ", ".join(no_voters)
        
        embed.description = f"請點擊下方按鈕投票\n\n**要**: {yes_count} 人\n{yes_voters_list}\n\n**不要**: {no_count} 人\n{no_voters_list}"
        
        await interaction.response.edit_message(embed=embed)

# 關閉投票
async def close_poll(poll_id):
    if poll_id in poll_messages:
        poll_data = poll_messages[poll_id]
        view = poll_data['view']
        message = poll_data['message']
        
        # 取得最終結果
        yes_count = len(view.yes_votes)
        no_count = len(view.no_votes)
        
        # 獲取投票者名稱 (使用伺服器暱稱)
        yes_voters = []
        no_voters = []
        
        guild = message.guild
        for user_id in view.yes_votes:
            member = guild.get_member(user_id)
            if member:
                yes_voters.append(member.display_name)
        
        for user_id in view.no_votes:
            member = guild.get_member(user_id)
            if member:
                no_voters.append(member.display_name)
        
        yes_voters_list = "無" if not yes_voters else ", ".join(yes_voters)
        no_voters_list = "無" if not no_voters else ", ".join(no_voters)
        
        # 建立結果訊息
        result_text = f"**投票結果**\n要玩: {yes_count} 人 ({yes_voters_list})\n不玩: {no_count} 人 ({no_voters_list})"
        
        # 停用按鈕
        for child in view.children:
            child.disabled = True
        
        # 更新原始投票訊息
        embed = discord.Embed(
            title="投票已結束: 今天有沒有要玩?",
            description=result_text,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"投票於 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} 結束")
        
        await message.edit(embed=embed, view=view)
        
        # 移除已關閉的投票
        del poll_messages[poll_id]

# 新增取消現有投票的命令
@bot.command(name="cancelpoll")
async def cancel_poll(ctx):
    for poll_id, poll_data in list(poll_messages.items()):
        if poll_data['message'].channel.id == ctx.channel.id:
            view = poll_data['view']
            message = poll_data['message']
            
            # 停用按鈕
            for child in view.children:
                child.disabled = True
            
            embed = message.embeds[0]
            embed.title = "投票已取消"
            embed.color = discord.Color.light_grey()
            
            await message.edit(embed=embed, view=view)
            await ctx.send("投票已取消")
            
            # 移除已取消的投票
            del poll_messages[poll_id]
            return
    
    await ctx.send("在此頻道中找不到活動中的投票")

# 啟動機器人
if __name__ == "__main__":
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("錯誤：未設定 BOT_TOKEN 環境變數")
    else:
        bot.run(bot_token)
