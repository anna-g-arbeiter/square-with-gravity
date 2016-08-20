# SQUARE WITH GRAVITY
A game for the EMF 2016 badge (work in progress)

Coloful squares are falling down, but the ground is not always the same. Use the orientation of the badge to change the background color and erase the squares before it is too late! 

The game runs on [TiLDA_MK3](https://badge.emfcamp.org/wiki/TiLDA_MK3) EMF 2016 badge.

To test the game download [pyboard.py](https://raw.githubusercontent.com/emfcamp/micropython/tilda-master/tools/pyboard.py). Then connect your bade via USB, cd into the square-to-gravity directory, and execute:

sudo python pyboard.py main.py --device=/dev/ttyACM0

If you want to permanently add the game to your badge, you can copy the square-to-gravity directory into your apps directory.
