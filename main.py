import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
import json
import os
import random
import asyncio
from datetime import datetime, timedelta

# ==================== CONFIG ====================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ ERROR: TOKEN not found!")
    print("Please add TOKEN in Environment Variables")
    exit(1)

DB_FILE = "z9x_scripts.json"

# ==================== FIX: Create JSON if missing ====================
def ensure_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "mm2": [
                    {
                        "map": "MM2",
                        "code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Murder-Mystery-2-KEYLESS-InstaWin-AutoFarm-Kill-all-XRay-nd-more-by-Moondiety-48644"))()',
                        "image": "https://tr.rbxcdn.com/30DAY-AvatarLaunch-0bc0db1e9c8e4c0f8c0e8c0e8c0e8c0e8c0e8c0e8/352/352/Avatar/Png/noFilter",
                        "has_key": False,
                        "working": True,
                        "trusted": True,
                        "time_ago": "a year ago",
                        "date": "2025/08/15",
                        "last_update": "غير معروف"
                    }
                ],
                "zombie attack": [
                    {
                        "map": "Zombie Attack",
                        "code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Zombie-Attack-Projeto-LKB-I-New-Gen-15535"))()',
                        "image": "https://tr.rbxcdn.com/30DAY-AvatarLaunch-0bc0db1e9c8e4c0f8c0e8c0e8c0e8c0e8c0e8c0e8/352/352/Avatar/Png/noFilter",
                        "has_key": False,
                        "working": True,
                        "trusted": True,
                        "time_ago": "2 years ago",
                        "date": "2024/07/14",
                        "last_update": "غير معروف"
                    }
                ]
            }, f, ensure_ascii=False, indent=2)

def load_db():
    ensure_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== SCRIPT NAVIGATOR ====================
class ScriptNavigator(View):
    def __init__(self, scripts):
        super().__init__(timeout=300)
        self.scripts = scripts
        self.index = 0
        self._update_buttons()
    
    def _update_buttons(self):
        self.clear_items()
        prev = Button(label="السابق ⬅️", style=discord.ButtonStyle.blurple, disabled=(self.index == 0))
        prev.callback = self._prev
        self.add_item(prev)
        nxt = Button(label="التالي ➡️", style=discord.ButtonStyle.blurple, disabled=(self.index == len(self.scripts) - 1))
        nxt.callback = self._next
        self.add_item(nxt)
        copy = Button(label="نسخ السكربت 📋", style=discord.ButtonStyle.green)
        copy.callback = self._copy
        self.add_item(copy)
    
    def _build_embed(self):
        s = self.scripts[self.index]
        embed = discord.Embed(color=0x2b2d31)
        key_status = "يوجد مفتاح ✅" if s.get('has_key') else "لا يوجد مفتاح ❌"
        embed.add_field(name="الفتح 🔑", value=key_status, inline=False)
        work_status = "مصحح ✅" if s.get('working') else "معطل ❌"
        embed.add_field(name="مصحح ⚙️", value=work_status, inline=False)
        time_str = f"انصنع قبل: {s.get('time_ago', 'غير معروف')}"
        if s.get('date'):
            time_str += f"\n📅 ({s.get('date')})"
        embed.add_field(name="وقت السكربت 🕐", value=time_str, inline=False)
        embed.add_field(name="آخر تحديث له 🔄", value=s.get('last_update', 'غير معروف'), inline=False)
        code = s.get('code', '')
        embed.add_field(name="السكربت 📜", value=f"```lua\n{code}\n```", inline=False)
        if s.get('image'):
            embed.set_image(url=s['image'])
        embed.set_footer(text=f"الصفحة {self.index + 1} من {len(self.scripts)} 📄 | Z9X Bot")
        return embed
    
    async def _prev(self, interaction: discord.Interaction):
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)
    
    async def _next(self, interaction: discord.Interaction):
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)
    
    async def _copy(self, interaction: discord.Interaction):
        code = self.scripts[self.index].get('code', '')
        await interaction.response.send_message(f"```lua\n{code}\n```\n✅ انسخ الكود فوق!", ephemeral=True)

