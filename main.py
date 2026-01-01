from disnake.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

class Bot(commands.Bot):
    def __init__(self, command_prefix = None, help_command = ..., description = None, *, strip_after_prefix = False, owner_id = None, owner_ids = None, reload = False, case_insensitive = False, command_sync_flags = ..., sync_commands = ..., sync_commands_debug = ..., sync_commands_on_cog_unload = ..., test_guilds = None, default_install_types = None, default_contexts = None, asyncio_debug = False, loop = None, shard_id = None, shard_count = None, enable_debug_events = False, enable_gateway_error_handler = True, gateway_params = None, connector = None, proxy = None, proxy_auth = None, assume_unsync_clock = True, max_messages = 1000, application_id = None, heartbeat_timeout = 60, guild_ready_timeout = 2, allowed_mentions = None, activity = None, status = None, intents = None, chunk_guilds_at_startup = None, member_cache_flags = None, localization_provider = None, strict_localization = False):
        super().__init__(command_prefix, help_command, description, strip_after_prefix=strip_after_prefix, owner_id=owner_id, owner_ids=owner_ids, reload=reload, case_insensitive=case_insensitive, command_sync_flags=command_sync_flags, sync_commands=sync_commands, sync_commands_debug=sync_commands_debug, sync_commands_on_cog_unload=sync_commands_on_cog_unload, test_guilds=test_guilds, default_install_types=default_install_types, default_contexts=default_contexts, asyncio_debug=asyncio_debug, loop=loop, shard_id=shard_id, shard_count=shard_count, enable_debug_events=enable_debug_events, enable_gateway_error_handler=enable_gateway_error_handler, gateway_params=gateway_params, connector=connector, proxy=proxy, proxy_auth=proxy_auth, assume_unsync_clock=assume_unsync_clock, max_messages=max_messages, application_id=application_id, heartbeat_timeout=heartbeat_timeout, guild_ready_timeout=guild_ready_timeout, allowed_mentions=allowed_mentions, activity=activity, status=status, intents=intents, chunk_guilds_at_startup=chunk_guilds_at_startup, member_cache_flags=member_cache_flags, localization_provider=localization_provider, strict_localization=strict_localization)

@Bot.event()
async def on_ready():
    print("Ready to serve!")

Bot.login(os.getenv("BOT_TOKEN"))