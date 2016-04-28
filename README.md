# Booru-Cogs

## Description
This repository will be used to host my *booru-related cogs. They're used to fetch images.

## Cogs
### Dan
Fetches anime-related images from https://danbooru.donmai.us/

#### Commands
`[p]dan [tags]` fetches the latest image with the entered tags  
`[p]danr [tags]` fetches a random image, optionally with the entered tags  

### Pony
Fetches pony-related images from http://derpiboo.ru/

#### Commands
`[p]pony [tags]` fetches the latest image with the entered tags  
`[p]ponyr [tags]` fetches a random image, optionally with the entered tags  
`[p]ponyfilter [option]` is used to adjust filter options  
`[p]ponyfilter list` displays all of the available filters  
`[p]ponyfilter set [name]`¹ is used to set the current filter for the current server  
`[p]ponyfilter add [name] [id]`² adds a filter associated with an id³ to the filter list  
`[p]ponyfilter del [name]`² deletes a filter from the filter list

#### Annotations
¹Commands may only be used by users with the manage_server permission  
²Commands may only be used by the bot owner  
³IDs can be found at http://derpiboo.ru/filters/ (https://derpiboo.ru/filters/<ID Number>)

## Installation
To install any of these cogs, make sure you're at least at commit [71240e5](https://github.com/Twentysix26/Red-DiscordBot/commit/71240e56a0245eb68054c86a5a6236a1a2650fd7) of Red-Discordbot, then add the repository.  
`[p]cog repo add booru-cogs https://github.com/alzarath/Booru-Cogs`

You can then list and install the available cogs.  
`[p]cog list booru-cogs`

## Assistance
Need help? Have an idea for a new booru-related cog? Post an issue or contact me (Alzarath#8039) from the official [Red - Discord Bot Discord Server](https://discord.gg/0k4npTwMvTpv9wrh).
