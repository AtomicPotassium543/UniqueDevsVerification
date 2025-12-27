import disnake
from disnake.ext import commands, tasks
from disnake import TextInputStyle
from dotenv import load_dotenv
import pymongo
import config
import os

load_dotenv()

skills = [role for role in config.verification_roles]

class Revoke_command(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = pymongo.MongoClient(os.getenv("CLUSTER"))
        self.db = self.client[config.db]
        self.review = self.db["review"]
        self.roles = self.db["roles"]

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        if "revoke_modal-" in inter.custom_id:
            await inter.response.defer(ephemeral=True)

            data = (inter.custom_id).replace("-", " ")

            new = data.split()

            main_guild = await self.bot.fetch_guild(config.Main_server)

            admin_guild = await self.bot.fetch_guild(config.Admin_server)

            log_channel = await admin_guild.fetch_channel(config.logs_channel)

            reason = inter.text_values.get("rejection_reason")

            member = await main_guild.fetch_member(int(new[1]))

            skill = new[2]

            role = main_guild.get_role(config.verification_roles[skill]["Id"])

            target_info = self.roles.find_one({"user_id": member.id})

            roles = list(target_info["obtained"])

            roles.remove(skill)

            await member.remove_roles(role)

            self.roles.update_one({"user_id": member.id}, {"$set": {"obtained": roles}})

            embed = disnake.Embed(
                title=f'Hello there!',
                description=f'Unfortunately, your skill role for ``{skill}`` has been revoked for:\n```"{reason}"```\nIf you believe this was a mistake, then please contact the support staff immediately!'
            )

            await member.send(embed=embed)

            embed = disnake.Embed(title="Skill role Revoked", description=f"# Information:")
            embed.add_field(name="Action committed by:", value=f"```Username & ID: {inter.user.name} (ID: {inter.user.id})\nRole revoked: {skill}\nReason: {reason}```", inline=True)
            embed.set_author(name=f"{member.name} | (ID: {member.id})", icon_url=member.display_avatar.url)

            await log_channel.send(embed=embed)

            await inter.edit_original_message(f"{member.mention}'s skill role ({skill}) has been revoked successfully!")

    @commands.slash_command(name="revoke-skill", description="revoke a user's skill")
    async def revoke_skill(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, skill: str=commands.Param(choices=skills)):

        main_guild = await self.bot.fetch_guild(config.Main_server)

        target_info = self.roles.find_one({"user_id": member.id})

        verifier_role = main_guild.get_role(config.verifier_role)

        role_id = config.verification_roles[skill]["Id"]

        skill_role = main_guild.get_role(role_id)

        if not (((verifier_role in inter.user.roles) and (skill_role in inter.user.roles))) and (not inter.user.guild_permissions.administrator):
            await inter.response.send_message("You do not have sufficient permissions to execute this command!", ephemeral=True)
            return

        if not target_info:
            self.roles.insert_one(
                {
                    "user_id": member.id,
                    "obtained": []
                }
            )

        if (not target_info):
            await inter.response.send_message("The target does not have any skill roles!", ephemeral=True)
            return

        if target_info['obtained'] == []:
            await inter.response.send_message("The target does not have any skill roles!", ephemeral=True)
            return

        components = [
            disnake.ui.TextInput(
                label="Reason",
                placeholder="Reason for skill role removal",
                custom_id=f"rejection_reason",
                style=TextInputStyle.paragraph,
                max_length=350,
            )
        ]
        modal = disnake.ui.Modal(
            title="Title & description",
            components=components,
            custom_id=f"revoke_modal-{member.id}-{skill}"
        )

        await inter.response.send_modal(modal=modal)

def setup(bot: commands.Bot):
    bot.add_cog(Revoke_command(bot))