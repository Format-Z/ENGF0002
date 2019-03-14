# Source code for the Pacman game.

To run single player version:
`python3 pacman.py`

To run multi-player version:

One must be the client and one must be the server.

To run server:
`python3 pacman.py -s -p <passwd>`

Password can be any single word password, but no spaces.  The server pacman will display its IP address on screen.

To run client:

`python3 pacman.py -p <passwd> -c <ipaddress>`

Password must be the same as on the server, and the IP address must be
the server's IP address.  The client and server must be on the same
local area network, or the server must have a publicly reachable IP
address (which is unlikely).

## Your task

Details of the task are in [assignment.pdf](https://github.com/mhandley/ENGF0002/blob/master/Assignments/assignment5/assignment.pdf)

## Controls

See the source code in te_controller.py

 * **w** - move up
 * **a** - move left
 * **s** - move down
 * **d** - move right
 * **q** - quit
 * **r** - restart

Cursor keys should also work.
