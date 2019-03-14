Simple Pong game that can be played over the Internet.
Communication between players implements a peer-to-peer architecture and is based on UDP.


GAME'S RULES:

As in the original Pong, each player owns a bat and has to hit the ball and send it beyond the other player's bat.

We have a couple of special rules, though:
- the score doesn't change if no player has touched the ball at least once.
- if the bat of a player touches the ball and the ball passes it, it would be a "own goal" and increase the score of the opponent.


=================
RUNNING THE GAME:
=================

To run a networked game, each player would have to specify our local IP address and port as well as the IP address and port of the network opponent.
The game should therefore be run using the following command:

$ python3 pong.py <local_ip> <local_port> <opponent_ip> <opponent_port>


EXAMPLE:

To run a networked game player between bots on a single (your own) machine, open two consoles and type the following commands:

console1$ python3 pong.py '127.0.0.1' 9998 '127.0.0.1' 9999

console2$ python3 pong.py '127.0.0.1' 9999 '127.0.0.1' 9998


ALTERNATIVES:

The game can also be played without a remote opponent, but ip addresses and ports still needs to be specified.

The file pong_settings.py specifies the settings for the game (including the type of players).
For example, you can use the following settings in pong_settings.py for you to play against a non-remote bot.

local_human_players = 1
local_bot_players = 1
remote_players = 0


=================
BUGS AND CAVEATS:
=================

We are aware that the game is NOT bug-free.

We have started to keep a set of unit tests to avoid re-introducing previously fixed cases in which the above and other bugs would appear -- following an agile software development philosophy.
Note that the tests for the Controller (in pong_test.py) include special objects (Mocks) to avoid the need to run the GUI and a real network connection for testing specific methods of the Controller.

However, the set of tests doesn't cover the full spectrum of cases where (latent) bugs appear.

Known bugs include:
- the ball may sometimes travel inside players' bats, despite we tried hard to avoid this behavior. A way to solve this bug is to simplify the check of whether the ball should bounce or not because it collided with a bar (method get_bouncing_angle in GenericBar). We kept it generic to ease extensions to games with more than two players -- which some of you might want to implement! :)
- players may temporarily disagree on the score. This can sometimes lead one player to declare the game over while the other still plays.
- ...


