# sardana-bookmarks
Simple bookmark manager macro for Sardana/ spock


This is a simple bookmark manager for Sardana/ spock. It can save a list of motor positions under a user-specified name. This (collective) position can then be recalled with the "goto" command.

**To avoid collisions, the motors are driven in the order specified!**

Usage:

`bm <cmd> [<name>] [<motors>]`

Available commands are: `list`, `save`, `goto`, `remove`, `export`, `import`

Examples:
* `bm list`
* `bm save sample1 motor1 motor2 motor3`
* `bm goto sample1`
* `bm remove sample1`
* `bm export bookmarks.json`


```
p04/door/haspp04max.01 [10]: wa s.
Current positions (user, dial) on 2021-03-21 22:04:49.779620

            sx        sy        sz
User   14.5303   19.9997   23.9987
Dial   14.5303   19.9997   23.9987

p04/door/haspp04max.01 [11]: bm save YAG sx sy sz

p04/door/haspp04max.01 [12]: bm list
List of bookmarked positions:

sample1
=======
  1. sx       --> 14.530312500000093
  2. sy       --> 19.99968751249983
  3. sz       --> 23.34999999980909


YAG
===
  1. sx       --> 14.530312500000093
  2. sy       --> 19.99968751249983
  3. sz       --> 23.99874999981071



p04/door/haspp04max.01 [13]: bm goto YAG
Moving to bookmark YAG:
  1. sx           14.530312500000093 --> 14.530312500000093
  2. sy           19.99968751249983 --> 19.99968751249983
  3. sz           23.99874999981071 --> 23.99874999981071


Type "yes" to proceed: yes
        sz
   23.9987


p04/door/haspp04max.01 [15]: bm export bookmarks.json
Saved bookmarks to file bookmarks.json.
```

