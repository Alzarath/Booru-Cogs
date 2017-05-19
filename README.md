# Booru-Cogs

1. [Description](#description)
2. [Installation](#installation)
3. [Features](#features)
    1. [Search](#search)
    2. [Random Search](#random-search)
    3. [Filter List](#filter-list)
    4. [Set](#set)
4. [Boorus](#boorus)
5. [Assistance](#assistance)

## Description

This repository will be used to host image board-related cogs. They're used to
fetch and display images.

## Installation

To install these cogs, make sure Red-DiscordBot is up-to-date and add the
repository.

```
[p]cog repo add booru-cogs https://github.com/alzarath/Booru-Cogs
```

You can then list and install the available cogs.

```
[p]cog list booru-cogs
```

Need more help with installation? RTFM

```
[p]help cog
```

and

```
[p]help cog install
```

## Features

Here's a full list of commands that can be run by the cog and detailed
explanations as to what they do.

Command examples are formatted in the following way:  
`[p]` stands for the bot's prefix (e.g. `!`)  
`[booru]` stands the the booru's command (e.g `dan`, `gel`, etc.)  
`[tags...]` is where you designate any amount of tags to search for  
`[tag]` is a singular desired tag to be filtered  
Anything else should be common sense.

### Search

The default functionality of the cogs. Searches the associated booru for the
entered tags and posts the latest result in the chat.  
`[p][booru] [tags...]`

### Random Search

Searches for a random image from the associated booru, optionally with tags,
and posts the result in the chat.  
`[p][booru]r [tags...]`

### Filter List

Filter lists can be used to automatically apply tags to any given search. 
These tags do count toward any sort of tag limit restrictions a booru may 
contain. Every booru contains a set of tags by default that attempt to prevent
users from fetching explicit images. These can, however, be removed.  
`[p][booru]filter list`

#### Add

Adding a tag to the filter list is simply a matter of running a command and
supplying the desired tag.  
`[p][booru]filter add [tag]`

This command may only be run by someone with the **Manage Server** permission

#### Delete

Deleting a filter is done similarly. Running the delete command without a
supplied tag will instead reset the entire server's filter list to the
default.  
`[p][booru]filter del [tag]`

This command may only be run by someone with the **Manage Server** permission

### Set

The 'set' command is used to apply different settings to a filter. These are
often global settings that affect every server and should only be done in a
direct message with the bot.

#### Username

Sets the username that's used to access the website. This can be useful if a
website has premium features for members that need to be logged in to access
(e.g. reduced tag limitations). This is a global setting.  
`[p][booru]set username [Username]`

Limited to:
* Gel

This command may only be run by the **Bot Owner** and should be done in a private
message with the bot.

#### API Key

The following is used in conjunction with the Username to give premium members
access to their benefits. This is a global setting that is only useable by a
few cogs.  
`[p][booru]set apikey [API key]`

Limited to:
* Gel

This command may only be run by the **Bot Owner** and should be done in a private
message with the bot.

**Warning.** There is a security risk you should be aware of:

Because this stores and uses the API key in plain text, this is a setting that
only the host of the bot should use. It's recommended to use a disposable
account if you do. The key and username is sent directly to the website, it is
not sent to me or anyone else via the cog. You can check the code yourself.

Were Red-DiscordBot to become a malicious tool by the creators, I am not
responsible for what they might do, should they choose to intercept whatever
the bot sends out.

Sending the key through Discord also means that the Discord company could
intercept it.

All that being said, you're a tiny fish, and the likelihood of someone actually
attempting to steal your account information through this is probably small.

#### Max Filters

This command is used to restrict the amount of filters that can be added to
each individual server. This should prevent servers from being able to fill up
the host computer's hard drive with filters. By default, a server can have 100
filters. This is a global setting.  
`[p][booru]set maxfilters [Amount]`

This command may only be run by the **Bot Owner**.

#### Verbose

Toggle Verbose mode on and off. With verbose mode enabled, instead of simply
getting an image URL, an embed is posted that contains the link to the image's
page, the image's content rating, and the image's tags.  
`[p][booru]set verbose [on|off]`

This command may only be run by someone with the **Manager Server** permission

## Boorus

This is a full list of the Booru sites available to you.

### Dan

Fetches anime-related images from <https://danbooru.donmai.us/>

### e621

Fetches furry-related images from <https://e621.net/>

### Gel

Fetches anime-related images from <https://gelbooru.com/>

### Kona

Fetches anime-related wallpapers from <https://konachan.com/>

### Loli

Fetches loli-related images from <https://lolibooru.moe/>

### Pony

Fetches pony-related images from <https://derpibooru.org/>

## Assistance

Need help? Have an idea for a new booru-related cog?
Post an issue or send a message in the #support\_booru-cogs channel in the
Red - Cog Support [Discord Server](https://discord.gg/MFrCXm4).
