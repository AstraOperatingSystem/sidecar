from os import getenv
from discord import Intents, Game, Interaction
from discord.ext import commands
from mpv import MPV, MpvEvent, MpvEventID
from queue import Queue

intents = Intents.default()
client = commands.Bot(command_prefix="/", intents=intents)
player = MPV(ytdl_format="bestaudio")
playq: Queue[str] = Queue()

def play_next() -> None:
	player.stop()
	if playq.empty(): return
	url = playq.get()
	player.play(url)

@player.event_callback(MpvEventID.END_FILE)
def mpv_end_event(_: MpvEvent) -> None:
	play_next()

@client.event
async def on_ready() -> None:
	print(f"Logged in as {client.user}")
	await client.change_presence(activity=Game("with the voices"))
	try:
		synced = await client.tree.sync()
		print(f"Synced {len(synced)} commands")
	except Exception as e:
		print(f"Failed to sync commands: {e}")
		exit(1)

@client.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: Interaction) -> None:
	latency = client.latency * 1000
	await interaction.response.send_message(f"Ping! Latency {latency:.2f}ms")

@client.tree.command(name="song", description="Play song")
async def song(interaction: Interaction, url: str) -> None:
	if player.idle_active:
		player.play(url)
		player.wait_until_playing()
		await interaction.response.send_message("Playing!")
	else:
		playq.put(url)
		await interaction.response.send_message("Queued!")

@client.tree.command(name="skip", description="Skip song")
async def skip(interaction: Interaction) -> None:
	play_next()
	await interaction.response.send_message("Skipped")

@client.tree.command(name="volume", description="Tweaks playback volume %")
async def volume(interaction: Interaction, vol: int) -> None:
	player.volume = vol
	await interaction.response.send_message(f"Volume set to {vol}")

@client.tree.command(name="pause", description="Toggle pause")
async def pause(interaction: Interaction) -> None:
	player.pause = not player.pause
	await interaction.response.send_message(f"Pause set to {player.pause}")

if __name__ == "__main__":
	token = getenv("DISCORD_TOKEN", None)
	if not token:
		print("DISCORD_TOKEN not set")
		exit(1)
	client.run(token)
