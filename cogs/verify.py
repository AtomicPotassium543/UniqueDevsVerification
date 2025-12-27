import disnake
from disnake.ext import commands
import pymongo
import config
from dotenv import load_dotenv
import os

load_dotenv()

class verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = pymongo.MongoClient(os.getenv("CLUSTER"))
        self.db = self.client[config.db]
        self.review = self.db["review"]
        self.roles = self.db["roles"]

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        selected = inter.values[0]

        data = self.review.find_one({"user_id": inter.user.id, "applying_for": selected, "status": "waiting_for_result"})

        if data:
            await inter.response.send_message("Your post is under review! You can't post now.", ephemeral=True)
            return

        components = []

        field_num = 1

        job = config.verification_roles[selected]

        for field in job["components"]:
            if field["Field_size_large"]:
                components.append(disnake.ui.TextInput(
                    label=field["label"],
                    placeholder=field["placeholder"],
                    min_length=field["minLength"],
                    max_length=field["maxLength"],
                    required=field["required"],
                    custom_id=f"field_{field_num}",
                    style=disnake.TextInputStyle.paragraph
                ))
            else:
                components.append(disnake.ui.TextInput(
                    label=field["label"],
                    placeholder=field["placeholder"],
                    min_length=field["minLength"],
                    max_length=field["maxLength"],
                    required=field["required"],
                    custom_id=f"field_{field_num}",
                    style=disnake.TextInputStyle.short
                ))
            field_num += 1

        modal = disnake.ui.Modal(
            title=f"{selected} Verification",
            components=components,
            custom_id=f"verify-{selected}"
        )

        await inter.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        if "verify-" in inter.custom_id:

            inputs = inter.text_values
            input_list = []

            for i in range(1, len(inputs) + 1):
                input_list.append(inter.text_values.get(f"field_{i}"))

            apply_for = inter.custom_id[len("verify-"):]

            self.review.insert_one(
                {
                    "inter_id": inter.id,
                    "user_id": inter.user.id,
                    "applying_for": apply_for
                }
            )

            field_string = ""

            for field in input_list:
                field_string = field_string + f"{field}\n"

            self.review.update_one({"inter_id": inter.id}, {"$set": {"fields": field_string}})

            self.review.update_one({"inter_id": inter.id}, {"$set": {"status": "waiting_for_upload"}})

            await inter.response.edit_message(content="Successfully sent for review!", view=None)

    @commands.slash_command(name="skill-verify", description="Don't forget to read the verification guidelines!")
    async def verify(self, inter: disnake.ApplicationCommandInteraction):

        await inter.response.defer(ephemeral=True)

        options = [

        ]

        roles = self.roles.find_one({"user_id": inter.author.id})

        for role in config.verification_roles:
            if not roles:
                self.roles.insert_one({"user_id": inter.user.id, "obtained": []})
                roles = self.roles.find_one({"user_id": inter.author.id})
            if not (role in list(roles["obtained"])):
                options.append(disnake.SelectOption(label=role, description=f"Apply for {role}", value=role))
            else:
                continue

        if len(options) == 0:
            await inter.edit_original_message("There are no roles that you can apply for!")
            return

        select_component = disnake.ui.StringSelect(
            placeholder="Select role to apply for",
            options=options,
            min_values=1,
            max_values=1
        )

        view = disnake.ui.View()

        view.add_item(select_component)

        await inter.edit_original_message("Please select a skill to verify:", view=view)

def setup(bot: commands.Bot):
    bot.add_cog(verify(bot))