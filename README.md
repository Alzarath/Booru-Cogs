# Booru-Cogs

## Description
This repository will be used to host my *booru-related cogs. They're used to fetch images.

## Installation
To install these cogs, make sure Red-DiscordBot is up-to-date and add the repository.  
`[p]cog repo add booru-cogs https://github.com/alzarath/Booru-Cogs`

You can then list and install the available cogs.  
`[p]cog list booru-cogs`

Need more help with installation? RTFM  
`[p]help cog` and `[p]help cog install`

## Cogs
### Dan
Fetches anime-related images from https://danbooru.donmai.us/

#### Commands
- `[p]dan [tags...]` fetches the latest image with the entered tags  
- `[p]danr [tags...]` fetches a random image, optionally with the entered tags  

### e621
Fetches furry-related images from https://e621.net/

#### Commands
- `[p]e621 [tags...]` fetches the latest image with the entered tags  
- `[p]e621r [tags...]` fetches a random image, optionally with the entered tags  
- `[p]e621filter [option]` is used to adjust filter options  
    - `list` display all the tags from the current server's filter list  
    - `add [tag]`¹ adds a tag to the current server's filter list  
    - `del [tag]`¹ deletes a tag from the current server's filter list
    - `del`¹ deletes the current server's filter list, making them use the default

### Furry
Fetches furry-related images from http://furry.booru.org/

#### Commands
- `[p]furry [tags...]` fetches the latest image with the entered tags  
- `[p]furryr [tags...]` fetches a random image, optionally with the entered tags  

### Gel
Fetches anime-related images from https://gelbooru.com/

#### Commands
- `[p]gel [tags...]` fetches the latest image with the entered tags  
- `[p]gelr [tags...]` fetches a random image, optionally with the entered tags  

### Loli
Fetches loli-related images from https://lolibooru.moe/

#### Commands
- `[p]loli [tags...]` fetches the latest image with the entered tags  
- `[p]lolir [tags...]` fetches a random image, optionally with the entered tags  

### Pony
Fetches pony-related images from http://derpiboo.ru/

#### Commands
- `[p]pony [tags...]` fetches the latest image with the entered tags  
- `[p]ponyr [tags...]` fetches a random image, optionally with the entered tags  
- `[p]ponyfilter [option]` is used to adjust filter options  
    - `list` displays all of the available filters  
    - `set [name]`¹ is used to set the current filter for the current server  
    - `add [name] [id]`² adds a filter associated with an id³ to the filter list  
    - `del [name]`² deletes a filter from the filter list

#### Annotations
¹Commands may only be used by users with the manage_server permission  
²Commands may only be used by the bot owner  
³IDs can be found at http://derpiboo.ru/filters/ (https://derpiboo.ru/filters/<ID Number>)

## Assistance
Need help? Have an idea for a new booru-related cog? Post an issue or contact me (Alzarath#8039) from the official [Red - Discord Bot Discord Server](https://discord.gg/0k4npTwMvTpv9wrh).
