#!/usr/bin/env python3
"""
Simple Sardana/ spock bookmarks

https://github.com/MBI-Div-B/sardana-bookmarks.git

@author: Michael Schneider, MBI Berlin
"""


import json
import re
from sardana.macroserver.macro import Macro, Type, Optional, UnknownEnv
from taurus.console import Alignment
from taurus.console.list import List


class _bm(Macro):
    '''Base class for bookmarks'''
    bm = {}
    mv_cmd = ''

    def load_from_env(self):
        '''Loads a dictionary of bookmarks from environment'''
        try:
            bm_dict = self.getEnv('_Bookmarks')
            self.bm = bm_dict['bookmarks']
            self.mv_cmd = bm_dict['mv_cmd']
        except UnknownEnv:
            self.output('No bookmarks defined in environment. Creating empty.')
            self.bm = dict()
            self.mv_cmd = 'umv'
            self.setEnv('_Bookmarks', dict(bookmarks=self.bm, mv_cmd=self.mv_cmd))


class bmgo(_bm):
    '''Move to previously saved bookmark location'''
    param_def = [
        ['name', Type.String, None,
         'Name of the bookmark to go to'],
        ['parallel', Type.Boolean, False,
         'Move motors sequentially (False, default) or parallel (True)'],
    ]
    interactive = True

    def run(self, name, parallel):
        self.load_from_env()
        try:
            bookmark = self.bm[name]
            mode = 'parallel' if parallel else 'sequential'
            self.output(f'{mode} movement to bookmark {name}\n')
            self.lsbm(name, True)
            ans = self.input('\nProceed (Y/n)?', default_value='y')
            if ans.lower() == 'y':
                if parallel:
                    mv_arg = []
                    for m in bookmark:
                        mv_arg.append(m['name'])
                        mv_arg.append(m['position'])
                    self.execMacro([self.mv_cmd] + mv_arg)
                else:
                    for m in bookmark:
                        self.execMacro([self.mv_cmd, m['name'], m['position']])
                        self.output('')  # avoids output being overwritten
            else:
                self.output('Aborted')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')


class lsbm(_bm):
    '''List existing bookmarks'''
    param_def = [
        ['filter', Type.String, Optional, 'Regular expression to filter bookmarks'],
        ['show_current', Type.Boolean, Optional, 'Also show current motor positions']
    ]

    def run(self, filter='.*', show_current=False):
        self.load_from_env()
        if len(self.bm) == 0:
            self.output('No bookmarks defined')
            return
        filter = '.*' if filter is None else filter
        bm_sel = {k: self.bm[k] for k in self.bm if re.match(filter, k)}
        ncols = max([len(ml) for ml in bm_sel.values()])
        if show_current:
            cols = ['name'] + ncols * ['Motor', 'current', 'target']
        else:
            cols = ['name'] + ncols * ['Motor', 'target']
        align = Alignment.Right * len(cols)
        out = List(cols, text_alignment=align)

        for bm_name, motorlist in bm_sel.items():
            row = [bm_name]
            for m in motorlist:
                row.append(m['name'])
                if show_current:
                    mot = self.getMoveable(m['name'])
                    row.append(mot.getPosition())
                row.append(m['position'])
            out.appendRow(row)
        for line in out.genOutput():
            self.output(line)
        self.output('\nmove command is ' + self.mv_cmd)


class bmsave(_bm):
    param_def = [
        ['name', Type.String, None, 'Name of the bookmark'],
        ['motornames', [['filter', Type.String, None, 'Name or pattern of motors']], None, 'Motors']
    ]

    def run(self, name, motornames):
        self.load_from_env()
        new_bm = []
        motors = []
        for n in motornames:
            motors += self.findObjs(n, Type.Moveable, reserve=False)
        for motor in motors:
            new_bm.append(dict(name=motor.getName(),
                               position=motor.getPosition()))
        if name in self.bm:
            self.output(f'Updating existing bookmark {name}')
        self.bm.update({name: new_bm})