# ==================== FILTER MENU ====================
class FilterMenu(View):
    def __init__(self, query):
        super().__init__(timeout=120)
        self.query = query
        self.key_filter = "all"
        self.trust_filter = "all"
        self._build()
    
    def _build(self):
        self.clear_items()
        key_sel = Select(
            placeholder="اختر نوع المفتاح",
            options=[
                discord.SelectOption(label="بمفتاح 🔑", value="true", description="السكربتات التي تحتاج مفتاحاً"),
                discord.SelectOption(label="بدون مفتاح 🚫", value="false", description="السكربتات التي لا تحتاج مفتاحاً"),
                discord.SelectOption(label="كلاهما 🔄", value="all", description="عرض النوعين معاً"),
            ],
            row=0
        )
        key_sel.callback = self._on_key
        self.add_item(key_sel)
        trust_sel = Select(
            placeholder="اختر حالة الموثوقية",
            options=[
                discord.SelectOption(label="موثوق ✅", value="true", description="السكربتات الموثوقة من المصدر"),
                discord.SelectOption(label="غير موثوق ❌", value="false", description="السكربتات غير الموثوقة"),
                discord.SelectOption(label="كلاهما 🔄", value="all", description="عرض الحالتين معاً"),
            ],
            row=1
        )
        trust_sel.callback = self._on_trust
        self.add_item(trust_sel)
        btn = Button(label="🔍 جاري البحث، الرجاء الانتظار...", style=discord.ButtonStyle.grey, disabled=True, row=2)
        btn.callback = self._search
        self.add_item(btn)
        self.search_btn = btn
    
    async def _on_key(self, interaction: discord.Interaction):
        self.key_filter = interaction.data['values'][0]
        self.search_btn.disabled = False
        self.search_btn.label = "🔍 ابدأ البحث"
        self.search_btn.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self)
    
    async def _on_trust(self, interaction: discord.Interaction):
        self.trust_filter = interaction.data['values'][0]
        self.search_btn.disabled = False
        self.search_btn.label = "🔍 ابدأ البحث"
        self.search_btn.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self)
    
    async def _search(self, interaction: discord.Interaction):
        db = load_db()
        results = []
        for map_name, scripts in db.items():
            if self.query.lower() in map_name.lower():
                for s in scripts:
                    if self.key_filter != "all":
                        if str(s.get('has_key', False)).lower() != self.key_filter:
                            continue
                    if self.trust_filter != "all":
                        if str(s.get('trusted', True)).lower() != self.trust_filter:
                            continue
                    results.append(s)
        if not results:
            await interaction.response.send_message("❌ ما لقيت نتائج بهذه الفلاتر", ephemeral=True)
            return
        view = ScriptNavigator(results)
        await interaction.response.edit_message(embed=view._build_embed(), view=view)

# ==================== COMMANDS ====================
@bot.tree.command(name="search", description="🔍 ابحث عن سكربتات ماب روبلوكس")
@app_commands.describe(query="اسم الماب (مثال: MM2, Blox Fruits)")
async def search_cmd(interaction: discord.Interaction, query: str):
    db = load_db()
    if not any(query.lower() in k.lower() for k in db.keys()):
        await interaction.response.send_message(f"❌ ما في ماب مسجل باسم **{query}**", ephemeral=True)
        return
    embed = discord.Embed(title="🔍 اختر نوع المفتاح وحالة الموثوقية قبل بدء البحث", color=0x2b2d31)
    await interaction.response.send_message(embed=embed, view=FilterMenu(query))

@bot.tree.command(name="addscript", description="➕ إضافة سكربت جديد (للأدمن فقط)")
@app_commands.describe(
    map_name="اسم الماب",
    code="كود السكربت الكامل",
    image="رابط صورة الماب",
    has_key="هل يحتاج مفتاح؟",
    working="هل السكربت شغال؟",
    trusted="هل المصدر موثوق؟"
)
async def addscript_cmd(
    interaction: discord.Interaction,
    map_name: str,
    code: str,
    image: str = None,
    has_key: bool = False,
    working: bool = True,
    trusted: bool = True
):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ للأدمن فقط!", ephemeral=True)
    db = load_db()
    key = map_name.lower()
    if key not in db:
        db[key] = []
    db[key].append({
        "map": map_name, "code": code, "image": image,
        "has_key": has_key, "working": working, "trusted": trusted,
        "time_ago": "الآن", "date": "", "last_update": "غير معروف"
    })
    save_db(db)
    embed = discord.Embed(title="✅ تمت الإضافة", description=f"تم إضافة السكربت لماب **{map_name}**", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="maps", description="📋 عرض كل المابات المتوفرة")
