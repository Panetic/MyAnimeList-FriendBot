
# MyAnimeList FriendBot

This is a Python rewrite of [Lastmentor/MyAnimeList_FriendBot](https://github.com/Lastmentor/MyAnimeList_FriendBot).

The original code was very simple and led to some issues with usage. This version includes several improvements to enhance functionality and reliability.


## Improvements
- **Cache**: Ensures users are added only once to avoid duplicates.
- **Randomized Interval & Retry**: Increases the success rate of friend requests.
- **Automatic Chromedriver Updates**: Ensures chromedriver is always up to date.




## Contributing

Feel free to fork the repository and submit pull requests with any changes or improvements you may have.


## Variables

To run this project, you will need to add the following variables to .env

`MALusername`

`MALpassword`



## Installation

**Clone the repository**:
    
        git clone https://github.com/Beeamo/MyAnimeList-FriendBot.git
        cd MyAnimeList-FriendBot

**Install requirements**:

    pip install -r requirements.txt

## Running the Bot

The code supports several runtime arguments:

- `--visible` to run the browser in visible mode (default is headless mode).
- `-n VALUE` to specify the number of friends to add (default is 20).
- `--message` to provide an optional message to post to profiles.
- `--username` to override the `.env` username.
- `--password` to override the `.env` password.

### Example

To run the bot with all arguments:

```sh
python main.py --visible -n 25 --message "Hello, let's be friends" --username "example" --password "password"
