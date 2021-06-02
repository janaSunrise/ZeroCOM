# Welcome to ZeroCom 👋
[![Twitter: janaSunrise](https://img.shields.io/twitter/follow/janaSunrise.svg?style=social)](https://twitter.com/janaSunrise)

> A secure and advanced chat application in Python.

## Install

The project uses pipenv for dependencies. Here's how to install the dependencies.

```sh
pipenv sync -d
```

## Usage

The server is configured to run in `127.0.0.1` in the port `5700`. The project uses a `.ini`
configuration file to config it, which is located at `config.ini`. You can configure as
you want by tweaking the settings in it.

#### Running the server

Here's how you can run the server, so you can connect using clients.

```sh
python -m app.server
```

#### Running the client, and logging into a server

Once you have the server running, or someone has a compatible server node running,
Here's how you can login to the server, by running the client like this.

```sh
python -m app.client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>
```

#### Message formatting

Yes, You heard that right! We support user based message formatting. If you want 
to express yourself better, That's now possible!

What can you do?
- Change color of message / various sections of it.
- Add markdown / formatting to messages!
- Use emojis with the format of `:<emoji-name>:` and It's converted into an emoji!

You can change color of message in following way: `[blue] Hello, world! [/]`

`[<contents>][/]` are the opening, and closing tag, and the contents can have the color you want.

You can also change color of a message into various sections like this: `[blue]Hi[/] [red]Hello[/]`

This colors `Hi` as blue, and `Hello` as red.

We support a lot of colors, use any you want to!

You can also format your message, by adding "boldness", "italics", "codeblocks" and more! Here are 
some examples:
- Bold: `[bold]This is bold[/]`
- Italics: `[i]This is italics[/]`
- Underline: `[u]This is underline[/]`
- Codeblocks: `[codeblocks]print("hello")[/]`

You can combine more styles together as such: `[blue bold]This is blue and bold[/]`
And you can also use nested tags together as following, `[blue]Blueeee [bold]bold[/bold][/blue]`

And finally, You can use emojis easily! Here's a example: `Star emoji - :star:`, and `:star:` 
gets converted into ⭐

## Future plans, Bugs and Issues

For the Future plans and more, check out Kanban board: https://github.com/janaSunrise/ZeroCOM/projects/

To check the Bugs and Issues we face currently in the application, Check here: https://github.com/janaSunrise/ZeroCOM/issues

## 🤝 Contributing

Contributions, issues and feature requests are welcome. After cloning & setting up project locally, you can just submit 
a PR to this repo and it will be deployed once it's accepted.

⚠️ It’s good to have descriptive commit messages, or PR titles so that other contributors can understand about your 
commit or the PR Created. Read [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.3/) before 
making the commit message.

## 💬 Get in touch

If you have various suggestions, questions or want to discuss things with our community, Have a look at
[Github discussions](https://github.com/janaSunrise/useful-python-snippets/discussions) or join our discord server!

[![Discord](https://discordapp.com/api/guilds/695008516590534758/widget.png?style=shield)](https://discord.gg/cSC5ZZwYGQ)

## Show your support

We love people's support in growing and improving. Be sure to leave a ⭐️ if you like the project and 
also be sure to contribute, if you're interested!

<div align="center">
  Made by Sunrit Jana with ❤️
</div>
