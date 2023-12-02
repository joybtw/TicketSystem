from discord.ext import commands

class Admin(commands.Cog): 
    pass


async def setup(bot): 
    await bot.add_cog(Admin(bot))