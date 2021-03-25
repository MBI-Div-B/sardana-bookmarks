# -*- coding: utf-8 -*-
"""
Simple Sardana/ spock bookmarks

https://github.com/MBI-Div-B/sardana-bookmarks.git

@author: Michael Schneider, MBI Berlin
"""


from sardana.macroserver.macro import Macro, Type, Optional, UnknownEnv
import json


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
         'bookmark name'],
        ['motors', [['motor', Type.Moveable, Optional, 'motor']], Optional,
         'List of motors'],
    ]

    interactive = True

    def run(self, cmd, name, motors):
        self.load_from_env()
        if cmd == 'list':
            self.cmd_list()
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

    def cmd_list(self):
        '''List currently defined bookmarks'''
        if len(self.bm['bookmarks']) > 0:
            self.output('List of bookmarked positions:\n')
            w = max([len(k) for k in self.bm['bookmarks'].keys()])
            for name, motorlist in self.bm['bookmarks'].items():
                fill = len(name) * '='
                self.output(f'{name}\n{fill}')
                self.print_bm(motorlist, w)
        else:
            self.output('No positions bookmarked!')
        self.output(f'move command used: {self.bm["mv_cmd"]}\n')

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
            self.output(f'{mode} movement to bookmark {name}')
            self.print_bm(bookmark, show_current=True)
            ans = self.input('Proceed (Y/n)?')
            if ans.lower() != 'n':
                if parallel:
                    mv_arg = []
                    for m in bookmark:
                        mv_arg.append(m['name'])
                        mv_arg.append(m['position'])
                    self.execMacro([mv_cmd] + mv_arg)
                else:
                    for m in bookmark:
                        self.execMacro([mv_cmd, m['name'], m['position']])
            else:
                self.output('Aborted')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')

    def cmd_remove(self, name):
        try:
            self.bm['bookmarks'].pop(name)
            self.output(f'Removed bookmark {name}.')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')

    def cmd_export(self, fname):
        if not fname.endswith('.json'):
            fname += '.json'
        with open(fname, 'w') as f:
            json.dump(self.bm, f)
        self.output(f'Saved bookmarks to file {fname}')

    def cmd_import(self, fname):
        with open(fname, 'r') as f:
            bm = json.load(f)
        self.bm.update(bm)

    def cmd_set_mv_cmd(self, cmd):
        if cmd in self.getMacroNames():
            self.bm['mv_cmd'] = cmd
        else:
            self.warning(f'{cmd} is not a macro')
        self.info(f'move command is {self.bm["mv_cmd"]}')


    def print_bm(self, bookmark, w=12, show_current=False):
        for i, m in enumerate(bookmark):
            name, target = m['name'], m['position']
            if show_current:
                mov = self.getMoveable(name)
                curr = str(mov.getPosition())
            else:
                curr = ''
            self.output(f"  {i + 1}. {name:{w}s} {curr} --> {target}")
        self.output('\n')

    def load_from_env(self):
        '''Loads a dictionary of bookmarks from environment'''
        try:
            self.bm = self.getEnv('_Bookmarks')
        except UnknownEnv:
            self.output('No bookmarks defined in environment. Creating empty.')
            self.bm = dict(mv_cmd='umv', bookmarks={})
            self.setEnv('_Bookmarks', self.bm)