class bm(Macro):
    '''A simple bookmark manager for Sardana/ spock.

    This macro saves a list of motor positions under a user-specified name.
    This (collective) position can then be recalled with the "goto" or "pgoto"
    command (see below).

    commands:
        list:
            list currently saved bookmarks

        save <name> <motors>:
            save current positions of [motors] under <name>, order matters!

        remove <name>:
            remove bookmark <name>

        goto <name>:
            sequentially drive motors specified in bookmark <name> to their
            saved positions

        pgoto <name>:
            simultaneously drive motors specified in bookmark <name> to their
            saved positions

        export <filename>:
            save currently defined bookmarks to json file

        import <filename>:
            load bookmarks from file

        mv_cmd <cmd>:
            set macro name to use for motor movement (default: umv)

    '''

    param_def = [
        ['command', Type.String, None,
         'Command [list, goto, save, remove, export, import]'],
        ['name', Type.String, Optional,
         'name of bookmark, or file, or macro (depends on command)'],
        ['motors', [['motor', Type.Moveable, Optional, 'motor']], Optional,
         'List of motors'],
    ]

    interactive = True

    def run(self, cmd, name, motors):
        self.load_from_env()
        if cmd == 'list':
            filter = name if name is not None else '.*'
            self.cmd_list(filter=filter, show_current=False)
        elif cmd == 'save':
            self.cmd_save(name, motors)
        elif cmd == 'remove':
            self.cmd_remove(name)
        elif cmd == 'goto':
            self.cmd_goto(name, parallel=False)
        elif cmd == 'pgoto':
            self.cmd_goto(name, parallel=True)
        elif cmd == 'export':
            self.cmd_export(name)
        elif cmd == 'import':
            self.cmd_import(name)
        elif cmd == 'mv_cmd':
            self.cmd_set_mv_cmd(name)

    def cmd_save(self, name, motors):
        '''Add a named bookmark for current position(s) of given motor(s).'''
        new_bm = []
        for motor in motors:
            new_bm.append(dict(name=motor.getName(),
                               position=motor.getPosition()))
        if name in self.bm['bookmarks']:
            self.output(f'Updating existing bookmark {name}')
        self.bm['bookmarks'].update({name: new_bm})

    def cmd_goto(self, name, parallel=False):
        try:
            bookmark = self.bm['bookmarks'][name]
            mode = 'parallel' if parallel else 'sequential'
            mv_cmd = self.bm['mv_cmd']
            self.output(f'{mode} movement to bookmark {name}\n')
            self.cmd_list(filter=name, show_current=True)
            ans = self.input('\nProceed (Y/n)?', default_value='y')
            if ans.lower() == 'y':
                if parallel:
                    mv_arg = []
                    for m in bookmark:
                        mv_arg.append(m['name'])
                        mv_arg.append(m['position'])
                    self.execMacro([mv_cmd] + mv_arg)
                else:
                    for m in bookmark:
                        self.execMacro([mv_cmd, m['name'], m['position']])
                        self.output('')  # avoids output being overwritten
            else:
                self.output('Aborted')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')

    def cmd_remove(self, name):
        try:
            self.bm['bookmarks'].pop(name)
            self.info(f'Removed bookmark {name}.')
        except KeyError:
            self.info(f'{name} is not a defined bookmark.')

    def cmd_export(self, fname):
        if not fname.endswith('.json'):
            fname += '.json'
        with open(fname, 'w') as f:
            json.dump(self.bm, f)
        self.info(f'Saved bookmarks to {fname}')

    def cmd_import(self, fname):
        try:
            with open(fname, 'r') as f:
                bm = json.load(f)
            self.bm.update(bm)
            self.info(f'Loaded bookmarks from {fname}')
        except FileNotFoundError:
            self.warning(f'{fname} not found')

    def cmd_set_mv_cmd(self, cmd):
        if cmd in self.getMacroNames():
            self.bm['mv_cmd'] = cmd
        else:
            self.warning(f'{cmd} is not a macro')
        self.info(f'move command is {self.bm["mv_cmd"]}')

    def cmd_list(self, filter='.*', show_current=False):
        '''Print a list defined bookmarks.

        Shows only bookmarks with names matching the filter regex
        Optionally shows current positions of affected motors.
        '''
        bm_filter = {k: v for k, v in self.bm['bookmarks'].items()
                     if re.match(filter, k)}
        ncols = max([len(ml) for ml in bm_filter.values()])
        cols = ['name']
        if show_current:
            cols += ncols * ['Motor', 'current', 'target']
        else:
            cols += ncols * ['Motor', 'target']
        align = Alignment.Right * len(cols)
        out = List(cols, text_alignment=align)

        for bm_name, motorlist in bm_filter.items():
            row = [bm_name]
            for m in motorlist:
                row.append(m['name'])
                if show_current:
                    mot = self.getMoveable(m['name'])
                    row.append(mot.getPosition())
                row.append(m['position'])
            out.appendRow(row)
        for line in out.genOutput():
            self.output(line)
        self.output('\nmove command is ' + self.bm['mv_cmd'])

    
