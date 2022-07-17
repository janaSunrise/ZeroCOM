<h1 align="center">ZeroCOM 🚀</h1>

<h3 align="center">Powerful chat application, built using Python. ✨</h3>

<!-- Badges -->
<p align="center">
  <a href="https://twitter.com/janaSunrise">
    <img src="https://img.shields.io/twitter/follow/janaSunrise.svg?style=social" alt="Twitter" />
  </a>

  <a href="https://github.com/janaSunrise/ZeroCOM/graphs/commit-activity">
    <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" alt="Maintained" />
  </a>
</p>

<!-- Links -->
<h3 align="center">
  <a href="https://github.com/janaSunrise/ZeroCOM/issues">Report a bug</a>
  <span> · </span>
  <a href="https://github.com/janaSunrise/ZeroCOM/discussions">Discussions</a>
</h3>

## 🚀 Installation

**Python 3.7 or above is required!**

The project uses pipenv for dependencies. Here's how to install the dependencies:

```sh
pipenv sync -d
```

## Usage

The server uses a configuration file (`config.ini`) located in the root of the project to run it.
It is configured to run in `127.0.0.1:5700` TCP port by default. You can change things as you need
and configure according to you.

To connect to the ZeroCom server, It is essential to have a ZeroCom client to establish connection and use it.

#### Running the server

Here's how you can run the server so you can connect using clients.

```sh
pipenv run server
```

#### Running the client, and logging into a server

Once you have the server running, or someone else has a ZeroCom server running,
Here's how you can login to the server by running the client like this.

```sh
pipenv run client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>
```

#### Message formatting

Yes, You heard that right! We support user based message formatting. If you want
to express yourself better, That's now possible!

What can you do?

- Change color of message / various sections of it.
- Add markdown / formatting to messages!
- Use emojis with the format of `:<emoji-name>:` and It's converted into an emoji!

You can change color of message in following way: `[blue]Hello, world![/]`

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

## 🤝 Contributing

Contributions, issues and feature requests are welcome. After cloning & setting up project locally, you can
just submit a PR to this repo and it will be deployed once it's accepted.

⚠️ It’s good to have descriptive commit messages, or PR titles so that other contributors can understand about your
commit or the PR Created. Read [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.3/) before
making the commit message.

## 💬 Get in touch

If you have various suggestions, questions or want to discuss things with our community, Have a look at
[Github discussions](https://github.com/janaSunrise/ZeroCom/discussions)!

## 👇 Show your support

We love people's support in growing and improving. Be sure to leave a ⭐️ if you like the project and
also be sure to contribute, if you're interested!

<div align="center">Made by Sunrit Jana with ❤️</div>
