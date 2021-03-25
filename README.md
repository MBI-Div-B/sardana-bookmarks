## sardana-bookmarks
Simple bookmark manager macro for Sardana/ spock


This is a simple bookmark manager for Sardana/ spock. It can save a list of motor positions under a user-specified name. This (collective) position can then be recalled with the "goto" command (moving motors sequentially) or the "pgoto" command (parallel movement).

The command to be used for moving the motors is configurable, default is `umv`.

Usage:

`bm <cmd> [<name>] [<motors>]`

Available commands are: `list`, `save`, `goto`, `pgoto`, `remove`, `export`, `import`, `mv_cmd`

## Examples


### List existing bookmarks
`bm list`

```
   name   Motor   target   Motor   target   Motor   target
 ------ ------- -------- ------- -------- ------- --------
   pos1   mot01      0.0   mot02      0.0
   pos2   mot01      5.0   mot02     -4.0   mot03      0.0
   pos3   mot01     10.0   mot02     -4.0   mot03     10.0
   test   mot01      0.0   mot02      0.0   mot03     10.0

move command is umv
```

### Save current position of selected motors
`bm save sample1 motor1 motor2 motor3`

### Go to saved location
`bm goto pos3`

```
sequential movement to bookmark pos3

  name  Motor   current    target  Motor   current    target  Motor   current    target 
 ------ ------- --------- -------- ------- --------- -------- ------- --------- --------
  pos3  mot01     5.0       10.0   mot02     -4.0      -4.0   mot03     0.0       10.0  

move command is umv

Proceed (Y/n) [y]? 
     mot01
   10.0000

     mot02
   -4.0000

     mot03
   10.0000
```

`bm pgoto pos2`

```
parallel movement to bookmark pos2

  name  Motor   current    target  Motor   current    target  Motor   current    target 
 ------ ------- --------- -------- ------- --------- -------- ------- --------- --------
  pos2  mot01     10.0      5.0    mot02     -4.0      -4.0   mot03     10.0      0.0   

move command is umv

Proceed (Y/n) [y]? 
     mot01      mot02      mot03
    5.0000    -4.0000     0.0000
```

### Remove bookmark
`bm remove sample1`

### Export bookmarks to file
`bm export bookmarks.json`

### Load bookmarks from file
`bm import bookmarks.json`

### Change move command
`bm mv_cmd my_mv`


