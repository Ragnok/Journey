#!/usr/bin/python3
from copy import deepcopy
import cmd, textwrap, sys, time
from select import select

#Ideas for rooms items and game designed were modified from the following:
#https://github.com/blakepell/CrimsonSkies/blob/master/area/
#http://www.realms.reichel.net/ahowto.html
#https://docs.python.org/3/library/cmd.html
#Monty Python and the Holy Grail-1975 Quotes http://www.imdb.com/title/tt0071853/quotes
#Tale 2.7 - MUD, mudlib & Interactive Fiction framework http://pythonhosted.org/tale/
#Color code found http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
"""
MAP of The Journey

          A Dead
          End
            |
          An Upward
          Sloping Path
            |                                                                                  Hermits
            |                                                                                  Lair
          A Fork      Further                   Entrance to                                     |
          in the____  Inside  ____ Inside _____ the Caves of___Path to the___Fountain_______ Path to     ___Dark
          Cave        the Cave     the Cave     Mahn-Tor       Caves of                      Hermits Lair   Cave
            |                                                  Mahn-Tor                        /
            |                                                              (START HERE)       /
          A Path                                Another   ______Older     _____Mine _____Entrance to the
          Heading Downwards                     Mine Shaft      Mine Shaft     Shaft     Mine Shaft
            |                                      |
          Further in                            Guarded
          the Cavern                            Room
            |                                      |
          End of                   Jail Cell___ Entrance to_____Jail Cell
          the Path                 One          a Dungeon       Three
             /                                     |
            /                                   Jail Cell
        A Large                                 Two
        Cavern
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

GROUND = 'ground'
SHOP = 'shop'
ENTER = 'enter cave'
EXIT = 'exit cave'
GROUNDDESC = 'grounddesc'
SHORTDESC = 'shortdesc'
LONGDESC = 'longdesc'
TAKEABLE = 'takeable'
DESCWORDS = 'descwords'
DESC = 'desc'
NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'
UP = 'up'
DOWN = 'down'

SCREEN_WIDTH = 79

#DESC is a text description of the area
#DIRECTION - adjacent rooms
#GROUND - items loaded in room

Rooms = {
    'Jail Cell One': {
        DESC: 'You are in a musty, dark jail cell.  Wet and dirty straw covers the floor.  The walls glisten with slime.  You see something stir in the straw.',
        EAST: 'Entrance to a Dungeon',
        GROUND: ['Human Prisoner']},
    'Jail Cell Two': {
        DESC: 'You are in a musty, dark jail cell.  Wet and dirty straw covers the floor.  The walls glisten with slime.  You see something stir in the straw.',
        NORTH: 'Entrance to a Dungeon',
        GROUND: ['Gnome Prisoner']},
    'Jail Cell Three': {
        DESC: 'You are in a musty, dark jail cell.  Wet and dirty straw covers the floor.  The walls glisten with slime.  You see something stir in the straw.',
        WEST: 'Entrance to a Dungeon',
        GROUND: []},
    'Entrance to a Dungeon': {
        DESC: 'The floor dips slightly as you walk into this dark and nasty place.  Your skin crawls as you look at the filth on the walls and see it move. Most of the exits lead into jail cells.',
        NORTH: 'Guarded Room',
        WEST: 'Jail Cell One',
        SOUTH: 'Jail Cell Two',
        EAST: 'Jail Cell Three',
        GROUND: []},
    'Guarded Room': {
        DESC: 'The guards store their spare weapons and armor here.  There are rusty swords on rotting shelves, and armor is laying on the floor.',
        NORTH: 'Another Mine Shaft',
        SOUTH: 'Entrance to a Dungeon',
        GROUND: ['Closed Cell Door','Key','Table','Sword','Helmet','Armor']},
    'Mine Shaft': {
        DESC: 'This mine shaft looks stable, at least in this area.  The wooden supports are thick and strong.  Torches line the walls.  A large door is to the east.',
        EAST: 'Entrance to the Mine Shaft',
        WEST: 'Older Mine Shaft',
        GROUND: ['Helmet', 'Prism', 'Closed Door']},
    'Older Mine Shaft': {
        DESC: 'You enter a part of the mine shaft where the torches have grown dim and are almost ready to go out.  From what you can see, there are plenty of cobwebs on the walls and rats at your feet.',
        EAST: 'Mine Shaft',
        WEST: 'Another Mine Shaft',
        GROUND: []},
    'Another Mine Shaft': {
        DESC: 'This mine shaft looks stable, at least in this area.  The wooden supports are thick and strong.  Torches line the walls.',
        EAST: 'Older Mine Shaft',
        SOUTH: 'Guarded Room',
        GROUND: []},
    'Entrance to the Mine Shaft': {
        DESC: 'As you enter the mine shaft, you get a sudden fear of the walls closing.  in on you.  A recently cut Edelweiss flower lies here.',
        WEST: 'Mine Shaft',
        UP: 'Path to Hermits Lair',
        GROUND: ['Edelweiss']},
    'Path to Hermits Lair': {
        DESC: 'All around you are the mountains of the southern range. A path leads north to a small hut, a sign and stange cave can be seen in the mountains.',
        NORTH: 'Hermits Lair',
        EAST: 'Dark Cave',
        WEST: 'Fountain',
        DOWN: 'Entrance to the Mine Shaft',
        GROUND: ['Warning Sign','Dark Cave','Gnome Woman']},
    'Hermits Lair': {
        DESC: 'Beautiful tapestries displaying the ancient masters of lore are on the walls, and the floor is covered with a plush multicolored carpet, which seems to rustle and move at the touch of your boots.',
        SOUTH: 'Path to Hermits Lair',
        GROUND: []},
    'Dark Cave': {
        DESC: 'PITCH BLACK. You cant see a thing other than Glowing Black Lava rocks in a cirlce beckoning for your attention.',
        WEST: 'Path to Hermits Lair',
        GROUND: ['Glowing Lava', 'Fire Sign']},
    'Dark Chamber': {
        DESC: 'Black obsidian walls transform the cave to an ancient temple!  Full humanoid figures embedded in the walls around the room, a statue with its mouth open stands in the corner.',
        GROUND: ['Burning Lava', 'Fire', 'Statue','Pile of Ash']},
    'Fountain': {
        DESC: 'You are standing amidst the ancient oaks and poplars in the holy grove. You feel unusually happy here, as if great burdens have been lifted from Your shoulders. From here, pleasant-looking paths lead east, and west.',
        WEST: 'Path to the Caves Mahn-Tor',
        EAST: 'Path to Hermits Lair',
        GROUND: ['Fountain']},
    'Path to the Caves Mahn-Tor': {
        DESC: 'All around you are the mountains of the southern range. A path leads west to the fabled caves of Mahn-Tor.',
        WEST: 'Entrance to the Caves of Mahn-Tor',
        EAST: 'Fountain',
        GROUND: []},
    'Entrance to the Caves of Mahn-Tor': {
        DESC: 'You are standing outside the entrance to a large cave.  The stone opening leads downwards into a pitch black darkness.  You can hear what you think is the sounds of creatures coming from within.',
        EAST: 'Path to the Caves Mahn-Tor',
        WEST: 'Inside the Cave',
        GROUND: []},
    'Inside the Cave': {
        DESC: 'You are standing inside the Cave of Mahn-tor.  To the west you can still see the light coming in from outside the cave.  The tunnel of the cave appears to bend to the southeast in the other direction.  The air is cool and humid here.',
        EAST: 'Entrance to the Caves of Mahn-Tor',
        WEST: 'Further Inside the Cave',
        GROUND: []},
    'Further Inside the Cave': {
        DESC: 'The rock ground of the cave is slippery here as water trickles down the cave walls.  You can hear noises coming from further in the cave as well as what sounds like bats flying about.  There is pitch black darkness in all directions.',
        EAST: 'Inside the Cave',
        WEST: 'A Fork in the Cave',
        GROUND: []},
    'A Fork in the Cave': {
        DESC: 'You have come to a fork.  To the north the cave path appears to be heading higher and to the south the path appears to be heading lower.',
        EAST: 'Further Inside the Cave',
        NORTH: 'An Upward Sloping Path',
        SOUTH: 'A Path Heading Downwards',
        GROUND: ['Faded Sign']},
    'An Upward Sloping Path': {
        DESC: 'The path is sloping upwards here.  The walls are slimy with a wet growth and the ground is very slippery.  There appear to be markings on the wall as if someone was trying to mark their location.',
        SOUTH: 'A Fork in the Cave',
        NORTH: 'A Dead End',
        GROUND: []},
    'A Dead End': {
        DESC: 'You have come to a dead end in the path blocked by a solid rock wall.',
        SOUTH: 'An Upward Sloping Path',
        GROUND: ['Campfire Remnants']},
    'A Path Heading Downwards': {
        DESC: 'As the path heads downwards you can begin to hear clamoring from some kind of live coming from deeper in the cave.  There also seems to be a faint light that you believe you can see.',
        NORTH: 'A Fork in the Cave',
        SOUTH: 'Further in the Cavern',
        GROUND: []},
    'Further in the Cavern': {
        DESC: 'The air has become more cool and humid here as the path heads downwards.  You can hear what sounds like water dripping coming from deeper in the Cave.',
        NORTH: 'A Path Heading Downwards',
        SOUTH: 'End of the Path',
        GROUND: []},
    'End of the Path': {
        DESC: 'You have come to the end of the path in this direction.  The water which is running down the floor and wall appears to be flowing into a large hole in the cave floor which leads directly down into the earth.  You can hear both water falling and noises of life from deep within the cave.',
        NORTH: 'Further in the Cavern',
        DOWN: 'A Large Cavern',
        GROUND: []},
    'A Large Cavern': {
        DESC: 'You are standing a large cavern with very high walls.  There are hundreds of stalagmites and stalagtites rising an hanging from the ceiling.  Water is drizzling down from the walls and pooling in a large spring which lays in the center of the room.',
        UP: 'End of the Path',
        GROUND: ['Mahn-Tor']},
    }

#GROUNDDESC value is a short string that displays in the area's description.
#SHORTDESC value is a short string
#LONGDESC displayed when player looks at the item.
#TAKEABLE Boolean True can pick up item -default - true
#DESCWORDS words used to interact with object

Items = {
    'Mahn-Tor': {
        GROUNDDESC: 'Mahn-Tor, the minotaur grand master, is here looking down at you.',
        SHORTDESC: 'Mahn-Tor is the leader of the minotaurs. He is awe-inspiring.',
        LONGDESC: 'Mahn-Tor towers above you. He is simply huge. Mahn-Tor is clad in the best of armor and robes. He wields the largest axe you have ever seen. You can see why Mahn-Tor is the leader of the minotaurs. He is awe-inspiring.',
        TAKEABLE: False,
        DESCWORDS: ['mahn-tor','minotaur']},
    'Campfire Remnants': {
        GROUNDDESC: 'the remnants of a recent campfire are here',
        SHORTDESC: 'the remnants of a recent campfire',
        LONGDESC: 'fresh coals and ash make up the remnants of a recent campfire.',
        TAKEABLE: False,
        DESCWORDS: ['gnome','woman']},
    'Gnome Woman': {
        GROUNDDESC: 'A gnome woman is standing here, trying to look beautiful.',
        SHORTDESC: 'a gnome woman',
        LONGDESC: 'The woman is short and gnarled, but acts like a woman several times her beauty.',
        TAKEABLE: False,
        DESCWORDS: ['gnome','woman']},
    'Warning Sign': {
        GROUNDDESC: 'An important sign stands is here.',
        SHORTDESC: 'a funny sign',
        #Monty Python and the Holy Grail-1975 Quotes http://www.imdb.com/title/tt0071853/quotes
        LONGDESC: 'We are now no longer the Knights who say Ni.\nWe are now the Knights who say...Ekki-ekki-ekki-ekki-PTANG. Zoom-Boing, znourrwringmm',
        TAKEABLE: False,
        DESCWORDS: ['warning','sign']},
    'Edelweiss': {
        GROUNDDESC: 'An edelweiss mountain flower lies here.',
        SHORTDESC: 'an Edelweiss flower',
        LONGDESC: 'An Edelweiss flower, belonging to the daisy or sunflower family.',
        TAKEABLE: True,
        DESCWORDS: ['edelweiss', 'flower']},
    'Helmet': {
        GROUNDDESC: 'A french medieval helmet lies here.',
        SHORTDESC: 'a helmet',
        LONGDESC: 'A helmet perfect for taunting those silly English khaaaa-nigggets!.',
        TAKEABLE: True,
        DESCWORDS: ['helmet']},
    'Prism': {
        GROUNDDESC: 'A strange prism lies here.',
        SHORTDESC: 'a small prism',
        LONGDESC: 'A small prism whose faces are parallel to one axis.',
        TAKEABLE: True,
        DESCWORDS: ['prism']},
    'Fountain': {
        GROUNDDESC: 'A large gurgling fountain.',
        SHORTDESC: 'a fountain',
        LONGDESC: 'A large fountain is here gurgling out an endless stream of water.',
        TAKEABLE: False,
        DESCWORDS: ['fountain', 'water']},
    'Sword': {
        GROUNDDESC: 'A two-handed bastard sword lies here.',
        SHORTDESC: 'a sword',
        LONGDESC: 'A two handed bastard sword lies here',
        TAKEABLE: True,
        DESCWORDS: ['sword', 'bastard']},
    'Pickle': {
        GROUNDDESC: 'An enormous steel pickle lies here.',
        SHORTDESC: 'an enormous steel dill pickle',
        LONGDESC: 'A large heavy steel dill pickle with a slot that states "PUT PRISM IN PICKLE".',
        TAKEABLE: False,
        DESCWORDS: ['pickle', 'dill']},
    'Meaning of Life': {
        GROUNDDESC: 'The Meaning of Life lies here.',
        SHORTDESC: 'the Meaning of Life',
        LONGDESC: 'The Meaning of Life is here..',
        TAKEABLE: True,
        DESCWORDS: ['meaning', 'life', 'meaning of life']},
    'Dark Cave': {
        GROUNDDESC: 'A strange Dark Cave.',
        SHORTDESC: 'A strange Dark Cave',
        LONGDESC: 'You see a creepy looking strange Dark Cave',
        TAKEABLE: False,
        DESCWORDS: ['dark', 'cave', 'dark cave']},
    'Glowing Lava': {
        GROUNDDESC: 'A Glowing Black Lava Rock Fire Pit loaded with wood.',
        SHORTDESC: 'A Black Lava Rock Fire Pit',
        LONGDESC: 'You see a Glowing Black Lava Rock Fire Pit loaded with wood longing to be to be set ablaze.  You hear a whisper "LIGHT FIRE"',
        TAKEABLE: False,
        DESCWORDS: ['fire pit', 'pit','lava','rock','rocks']},
    'Fire Sign': {
        GROUNDDESC: 'A sign stands before the fire pit.',
        SHORTDESC: 'a sign with instructions',
        LONGDESC: 'the sign says, LIGHT FIRE and WAIT',
        TAKEABLE: False,
        DESCWORDS: ['instructions','sign']},
    'Sign Burn': {
        GROUNDDESC: 'A burnt unreadable sign smolders by the fire.',
        SHORTDESC: 'a burned sign',
        LONGDESC: 'a burnt unreadable sign',
        TAKEABLE: False,
        DESCWORDS: ['unreadable','sign']},
    'Faded Sign': {
        GROUNDDESC: 'An old faded sign warns you not to proceed.',
        SHORTDESC: 'a faded sign',
        LONGDESC: 'The faded sign says, "YOU WILL DIE SOON!" and "LEAVE THIS PLACE NOW!"',
        TAKEABLE: False,
        DESCWORDS: ['faded','sign']},
    'Burning Lava': {
        GROUNDDESC: 'A Glowing Black Lava Rock Fire Pit surrounds a Blazing Fire.',
        SHORTDESC: 'A Black Lava Rock Fire Pit',
        LONGDESC: 'You see a Glowing Black Lava Rock Fire Pit lights the room with its burning blaze.',
        TAKEABLE: False,
        DESCWORDS: ['fire pit','lava','rocks','glowing']},
    'Closed Cell Door': {
        GROUNDDESC: 'A steel cell door is closed to the south.',
        SHORTDESC: 'A steel cell door',
        LONGDESC: 'A steel cell door is closed to the south.',
        TAKEABLE: False,
        DESCWORDS: ['door', 'closed','cell']},
    'Open Cell Door': {
        GROUNDDESC: 'A steel cell door is open to the south.',
        SHORTDESC: 'A steel cell door is open to the south',
        LONGDESC: 'A steel cell door is open  to the east, leading to the jail cells.',
        TAKEABLE: False,
        DESCWORDS: ['door', 'open','cell']},
    'Closed Door': {
        GROUNDDESC: 'A large door is closed to the east.',
        SHORTDESC: 'A large door is closed to the east',
        LONGDESC: 'A large door is closed to the east.',
        TAKEABLE: False,
        DESCWORDS: ['door', 'closed']},
    'Open Door': {
        GROUNDDESC: 'A large door is open to the east.',
        SHORTDESC: 'A large door is open to the east',
        LONGDESC: 'A large door is open  to the east, leading out of the mine.',
        TAKEABLE: False,
        DESCWORDS: ['door', 'open']},
    'Statue': {
        GROUNDDESC: 'A statue of a humanoid with a gaping open mouth stands here.',
        SHORTDESC: 'A statue of a humanoid with  Open Mouth',
        LONGDESC: 'A statue of a Giant with his mouth open wide seems to await for your tribute.',
        TAKEABLE: False,
        DESCWORDS: ['mouth', 'statue']},
    'Hungry Statue': {
        GROUNDDESC: 'A statue of a humanoid with a gaping open mouth stands here.',
        SHORTDESC: 'A statue of a humanoid with  Open Mouth',
        LONGDESC: 'A statue of a Giant with his mouth open wide seems to await for your tribute.\nA whisper says "PUT HELMET IN STATUE"',
        TAKEABLE: False,
        DESCWORDS: ['mouth', 'statue']},
    'Fire': {
        GROUNDDESC: 'A blazing fire.',
        SHORTDESC: 'A blazing fire',
        LONGDESC: 'A fire blazes surrounded by glowing black lava rocks.  It whispers "PUT EDELWEISS IN FIRE"',
        TAKEABLE: False,
        DESCWORDS: ['fire']},
    'Human Prisoner': {
        GROUNDDESC: 'A human prisoner is here resting in the straw.',
        SHORTDESC: 'A human prisoner',
        LONGDESC: 'The prisoner is just barely alive.',
        TAKEABLE: False,
        DESCWORDS: ['human', 'prisoner']},
    'Gnome Prisoner': {
        GROUNDDESC: 'A gnome prisoner is here resting in the straw.',
        SHORTDESC: 'A gnome prisoner',
        LONGDESC: 'The prisoner is just barely alive.',
        TAKEABLE: False,
        DESCWORDS: ['gnome', 'prisoner']},
    'Armor': {
        GROUNDDESC: 'A large suit of heavy banded mail is here.',
        SHORTDESC: 'heavy banded armor',
        LONGDESC: 'A large suit of heavy banded mail is here.',
        TAKEABLE: True,
        DESCWORDS: ['armor', 'banded','mail']},
    'Coins': {
        GROUNDDESC: 'A pile of coins.',
        SHORTDESC: 'a pile of coins',
        LONGDESC: 'A pile of coins.',
        TAKEABLE: True,
        DESCWORDS: ['pile', 'coins']},
    'Key': {
        GROUNDDESC: 'A large key is here.',
        SHORTDESC: 'a key',
        LONGDESC: 'A large key.',
        TAKEABLE: True,
        DESCWORDS: ['key']},
    'Table': {
        GROUNDDESC: 'A well worn table and chairs is here.',
        SHORTDESC: 'a table and chairs',
        LONGDESC: 'A well worn table and chairs is here.',
        TAKEABLE: False,
        DESCWORDS: ['table', 'chairs','chair']},
    'Pile of Ash': {
        GROUNDDESC: 'A small pile of ash is here.',
        SHORTDESC: 'a pile of ash',
        LONGDESC: 'A small pile of ash is here.',
        TAKEABLE: False,
        DESCWORDS: ['ash', 'pile']},
    }


location = 'Mine Shaft' # start loc
inventory = [] # start with blank inventory
showFullExits = True

def displayLocation(loc):
    # Print the room name.
    print('\n')
    print (bcolors.BOLD + bcolors.UNDERLINE + (loc) + bcolors.ENDC)
#    print (bcolors.BOLD + ('=' * len(loc)) + bcolors.ENDC)

    # Print the room's description (using textwrap.wrap())
    print('\n'.join(textwrap.wrap(Rooms[loc][DESC], SCREEN_WIDTH)))

    # Print items on the ground.
    if len(Rooms[loc][GROUND]) > 0:
        print()
        for item in Rooms[loc][GROUND]:
            print (bcolors.OKBLUE + (Items[item][GROUNDDESC]) + bcolors.ENDC)

    # Print exits.
    exits = []
    for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
        if direction in Rooms[loc].keys():
            exits.append(direction.title())
    print()
    if showFullExits:
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction in Rooms[location]:
                print('%s: %s' % ((bcolors.OKGREEN + (direction.title()) + bcolors.ENDC), Rooms[location][direction]))
    else:
        print('Exits: %s' % ' '.join(exits))

def win():
    print (bcolors.WARNING + ("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"))
    print (" ██╗   ██╗ ██████╗ ██╗   ██╗      ")
    print (" ╚██╗ ██╔╝██╔═══██╗██║   ██║      ")
    print ("  ╚████╔╝ ██║   ██║██║   ██║      ")
    print ("   ╚██╔╝  ██║   ██║██║   ██║      ")
    print ("    ██║   ╚██████╔╝╚██████╔╝      ")
    print ("    ╚═╝    ╚═════╝  ╚═════╝       ")
    print ("                                  ")
    print (" ██╗    ██╗██╗███╗   ██╗██╗██╗██╗ ")
    print (" ██║    ██║██║████╗  ██║██║██║██║ ")
    print (" ██║ █╗ ██║██║██╔██╗ ██║██║██║██║ ")
    print (" ██║███╗██║██║██║╚██╗██║╚═╝╚═╝╚═╝ ")
    print (" ╚███╔███╔╝██║██║ ╚████║██╗██╗██╗ ")
    print (("  ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝╚═╝╚═╝ ") + bcolors.ENDC)
    print ("Congratulations you beat Dungeon Dudes 2 - The Journey!! ")
    print ("by MSG Mike Simpson")

class JourneyCmd(cmd.Cmd):
    intro = ('\nType "help" for commands.')
    prompt = ('\n# ')

    def precmd(self, line):
        return line.lower()

    def default(self, arg):
        print('I do not understand. Please type "help" for a command list.')

    #From SSG Torres thank you!
    def emptyline(self):
        pass


    def parse(arg):
        return tuple(arg.split())

    def do_quit(self, arg):
        """quit ends your journey."""
        return True

    def do_put(self, arg):
        """put is helpful when you want to place something in or on something else."""
        if 'Edelweiss' in inventory and "Pile of Ash" in Rooms[location][GROUND]:
            if arg == 'edelweiss in fire':
                print('The fire flashes a bright green providing daylight through the room as the fire\n disappears.')
                Rooms[location][GROUND].remove('Fire') # remove fire
                inventory.remove('Edelweiss') # remove from inventory
                Rooms[location][GROUND].remove('Burning Lava') # remove from floor
                Rooms[location][GROUND].append('Glowing Lava') # add to floor
                Rooms[location][GROUND].remove('Statue') # remove from floor
                Rooms[location][GROUND].append('Hungry Statue') # add to floor
            else:
                print('Cant put %s here.' % arg)
        elif 'Helmet' in inventory and "Hungry Statue" in Rooms[location][GROUND]:
            if arg == "helmet in statue":
                print('You move toward the statue..')
                time.sleep(2)
                print ('the statues eyes open and focus on the helmet in your hands')
                time.sleep(3)
                print ('You hold the helmet out in front of you..')
                time.sleep(3)
                print ('The statue leans toward you and suddenly bites the helmet from your hands.. chewing vigorously.')
                inventory.remove('Helmet') # remove from inventory
                time.sleep(5)
                print('\nThe statue begins to dry-heave..')
                time.sleep(3)
                print('The statue vomits and the entire statue transforms to an enormous heavy \nsteel pickle..  it lays on the ground before you!')
                Rooms[location][GROUND].remove('Hungry Statue') # remove statue
                Rooms[location][GROUND].append('Pickle') # add Pickle to floor
            else:
                print('Cant put %s here.' % arg)
        elif 'Prism' in inventory and "Pickle" in Rooms[location][GROUND]:
            if arg == 'prism in pickle':
                print('You lean down and slide your prism into the prism slot on the pickle')
                inventory.remove('Prism') # remove from inventory
                time.sleep(3)
                print('The pickle rises from the floor and your quest for the location of the Meaning of Life will finally be revealed.\n')
                time.sleep(5)
                print('The pickle speaks to you, "Seek out the Hermits Lair.. \nfor there the Meaning of Life can be found"\n')
                time.sleep(5)
                print('A magical wind blows through the chamber as the Pickle disolves\n')
                Rooms[location][GROUND].remove('Pickle') # remove Pickle
                Rooms[location][GROUND].remove('Pile of Ash') # remove Ash
                #Need to blow open exit to proceed to the end
                Rooms['Dark Chamber']={DESC: 'Black obsidian walls transform the cave to an ancient temple!  Full humanoid figures embedded in the walls around the room.',WEST: 'Path to Hermits Lair',GROUND: ['Glowing Lava']}#more forward in story to statue
#                moveDirection('west')
                Rooms['Hermits Lair'][GROUND].append('Meaning of Life')
            else:
                print('Cant put %s here.' % arg)
        else:
            print('You cant put %s here.' % arg)

    def do_open(self, arg):
        """open is helpful when you find something closed that you would like to open."""
        if "Closed Door" in Rooms[location][GROUND] and arg == 'door' or arg =='east':
            print('You open the door that leads out of the Mine.')
            Rooms[location][GROUND].remove('Closed Door') # remove Closed door
            Rooms[location][GROUND].append('Open Door') # add Open door
        elif "Closed Cell Door" in Rooms[location][GROUND] and arg == 'door' or arg == 'cell' or arg =='south':
            if 'Key' in inventory:
                print('You use the large key to unlock and open the cell door.')
                Rooms[location][GROUND].remove('Closed Cell Door') # remove Closed door
                Rooms[location][GROUND].append('Open Cell Door') # add Open door
            else:
                print('You dont have the key to unlock the cell door.')
        else:
            print('Cant open %s.' % arg)

    def do_close(self, arg):
        """close is helpful when you find something open you would like to close."""
        if "Open Door" in Rooms[location][GROUND] and arg == 'door'or arg =='east':
            print('You close the door that leads out of the Mine.')
            Rooms[location][GROUND].append('Closed Door') # add Closed door
            Rooms[location][GROUND].remove('Open Door') # remove Open door
        elif "Open Cell Door" in Rooms[location][GROUND] and arg == 'door' or arg == 'cell' or arg =='south':
            if 'Key' in inventory:
                print('You use the large key to lock and close the cell door.')
                Rooms[location][GROUND].append('Closed Cell Door') # remove Closed door
                Rooms[location][GROUND].remove('Open Cell Door') # add Open door
            else:
                print('You dont have the key to unlock the cell door.')
        else:
            print('What do you want to close?')


    def do_enter(self, arg):
        """enter is helpful in entering a cave or other confined area."""
        if 'Dark Cave' in Rooms[location][GROUND] and arg == 'cave':
            moveDirection('east')
        else:
            print('No %s here to enter.' % arg)

    def do_exit(self, arg):
        """exit is helpful in leaving a cave or other confined area."""
        if 'Glowing Lava' in Rooms[location][GROUND] and arg == 'cave':
            moveDirection('west')
        else:
            print('What do you want to exit?')

    def do_wait(self, arg):
        """wait.. time will pass.. this is very productive after you light a fire.."""
        if 'Sign Burn' in Rooms[location][GROUND]:#sign burn ensures fire is lit
            time.sleep(1)
            print ('As the fire builds in brightness.. the room is slowly revealed\n\n')
            time.sleep(3)
            Rooms[location][GROUND].remove('Sign Burn') # add burnt sign
            Rooms[location][GROUND].append('Pile of Ash') # add ash
            Rooms['Dark Cave']={DESC: 'PITCH BLACK.',NORTH: 'Dark Chamber',GROUND: []}#more forward in story to statue
            moveDirection('north')
        else:
            print('You wait.. ')
            time.sleep(4)
            print('Time passes..')

    def do_light(self, arg):
        """light a fire.. it is important to "WAIT" after lighting a fire to give it time to build."""
        if 'Fire Sign' in Rooms[location][GROUND] and arg == 'fire':
            if 'Prism' not in inventory: # check for Prism in inventory
                print ('You hear a whisper, "You are the chosen one.. but without a Prism you are not ready."')
            elif 'Helmet' not in inventory: # check for helmet in inventory
                print ('You hear a whisper, "You are the chosen one.. but without the Helmet you are not ready."')
            elif 'Edelweiss' not in inventory: # check for flower in inventory
                print ('You hear a whisper, "You are the chosen one.. but without Edelweiss you are not ready."')
            else:
                print ('A flash and the Cave Entrance is SEALED!')
                time.sleep(2)
                print('The sign by the fire is smoking, and slowly flames start to dance in the fire pit..')
                time.sleep(2)
                print('This may take a while.. your hear a whisper "WAIT"')
                Rooms[location][GROUND].remove('Fire Sign') # remove sign
                Rooms[location][GROUND].append('Sign Burn') # add burnt sign
                Rooms['Path to Hermits Lair'].pop(EAST)
                Rooms['Path to Hermits Lair'][GROUND].remove('Dark Cave')
                Rooms['Dark Cave'].pop(WEST)
        else:
            print('What do you want to light?')

    def do_look(self, arg):
        """look at an item or in a direction for more information."""
        lookingAt = arg.lower()
        if lookingAt == '':
            #"look" will show area description
            displayLocation(location)
            return

        if lookingAt == 'exits':
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in Rooms[location]:
                    print('%s: %s' % (direction.title(), Rooms[location][direction]))
            return

        if lookingAt in ('north', 'west', 'east', 'south', 'up', 'down', 'n', 'w', 'e', 's', 'u', 'd'):
            if lookingAt.startswith('n') and NORTH in Rooms[location]:
                print(Rooms[location][NORTH])
            elif lookingAt.startswith('w') and WEST in Rooms[location]:
                print(Rooms[location][WEST])
            elif lookingAt.startswith('e') and EAST in Rooms[location]:
                print(Rooms[location][EAST])
            elif lookingAt.startswith('s') and SOUTH in Rooms[location]:
                print(Rooms[location][SOUTH])
            elif lookingAt.startswith('u') and UP in Rooms[location]:
                print(Rooms[location][UP])
            elif lookingAt.startswith('d') and DOWN in Rooms[location]:
                print(Rooms[location][DOWN])
            else:
                print('There is nothing in that direction.')
            return

        # see if the item being looked at is on the ground at this location
        item = getFirstItemMatchingDesc(lookingAt, Rooms[location][GROUND])
        if item != None:
            print('\n'.join(textwrap.wrap(Items[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is in the inventory
        item = getFirstItemMatchingDesc(lookingAt, inventory)
        if item != None:
            print('\n'.join(textwrap.wrap(Items[item][LONGDESC], SCREEN_WIDTH)))
            return

        print('You do not see that here.')

    def do_north(self, arg):
        """move north."""
        moveDirection('north')

    def do_south(self, arg):
        """move south."""
        moveDirection('south')

    def do_east(self, arg):
        """move east."""
        moveDirection('east')

    def do_west(self, arg):
        """move west."""
        moveDirection('west')

    def do_up(self, arg):
        """move up."""
        moveDirection('up')

    def do_down(self, arg):
        """move down."""
        moveDirection('down')

#shortened names:
    do_n = do_north
    do_s = do_south
    do_e = do_east
    do_w = do_west
    do_u = do_up
    do_d = do_down
    do_l = do_look
    do_examine = do_look


    def do_exits(self, arg):
        """Toggle showing full exit descriptions or brief exit descriptions."""
        global showFullExits
        showFullExits = not showFullExits
        if showFullExits:
            print('Showing full exit descriptions.')
        else:
            print('Showing brief exit descriptions.')

    def do_inventory(self, arg):
        """Display a list of the items in your possession."""

        if len(inventory) == 0:
            print('Inventory:\n  (nothing)')
            return

        itemCount = {}
        for item in inventory:
            if item in itemCount.keys():
                itemCount[item] += 1
            else:
                itemCount[item] = 1

        print('Inventory:')
        for item in set(inventory):
            if itemCount[item] > 1:
                print('  %s (%s)' % (item, itemCount[item]))
            else:
                print('  ' + item)
    do_inv = do_inventory
    do_i = do_inv #i == inv == inventory

    def do_take(self, arg):
        """take/get item and place in your inventory."""
        itemToTake = arg.lower()

        if itemToTake == '':
            print('Take what? Type "look" the items on the ground here.')
            return

        cantTake = True
        for item in getAllItemsMatchingDesc(itemToTake, Rooms[location][GROUND]):
            if Items[item].get(TAKEABLE, True) == False:
                cantTake = True
                continue # there may be other items named this that you can take, so we continue checking
            print('You get %s.' % (Items[item][SHORTDESC]))
            Rooms[location][GROUND].remove(item) # remove from the ground
            inventory.append(item) # add to inventory
            if 'Meaning of Life' in inventory:
                time.sleep(1)
                win()
                sys.exit('Thanks for playing!')
            return

        ground = deepcopy(Rooms[location][GROUND])
        while arg == 'all'and ground:
            for item in ground:
                if Items[item].get(TAKEABLE, True) == False:
                    cantTake = True
                    ground.remove(item) # remove from the ground
                    continue #continue checking
                print('You get %s.' % (Items[item][SHORTDESC]))
                ground.remove(item) # remove from the ground
                Rooms[location][GROUND].remove(item) # remove from the ground
                inventory.append(item) # add to inventory
                if 'Meaning of Life' in inventory:
                    time.sleep(5)
                    win()
                    sys.exit('Thanks for playing!')
        return

        if not cantTake:
            print('You cannot take "%s".' % (itemToTake))
        else:
            print('That is not on the ground.')

    do_get = do_take # take == get

    def do_drop(self, arg):
        """drop item take out of your inventory and place on the ground."""
        itemToDrop = arg.lower()
        invDescWords = getAllDescWords(inventory)

        #chk player has that item
        if itemToDrop not in invDescWords and itemToDrop != 'all':
            print('You do not have "%s" in your inventory.' % (itemToDrop))
            return
        elif itemToDrop == 'all':
            while itemToDrop == 'all'and inventory:
                for item in inventory:
                    Rooms[location][GROUND].append(item) # add to the ground
                    inventory.remove(item)  #remove from inventory
                    print('You drop %s.' % (Items[item][SHORTDESC]))

        item = getFirstItemMatchingDesc(itemToDrop, inventory)
        if item != None:
            print('You drop %s.' % (Items[item][SHORTDESC]))
            inventory.remove(item) # remove from inventory
            Rooms[location][GROUND].append(item) # add to the ground


    def complete_take(self, text, line, begidx, endidx):
        possibleItems = []
        text = text.lower()

        #type "take" no item name:
        if not text:
            return getAllFirstDescWords(Rooms[location][GROUND])

        for item in list(set(Rooms[location][GROUND])):
            for descWord in Items[item][DESCWORDS]:
                if descWord.startswith(text) and Items[item].get(TAKEABLE, True):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def complete_drop(self, text, line, begidx, endidx):
        possibleItems = []
        itemToDrop = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        for descWord in invDescWords:
            if line.startswith('drop %s' % (descWord)):
                return [] # command is complete

        #type "drop" no item name:
        if itemToDrop == '':
            return getAllFirstDescWords(inventory)

        for descWord in invDescWords:
            if descWord.startswith(text):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

def getAllDescWords(itemList):
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.extend(Items[item][DESCWORDS])
    return list(set(descWords))

def getAllFirstDescWords(itemList):
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.append(Items[item][DESCWORDS][0])
    return list(set(descWords))

def getFirstItemMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    for item in itemList:
        if desc in Items[item][DESCWORDS]:
            return item
    return None

def getAllItemsMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    matchingItems = []
    for item in itemList:
        if desc in Items[item][DESCWORDS]:
            matchingItems.append(item)
    return matchingItems

def moveDirection(direction):
    global location

    if direction in Rooms[location]:
        if "Closed Door" in Rooms[location][GROUND] and direction == 'east':
            print('The door to the east leading out of the mine is closed.')
        elif "Closed Cell Door" in Rooms[location][GROUND] and direction == 'south':
            print('The door to the south leading to the cells is closed.')
        elif 'Dark Cave' in Rooms[location][GROUND]:
            print('You enter the Dark Cave')
            location = Rooms[location][direction]
            displayLocation(location)
        elif 'Fire Sign' in Rooms[location][GROUND]:#check for sign
            location = Rooms[location][direction]
            displayLocation(location)
        elif 'Sign Burn' in Rooms[location][GROUND]:#check for sign
            location = Rooms[location][direction]
            displayLocation(location)
        else:
            location = Rooms[location][direction]
            displayLocation(location)
    else:
        print('You cannot move in that direction')

    if location == 'A Large Cavern':#Mahn-Tor will kill player if they dont press a key
        time.sleep(2)
        print("You are frozen with fear..")
        time.sleep(2)
        print("Mahn-Tor slowly turns his head in your direction")
        time.sleep(2)
        print("You feel like you are not welcome here..")
        print("Mahn-Tor slowly raises the monsterous axe above his head")
        time.sleep(2)
        print("Hurry!!  Get out of here!! Go UP NOW!!")
        timeout = 4
        rlist, wlist, xlist = select([sys.stdin], [], [], timeout)
        if not rlist:
            print("\n\nYour End was Quick!\n")
            sys.exit('Thanks for playing!\n')
        else:
            print("\nYou overcame your fear in the nick of time!!")
            print("WHEW THAT WAS CLOSE! You barely made it out of there!")

#            moveDirection('up')
#        if location == 'A Large Cavern':

#ASCII ART Creator http://patorjk.com/software/taag/
if __name__ == '__main__':
    print (bcolors.HEADER + bcolors.BOLD + "")
    print (" ________                                             ")
    print (" \______ \  __ __  ____    ____   ____  ____   ____    222222222222222    ")
    print ("  |    |  \|  |  \/    \  / ___\_/ __ \/  _ \ /    \  2:::::::::::::::22  ")
    print ("  |    `   \  |  /   |  \/ /_/  >  ___(  <_> )   |  \ 2::::::222222:::::2 ")
    print (" /_______  /____/|___|  /\___  / \___  >____/|___|  / 2222222     2:::::2 ")
    print ("         \/           \//_____/      \/           \/              2:::::2 ")
    print ("                                                                  2:::::2 ")
    print ("                         THE  JOURNEY                          2222::::2  ")
    print ("  _ .-') _               _(`-')     (`-')  _  (`-').->     2222::::::22   ")
    print (" ( (  OO) )             ( (OO ).->  ( OO).-/  ( OO)_    22::::::::222     ")
    print ("  \     .'_  ,--. ,--.   \    .'_  (,------. (_)--\_) 22:::::22222        ")
    print (" ,`'--..._) |  | |(' -')'`'-..__)  |  .---' /    _ /  2:::::2             ")
    print (" |  |   ' | |  |_|( OO )|  |  ' | (|  '--.  \_..`--.  2:::::2       222222")
    print (" |  |   / : |  | | `-' /|  |  / :  |  .--'  .-._)   \ 2::::::2222222:::::2")
    print (" |  '--'  / \  '-'(_ .' |  '-'  /  |  `---. \       / 2::::::::::::::::::2")
    print ("  `-------'  `-----'    `------'   `------'  `-----'  22222222222222222222")
    print ("" + bcolors.ENDC)

    displayLocation(location)
    JourneyCmd().cmdloop()
    print('Thanks for playing!')
