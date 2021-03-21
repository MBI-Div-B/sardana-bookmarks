# -*- coding: utf-8 -*-
"""
Simple Sardana/ spock bookmarks

@author: Michael Schneider, MBI Berlin
"""


from sardana.macroserver.macro import Macro, Type, Optional, UnknownEnv
import json


class bm(Macro):
    
    param_def = [
        ['command', Type.String, Optional,
         'Command [list, goto, save, remove, to_file, from_file]'],
        ['name', Type.String, Optional,
         'bookmark name'],
        ['motors', [['motor', Type.Moveable, Optional, 'motor']], Optional,
         'List of motors'],
    ]
    
    interactive = True
    
    __usage = '''Usage: bm <cmd> [name] [motors]
    
This is a simple bookmark manager for Sardana/ spock. It can save a list of
motor positions under a user-specified name. This (collective) position
can then be recalled with the "goto" command.

TO AVOID COLLISIONS, THE MOTORS ARE DRIVEN IN THE ORDER SPECIFIED!

commands: 
    list:
        list currently saved bookmarks
        
    save <name> <motors>:
        save current positions of [motors] under <name>, ORDER MATTERS!
        
    remove <name>:
        remove bookmark <name>
        
    goto <name>:
        drive motors specified in bookmark <name> to their saved positions
        
    to_file <filename>:
        save currently defined bookmarks to json file
        
    from_file <filename>:
        load bookmarks from file

    '''
    
        
    def run(self, *args):
        cmd, name, motors = args
        self.load_from_env()
        if cmd == 'list':
            self.cmd_list()
        elif cmd == 'save':
            self.cmd_save(name, motors)
        elif cmd == 'remove':
            self.cmd_remove(name)
        elif cmd == 'goto':
            self.cmd_goto(name)
        elif cmd == 'to_file':
            self.cmd_to_file(name)
        elif cmd == 'from_file':
            self.cmd_from_file(name)
        else:
            self.output(self.__usage)

    def cmd_list(self):
        '''List currently defined bookmarks'''
        if len(self.bm) > 0:
            self.output('List of bookmarked positions:\n')
            w = max([len(k) for k in self.bm.keys()])
            for name, motorlist in self.bm.items():
                fill = len(name) * '='
                self.output(f'{name}\n{fill}')
                self.print_bm(motorlist, w)
        else:
            self.output('No positions bookmarked!')
    
    def cmd_save(self, name, motors):
        '''Add a named bookmark for current position(s) of given motor(s).'''
        new_bm = []
        for motor in motors:
            new_bm.append(dict(name=motor.getName(),
                               position=motor.getPosition()))
        if name in self.bm:
            self.output(f'Updating existing bookmark {name}')
        self.bm.update({name: new_bm})
    
    def cmd_goto(self, name):
        try:
            bookmark = self.bm[name]
            self.output(f'Moving to bookmark {name}:')
            self.print_bm(bookmark, show_current=True)
            ans = self.input('Type "yes" to proceed: ')
            if ans == 'yes':
                for i, m in enumerate(bookmark):
                    self.execMacro(['umv', m['name'], m['position']])
            else:
                self.output('Aborted')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')
    
    def cmd_remove(self, name):
        try:
            self.bm.pop(name)
            self.output(f'Removed bookmark {name}.')
        except KeyError:
            self.output(f'{name} is not a defined bookmark.')
    
    def cmd_to_file(self, fname):
        if not fname.endswith('.json'):
            fname += '.json'
        with open(fname, 'w') as f:
            json.dump(self.bm, f)
        self.output(f'Saved bookmarks to file {fname}.')
    
    def cmd_from_file(self, fname):
        with open(fname, 'r') as f:
            bm = json.load(f)
        self.bm.update(bm)
    
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
            self.bm = {}
            self.setEnv('_Bookmarks', self.bm)