async def maps_cmd(interaction: discord.Interaction):
    db = load_db()
    if not db:
        return await interaction.response.send_message("❌ لا توجد مابات مسجلة", ephemeral=True)
    embed = discord.Embed(title="📋 المابات المتوفرة في Z9X", description="استخدم `/search` للبحث", color=0x5865f2)
    for map_name, scripts in db.items():
        embed.add_field(name=f"🎮 {map_name.title()}", value=f"{len(scripts)} سكربت", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tiktok", description="📱 تحميل فيديو تيك توك بدون علامة مائية")
@app_commands.describe(url="رابط فيديو تيك توك")
async def tiktok_cmd(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=True)
    embed = discord.Embed(
        title="📱 TikTok Downloader",
        description=f"**الرابط:** {url}\n\n⚡ للتحميل بدون علامة مائية:\n[SSSTik](https://ssstik.io) | [SnapTik](https://snaptik.app)",
        color=0xff0050
    )
    await interaction.followup.send(embed=embed)

giveaways = {}

@bot.tree.command(name="giveaway", description="🎉 إنشاء فعالية Giveaway")
@app_commands.describe(prize="الجائزة", duration="المدة بالدقائق", winners="عدد الفائزين")
async def giveaway_cmd(interaction: discord.Interaction, prize: str, duration: int, winners: int = 1):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ للأدمن فقط!", ephemeral=True)
    end = discord.utils.utcnow() + timedelta(minutes=duration)
    embed = discord.Embed(
        title=f"🎉 فعالية: {prize}",
        description=f"اضغط على 🎉 للمشاركة!\n⏰ المدة: {duration} دقيقة\n🏆 الفائزين: {winners}\n🕐 ينتهي: <t:{int(end.timestamp())}:R>",
        color=discord.Color.gold(),
        timestamp=end
    )
    embed.set_footer(text=f"منشئ: {interaction.user.name}")
    await interaction.response.send_message("🎉 جاري الإنشاء...")
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")
    giveaways[msg.id] = {"prize": prize, "winners": winners, "channel_id": interaction.channel_id}
    await asyncio.sleep(duration * 60)
    try:
        ch = bot.get_channel(interaction.channel_id)
        msg = await ch.fetch_message(msg.id)
        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        if reaction:
            users = [u async for u in reaction.users() if not u.bot]
            if users:
                wins = random.sample(users, min(winners, len(users)))
                wembed = discord.Embed(title="🎉 انتهت الفعالية!", description=f"**الجائزة:** {prize}\n**الفائزين:** {', '.join([w.mention for w in wins])}", color=discord.Color.green())
                return await ch.send(embed=wembed)
        await ch.send("❌ لم يشارك أحد!")
    except Exception as e:
        print(f"Giveaway Error: {e}")

@bot.tree.command(name="help", description="ℹ️ عرض كل أوامر البوت")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 أوامر بوت Z9X", color=0x5865f2)
    embed.add_field(name="`/search [ماب]`", value="🔍 بحث متقدم مع فلترة", inline=False)
    embed.add_field(name="`/addscript`", value="➕ إضافة سكربت (أدمن)", inline=False)
    embed.add_field(name="`/maps`", value="📋 عرض المابات", inline=False)
    embed.add_field(name="`/tiktok [رابط]`", value="📱 تحميل تيك توك", inline=False)
    embed.add_field(name="`/giveaway`", value="🎉 فعالية جيف أوي", inline=False)
    embed.add_field(name="`/help`", value="ℹ️ المساعدة", inline=False)
    embed.set_footer(text="Z9X Bot | مطور خصيصاً لسيرفرك")
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} Online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync error: {e}")

bot.run(TOKEN)
