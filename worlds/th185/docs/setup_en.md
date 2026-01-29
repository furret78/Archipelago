# Black Market of Bulletphilia ~ 100th Black Market Randomizer Setup Guide

## Required Software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
- The .apworld for 100th Black Market, if not bundled with Archiepelago.
- Touhou 18.5: 100th Black Market, the game. Preferably obtained from [Steam](https://store.steampowered.com/app/2097720/Black_Market_of_Bulletphilia___100th_Black_Market/), but its Comiket CD release is also supported.

## Setup Before Playing

Before opening the game and playing, ensure that your local save data has been wiped,
including its backups. It is recommended that you make a copy of your old save data for the game and keep it somewhere safe.

The game's save data is typically located in `%appdata%\ShanghaiAlice\th185`,
where you might find two files called `scoreth185.dat` and `scoreth185.bak.dat`.
You may make a copy of these two files and paste them somewhere where you can find them.

If 100th Black Market's .apworld has not yet been installed,  do so before playing.
Before opening the game, open the client in the Archipelago Launcher and run one simple setup command to clear the game's save data.
The command will also paste in fresh save data tailored specifically to the randomizer.
It is recommended that this be done every time before opening the game to ensure that there is no inconvenience that arises during launch.
See the setup guide below for more details.

## Randomizer Setup

In order to play this implementation, a multiworld room is required.
For this, you or someone you know has to generate a game. This will not be explained here, but you can check the [Archipelago Setup Guide](/tutorial/Archipelago/setup_en#generating-a-game).

At the top of the client, you may see a text box.
This is where the `IP Address`/`Hostname` and `Port` will go so that the client can connect to a room.
Simply type in the address and port number separated by a `:` symbol. (e.g. `archipelago.gg:69420`)

If the client successfully connects, you will be asked for your slot name.
Enter the name you used during the `.yaml` generation.

Before opening the game itself, it is advised to run the `/replace_save` command to prepare the game's save data for Archipelago.
This will delete any old save data in `%appdata%\ShanghaiAlice\th185` and paste in save data tailored to the randomizer.

Once this is done, you may open the game. The client will attempt to connect to the game.
If successful, you will be informed that the client is initiating game loops.
You may then play the game as usual.