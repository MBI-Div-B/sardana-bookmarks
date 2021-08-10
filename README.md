## sardana-bookmarks
Simple bookmark manager macro for Sardana/ spock


This is a simple bookmark manager for Sardana/ spock. It can save a list of motor positions under a user-specified name. This (collective) position can then be recalled with the "bmgo" macro. An optional parameter determines whether all motors are moved simultaneously, or sequentially (default).

The command to be used for moving the motors is configurable, default is `umv`.

Bookmarks can be ex- and imported via json files. This can be automated by setting an automatic backup file using the `bm_backupfile` macro. If this is set, all bookmarks are exported to that file whenever a new position is bookmarked. Beware that this overwrites the old file, howerver.

Available macros are: `lsbm`, `bmsave`, `bmgo`, `bm_remove`, `bm_setmv`, `bm_export`, `bm_import`, `bm_backupfile`

Examples:

Save positions under a name, use wildcards for motor names
```
Door_test_1 [19]: wa
Current positions (user) on 2021-05-01 11:44:12.532858

         gap01     mot01     mot02     mot03     mot04  offset01
User    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000

Door_test_1 [20]: lsbm
No bookmarks defined

Door_test_1 [21]: bmsave pos1 gap01 mot01

Door_test_1 [22]: bmsave wild mot.*

Door_test_1 [23]: lsbm
   name   Motor   target   Motor   target   Motor   target   Motor   target
 ------ ------- -------- ------- -------- ------- -------- ------- --------
   pos1   gap01      0.0   mot01      0.0
   wild   mot03      0.0   mot01      0.0   mot04      0.0   mot02      0.0

move command is umv
```

Recall saved position in sequential movement (default)
```
Door_test_1 [24]: umvr mot01 1 mot02 -2 mot03 1.5
     mot01      mot02      mot03
    1.0000    -2.0000     1.5000

Door_test_1 [25]: bmgo pos1
sequential movement to bookmark pos1

   name   Motor   current   target   Motor   current   target
 ------ ------- --------- -------- ------- --------- --------
   pos1   gap01      -1.0      0.0   mot01       1.0      0.0

move command is umv

Proceed (Y/n) [y]? 
     gap01
    0.0000

     mot01
    0.0000
```

Recall position in parallel movement by passing `True` as final argument
```
Door_test_1 [26]: bmgo wild True
parallel movement to bookmark wild

   name   Motor   current   target   Motor   current   target   Motor   current   target   Motor   current   target
 ------ ------- --------- -------- ------- --------- -------- ------- --------- -------- ------- --------- --------
   wild   mot03       1.5      0.0   mot01       0.0      0.0   mot04       0.0      0.0   mot02      -1.5      0.0

move command is umv

Proceed (Y/n) [y]? 
     mot03      mot01      mot04      mot02
    0.0000     0.0000     0.0000     0.0000
```

Export bookmarks to json file
```
Door_test_1 [27]: bm_export bookmarks.json
Saved bookmarks to bookmarks.json

```

Remove bookmark
```
Door_test_1 [29]: bm_remove wild
Removed bookmark wild.

Door_test_1 [30]: lsbm
   name   Motor   target   Motor   target
 ------ ------- -------- ------- --------
   pos1   gap01      0.0   mot01      0.0

move command is umv
```

Import from json file
```
Door_test_1 [31]: bm_import bookmarks.json
Loaded bookmarks from bookmarks.json

Door_test_1 [32]: lsbm
   name   Motor   target   Motor   target   Motor   target   Motor   target
 ------ ------- -------- ------- -------- ------- -------- ------- --------
   pos1   gap01      0.0   mot01      0.0
   wild   mot03      0.0   mot01      0.0   mot04      0.0   mot02      0.0

move command is umv
```

### Remove bookmark
`bm remove sample1`

### Export bookmarks to file
`bm export bookmarks.json`

### Load bookmarks from file
`bm import bookmarks.json`

### Change move command
`bm mv_cmd my_mv`


