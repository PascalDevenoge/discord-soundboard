# Simple Discord Soundboard

## Important!

This bot is a quickly thrown together experiment without any concern for security or robustness. The web server
should only ever be run behind a VPN that is only accessible to trustworthy users, and never exposed to the open
internet!

While the code is publicly available, we cannot accept contributions, issues or requests and the project should
be regarded as essentially unmaintained at this point.

### Installation

Use the provided compose.yaml file to start a docker container running the bot.

The compose.yaml file expects the following environment variables to be set:

- ```DISCORD_SBRD_TOKEN=<Token>``` (The Discord API token for a developer application)
- ```DISCORD_SBRD_TARGET_CHANNEL=<Voice channel name>``` (The name of the voice channel the bot should join)
- ```DISCORD_SBRD_DATA_DIR=<Path>``` (Path to the host directory containing the bots data files)

### Development setup

To run the bot locally for development, follow the following steps:

- Install npm packages for front-end dependencies and tools
- Create and activate Python virtual environment
- Install server dependencies from requirements.txt file
- Run ```npm run build``` to build the front-end
- __Optionally:__ Run ```npm run watch``` to rebuild the front-end files on changes of the code
- Run the ```run.sh``` script with the Discord API token as its argument to startup the bot server

The web server will start to listen on ```localhost:5124```

### Current limitations

The bot is a rather rudimentary prototype and has the following limitations at this point:

- Can only join a single Discord Server.
  Joining the bot to multiple servers will probably cause it to malfunction.

- Only able to join a single preset voice channel. The bot will only join a single voice channel, identified
  by its name. The name of the channel to join is set during startup as an environment variable.
