# sardana-bookmarks
Simple bookmark manager macro for Sardana/ spock


This is a simple bookmark manager for Sardana/ spock. It can save a list of motor positions under a user-specified name. This (collective) position can then be recalled with the "goto" command.

TO AVOID COLLISIONS, THE MOTORS ARE DRIVEN IN THE ORDER SPECIFIED!

Usage: `bm <cmd> [<name>] [<motors>]`

Example:
`bm list`
`bm save sample1 motor1 motor2 motor3`
`bm goto sample1`


## Commands

### list
list currently saved bookmarks
### save *name motors*
save current positions of `motors` under `name`, ORDER MATTERS!
### remove *name*
remove bookmark `name`
### goto *name*
drive motors specified in bookmark `name` to their saved positions
### to_file *filename*
save currently defined bookmarks to json file
### from_file *filename*
load bookmarks from file
