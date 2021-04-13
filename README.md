# sardana-bookmarks
Simple bookmark manager macro for Sardana/ spock


This is a simple bookmark manager for Sardana/ spock. It can save a list of motor positions under a user-specified name. This (collective) position can then be recalled with the "bmgo" macro. An optional parameter determines whether all motors are moved simultaneously, or sequentially (default).

The command to be used for moving the motors is configurable, default is `umv`.

Available macros are: `lsbm`, `bmsave`, `bmgo`, `bm_remove`, `bm_setmv`, `bm_export`, `bm_import`

Examples:


```
Door_test_1 [126]: lsbm
   name   Motor   target   Motor   target   Motor   target   Motor   target      Motor   target
 ------ ------- -------- ------- -------- ------- -------- ------- -------- ---------- --------
   test   mot01      0.0
   pos2   mot04      0.0   mot01      2.0   mot03     10.0   mot02     -4.0
   new1   mot04      0.0   mot02     -4.0   mot03     10.0   mot01      2.0
   new2   mot04      0.0   mot02      0.0   mot03      0.0   mot01      0.0   offset01      0.0

move command is umv



Door_test_1 [131]: bmgo pos2
sequential movement to bookmark pos2

   name   Motor   current   target   Motor   current   target   Motor   current   target   Motor   current   target
 ------ ------- --------- -------- ------- --------- -------- ------- --------- -------- ------- --------- --------
   pos2   mot04       0.0      0.0   mot01       0.0      2.0   mot03       0.0     10.0   mot02       0.0     -4.0

move command is umv

Proceed (Y/n) [y]? 
     mot04
    0.0000

     mot01
    2.0000

     mot03
   10.0000

     mot02
   -4.0000
```

