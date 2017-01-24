# Booru-Cogs

1. [Description](#description)
2. [Installation](#installation)
3. [Features](#features)
  1. [Search](#search)
  2. [Random Search](#random-search)
  3. [Filter List](#filter-list)
  4. [Set](#set)
4. [Cogs](#cogs)
  1. [Dan](#dan)
  2. [e621](#e621)
  3. [Gel](#gel)
  4. [Loli](#loli)
  5. [Pony](#pony)
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
Adding a tag to the filter list is simply a matter of running a command and
supplying the desired tag.

#### Add

`[p][booru]filter add [tag]`
Similarly, deleting a filter is done similarly. Running the delete command
without a supplied tag will instead reset the server's filter list to the
default.

#### Delete

`[p][booru]filter del [tag]`

### Set

The 'set' command is used to apply different settings to a filter. These are
often global settings that affect every server and should only be done in a
direct message with the bot. What's a "global setting"? A setting that can
be set and is used by every single server which uses the bot.

#### Username

Sets the username that's used to access the website. This can be useful if a
website has premium features for members that need to be logged in to access
(e.g. reduced tag limitations). This is a global setting and is only useable by
a few cogs.
`[p][booru]set username [Username]`

#### API Key

The following is used in conjunction with the Username to give premium members
access to their benefits. This is a global setting that is only useable by a
few cogs.
`[p][booru]set apikey [API key]`

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

## Cogs

This is a full list of cogs and their commands. Each of these cogs only have
access to the commands that are listed under them.

### Dan

Fetches anime-related images from <https://danbooru.donmai.us/>

#### Dan Commands

- `[p]dan [tags...]` fetches the latest image with the entered tags
- `[p]danr [tags...]` fetches a random image, optionally with the entered tags
- `[p]danfilter [option]` is used to adjust filter options
  - `list` display all the tags from the current server's filter list
  - `add [tag]`¹ adds a tag to the current server's filter list
  - `del [tag]`¹ deletes a tag from the current server's filter list
  - `del`¹ deletes the current server's filter list, making them use the default
- `[p]danset [option]` is used to adjust cog settings
  - `username [username]`² sets the username used to access the booru
  - `apikey [API key]`² sets the API key used to access the booru
  - `maxfilters [number]`² sets the maximum tags allowed in the cog's filter
                           list per server

### e621

Fetches furry-related images from <https://e621.net/>

#### e621 Commands

- `[p]e621 [tags...]` fetches the latest image with the entered tags
- `[p]e621r [tags...]` fetches a random image, optionally with the entered tags
- `[p]e621filter [option]` is used to adjust filter options
  - `list` display all the tags from the current server's filter list
  - `add [tag]`¹ adds a tag to the current server's filter list
  - `del [tag]`¹ deletes a tag from the current server's filter list
  - `del`¹ deletes the current server's filter list, making them use the default
- `[p]e621set [option]` is used to adjust cog settings
  - `maxfilters [number]`² sets the maximum tags allowed in the cog's filter
                           list per server

### Gel

Fetches anime-related images from <https://gelbooru.com/>

#### Gel Commands

- `[p]gel [tags...]` fetches the latest image with the entered tags
- `[p]gelr [tags...]` fetches a random image, optionally with the entered tags
- `[p]gelfilter [option]` is used to adjust filter options
  - `list` display all the tags from the current server's filter list
  - `add [tag]`¹ adds a tag to the current server's filter list
  - `del [tag]`¹ deletes a tag from the current server's filter list
  - `del`¹ deletes the current server's filter list, making them use the default
- `[p]gelset [option]` is used to adjust cog settings
  - `maxfilters [number]`² sets the maximum tags allowed in the cog's filter
                           list per server

### Loli

Fetches loli-related images from <https://lolibooru.moe/>

#### Loli Commands

- `[p]loli [tags...]` fetches the latest image with the entered tags
- `[p]lolir [tags...]` fetches a random image, optionally with the entered tags
- `[p]lolifilter [option]` is used to adjust filter options
  - `list` display all the tags from the current server's filter list
  - `add [tag]`¹ adds a tag to the current server's filter list
  - `del [tag]`¹ deletes a tag from the current server's filter list
  - `del`¹ deletes the current server's filter list, making them use the default
- `[p]loliset [option]` is used to adjust cog settings
  - `maxfilters [number]`² sets the maximum tags allowed in the cog's filter
                           list per server

### Pony

Fetches pony-related images from <https://derpibooru.org/>

#### Pony Commands

- `[p]pony [tags...]` fetches the latest image with the entered tags
- `[p]ponyr [tags...]` fetches a random image, optionally with the entered tags
- `[p]ponyfilter [option]` is used to adjust filter options
  - `list` display all the tags from the current server's filter list
  - `add [tag]`¹ adds a tag to the current server's filter list
  - `del [tag]`¹ deletes a tag from the current server's filter list
  - `del`¹ deletes the current server's filter list, making them use the default
- `[p]ponyset [option]` is used to adjust cog settings
  - `maxfilters [number]`² sets the maximum tags allowed in the cog's filter
                           list per server

### Annotations

¹Commands may only be used by users with the manage\_server permission
²Commands may only be used by the bot owner

## Assistance

Need help? Have an idea for a new booru-related cog?
Post an issue or contact me (Alzarath#8039) from the official
Red - Discord Bot [Discord Server](https://discord.gg/0k4npTwMvTpv9wrh).
