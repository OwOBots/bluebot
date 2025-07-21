# BlueBot

Tootbot but for bluesky

****
# DISCLAIMER

Very basic. No guarantees. Use at your own risk. No support will be provided. This is a hobby project and not intended
for production use.

***

# Installation

- Windows: [FFmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/)
- macOS: `brew install ffmpeg`
- Linux: Use your distro’s package manager (e.g. `sudo apt install ffmpeg`)

    git clone https://github.com/OwOBots/bluebot
    Set up the .env file
    uv run main.py

***



# Setting up .env

    Grab your app password from BlueSky and put it in AP in .env.example (dont forget to rename it)
    Put your user name in APU in .env.example

****
# Setting up Reddit API access

    Log into Reddit, go to your app preferences, and click the 'Create a new application' button at the bottom.
    Select 'script' as the application type, and click the 'Create app' button.
    You should see a Reddit agent string (underneath 'personal use script') and an agent secret.
    Copy these values and put them in the .env file.

****
# Running the bot

***
``` bash
    uv run main.py
```

****
# License

[CC0](https://github.com/OwOBots/bluebot/blob/main/LICENSE)

# Credits

- [BlueSky](https://bsky.app)
- [Reddit](https://reddit.com)
- [PRAW](https://praw.readthedocs.io/en/latest/)
- [atproto](https://github.com/MarshalX/atproto)
- [The Og tootbot](https://github.com/corbindavenport/tootbot)
- [tootbotX](https://gitlab.com/mocchapi/tootbotX)
- [FFmpeg-python](https://github.com/kkroening/ffmpeg-python)
