# Mesh-Network
Simple mesh network simulator in Python with Pygame.

This script creates a graphical representation of a managed flood network. A randomly chosen node sends out a signal instructing other nodes to change color. Receiving nodes process the instructions and relay the signal to nearby nodes. Signals have a finite radius they can reach before fading, as well as a TTL or maximum number of relay hops they can take before being ignored. The process starts over when all the signals have died out. 

Click to add a new node, right-click to remove a node.

Edit the values in the settings dict to customize parameters and experiment with the results.

This version contains support for node subscriptions (nodes relay all incoming signals but only "obey" signals whose category they subscribe to), but by default the basic loop does not feature these.

