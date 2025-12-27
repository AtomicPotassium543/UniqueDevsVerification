import disnake
from disnake.ext import commands, tasks
from disnake import TextInputStyle
from dotenv import load_dotenv
import pymongo
import config
import os

load_dotenv()


class ReviewUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = pymongo.MongoClient(os.getenv("CLUSTER"))
        self.db = self.client[config.db]
        self.review = self.db["review"]
        self.roles = self.db["roles"]
        self.send_for_review.start()

    def cog_unload(self):
        self.send_for_review.cancel()

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if "approve-" in inter.component.custom_id:

            await inter.message.delete()

            await inter.response.defer(ephemeral=True)

            identification = int((inter.component.custom_id)[len("approve-"):])

            post = self.review.find_one({"inter_id": identification})

            logs_channel = await self.bot.fetch_channel(config.logs_channel)

            user = await self.bot.fetch_user(post["user_id"])

            main_server = self.bot.get_guild(config.Main_server)
            try:
                member = await main_server.fetch_member(user.id)
            except:
                user_exists = self.roles.find_one({"user_id": user.id})
                if user_exists:
                    data = self.roles.find_one({"user_id": user.id})

                    user_roles = list(data["obtained"])

                    user_roles.append(post["applying_for"])

                    self.roles.update_one({"user_id": user.id}, {"$set": {"obtained": user_roles}})

                elif not user_exists:
                    self.roles.insert_one({"user_id": user.id, "obtained": [post["applying_for"]]})

                self.review.update_one({"inter_id": identification, "applying_for": post["applying_for"]},
                                       {"$set": {"status": "reviewed"}})

                embed = disnake.Embed(title="New verification request!",
                                      description=f"User: {user.name} (ID: {user.id})\nApplying for: {post["applying_for"]}")
                embed.add_field(name="Projects & Sources:", value=post["fields"], inline=True)
                embed.set_author(name=f"{user.name} | (ID: {user.id})", icon_url=user.display_avatar.url)
                embed.set_footer(text=f"Request ID: {post["_id"]}")

                await logs_channel.send(
                    f"The following verification request has been accepted by {inter.user.name} (ID: {inter.user.id})",
                    embed=embed)

                await inter.followup.send("Successfully approved the post!", ephemeral=True)
                return

            role_id = config.verification_roles[post["applying_for"]]["Id"]
            giving_role = main_server.get_role(role_id)

            user_exists = self.roles.find_one({"user_id": user.id})

            if user_exists:
                data = self.roles.find_one({"user_id": user.id})

                user_roles = list(data["obtained"])

                user_roles.append(post["applying_for"])

                self.roles.update_one({"user_id": user.id}, {"$set": {"obtained": user_roles}})

            elif not user_exists:
                self.roles.insert_one({"user_id": user.id, "obtained": [post["applying_for"]]})

            self.review.update_one({"inter_id": identification, "applying_for": post["applying_for"]}, {"$set": {"status": "reviewed"}})

            embed = disnake.Embed(title="New verification request!", description=f"User: {user.name} (ID: {user.id})\nApplying for: {post["applying_for"]}")
            embed.add_field(name="Projects & Sources:", value=post["fields"], inline=True)
            embed.set_author(name=f"{user.name} | (ID: {user.id})", icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Request ID: {post["_id"]}")

            if not giving_role:
                pass
            else:
                try:
                    await member.add_roles(giving_role)
                except:
                    pass

            await logs_channel.send(f"The following verification request has been accepted by {inter.user.name} (ID: {inter.user.id})", embed=embed)

            embed = disnake.Embed(
                title=f'Hello there!',
                description=f'Congratulations, your verification for {post["applying_for"]} has been accepted.'
            )

            try:
                await user.send(embed=embed)
            except:
                pass

            await inter.followup.send("Successfully approved the post!", ephemeral=True)

        elif "reject-" in inter.component.custom_id:
            identification = (inter.component.custom_id)[len("reject-"):]

            components = [
                disnake.ui.TextInput(
                    label="Reason",
                    placeholder="Reason for post rejection",
                    custom_id=f"rejection_reason",
                    style=TextInputStyle.paragraph,
                    max_length=350,
                )
            ]
            modal = disnake.ui.Modal(
                title="Title & description",
                components=components,
                custom_id=f"rejection_modal-{identification}"
            )

            await inter.response.send_modal(modal=modal)

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        if "rejection_modal-" in inter.custom_id:

            await inter.message.delete()

            await inter.response.defer(ephemeral=True)

            identification = int((inter.custom_id)[len("rejection_modal-"):])

            reason = inter.text_values.get("rejection_reason")

            post = self.review.find_one({"inter_id": identification})

            logs_channel = self.bot.get_channel(config.logs_channel)

            user = await self.bot.fetch_user(post["user_id"])

            main_server = self.bot.get_guild(config.Main_server)

            try:
                member_of_server = await main_server.fetch_member(user.id)
            except:
                member_of_server = False

            embed = disnake.Embed(title="New verification request!", description=f"User: {user.name} (ID: {user.id})\nApplying for: {post["applying_for"]}")
            embed.add_field(name="Projects & Sources:", value=post["fields"], inline=True)
            embed.set_author(name=f"{user.name} | (ID: {user.id})", icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Request ID: {post["_id"]}")

            await logs_channel.send(f"The following verification request has been rejected by {inter.user.name} (ID: {inter.user.id})\nReason: {reason}", embed=embed)

            embed = disnake.Embed(
               title=f'Hello there!',
               description=f'Unfortunately, your verification for {post["applying_for"]} has been rejected for {reason}.'
            )

            if member_of_server:
                await user.send(embed=embed)
            else:
                pass

            self.review.update_one({"inter_id": post["inter_id"]}, {"$set": {"status": "reviewed"}})

            await inter.edit_original_message("Successfully rejected the post!")

    @tasks.loop(seconds=5)
    async def send_for_review(self):
        review_posts = self.review.find({"status": "waiting_for_upload"})
        for post in review_posts:

            admin_server = self.bot.get_guild(config.Admin_server)
            review_channel = await admin_server.fetch_channel(config.review_channel)

            user = await self.bot.fetch_user(post["user_id"])

            embed = disnake.Embed(title="Skill Verification Request!", description=f"```User: {user.name} (ID: {user.id})\nApplying for: {post["applying_for"]}```")
            embed.add_field(name="Projects:", value=post["fields"], inline=True)
            embed.set_author(name=f"{user.name} | (ID: {user.id})", icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Request ID: {post["_id"]}")

            approve = disnake.ui.Button(
                label="Approve",
                style=disnake.ButtonStyle.success,
                custom_id=f"approve-{post["inter_id"]}"
            )

            reject = disnake.ui.Button(
                label="Reject",
                style=disnake.ButtonStyle.danger,
                custom_id=f"reject-{post["inter_id"]}"
            )

            view = disnake.ui.View()
            view.add_item(approve)
            view.add_item(reject)

            await review_channel.send(embed=embed, view=view)

            self.review.update_one({"inter_id": post["inter_id"]}, {"$set": {"status": "waiting_for_result"}})

def setup(bot: commands.Bot):
    bot.add_cog(ReviewUpload(bot))