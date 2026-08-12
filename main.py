import discord
from discord.ext import commands
import asyncio
import logging

import config
from database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("z9x-bot")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

INITIAL_COGS = [
    "cogs.tickets",
    "cogs.moderation",
    "cogs.welcome",
    "cogs.leveling",
]


@bot.event
async def on_ready():
    log.info(f"تم تسجيل الدخول باسم {bot.user} (ID: {bot.user.id})")
    try:
        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
        else:
            synced = await bot.tree.sync()
        log.info(f"تمت مزامنة {len(synced)} أمر سلاش.")
    except Exception as e:
        log.error(f"خطأ أثناء مزامنة الأوامر: {e}")

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{config.SERVER_NAME} 🛡️")
    )


async def main():
    init_db()
    async with bot:
        for cog in INITIAL_COGS:
            try:
                await bot.load_extension(cog)
                log.info(f"تم تحميل {cog}")
            except Exception as e:
                log.error(f"فشل تحميل {cog}: {e}")
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    if not config.TOKEN:
        raise SystemExit("خطأ: TOKEN غير موجود. تأكد من ملف settings.env")
    asyncio.run(main())
