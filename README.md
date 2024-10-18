# BlueBot

    Tootbot but for bluesky

# DISCLAIMER

     Very basic. No guarantees. Use at your own risk. Follow TOS and Privacy Policy.

## Usage

### Note: This was only tested on python 3.12

``` bash
pip install -r requirements.txt
python main.py
```

# Setting up .env

    Grab your app password from BlueSky and put it in AP in .env.example (dont forget to rename it)
    Put your user name in APU in .env.example

# Setting up Reddit API access

    Log into Reddit, go to your app preferences, and click the 'Create a new application' button at the bottom.
    Select 'script' as the application type, and click the 'Create app' button.
    You should see a Reddit agent string (underneath 'personal use script') and an agent secret.
    Copy these values and put them in the .env file.

# Running the bot

``` bash
    python main.py
```

# License

# Credits

- [BlueSky](https://bsky.app)
- [Reddit](https://reddit.com)
- [PRAW](https://praw.readthedocs.io/en/latest/)
- [atproto](https://github.com/MarshalX/atproto)
- [The Og tootbot](https://github.com/corbindavenport/tootbot)
- [tootbotX](https://gitlab.com/mocchapi/tootbotX)