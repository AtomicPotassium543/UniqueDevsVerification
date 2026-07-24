<h1>
Unique Verification (Version management)
</h1>
<hr>
<div>
    <p>An automatic application system (discord bot) made using Python & MongoDB.</p>
    <h2>
         📁 Files & folders description:
    </h2>
    <p>
        - 👑 main: Loads all the cogs and turns on the bot.<br>
        - 🖊️ config: Consists of all the bot configuration.<br>
        - ⚙️ cogs: All the commands, tasks (loops) and not-command-related-functionality of the bot is kept in this folder.<br>
        <blockquote>
            <h3>Files in cogs folder:<br></h3>
                - Verify.py: Code for /verify functioanlity <br>
                - ReviewUpload.py: Sends the post in the review channel whenever a post has been submitted for review.<br>
                - RevokeCommand.py: Revokes commands (such as <b>on_message</b>)
        </blockquote>
    </p>
    <hr>
    <h2>Important note!</h2>
    <p>
        Make sure to create a .env file and insert "CLUSTER" (Mongodb connection string) and "TOKEN" (discord bot token) variable in the file.
    </p>
</div>
