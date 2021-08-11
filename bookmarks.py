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
            self.bm_dict = self.getEnv('_Bookmarks')
            self.bm = self.bm_dict['bookmarks']
            self.mv_cmd = self.bm_dict['mv_cmd']
            self.autosavefile = self.bm_dict['autosavefile']
        except UnknownEnv:
            self.info('No bookmarks defined in environment. Creating empty.')
            self.bm = dict()
            self.mv_cmd = 'umv'
            self.autosavefile = None
            self.bm_dict = dict(
                mv_cmd=self.mv_cmd,
                bookmarks=self.bm,
                autosavefile=self.autosavefile,
                )
            self.setEnv('_Bookmarks', self.bm_dict)


class bmgo(_bm):
    '''Move to previously saved bookmark location'''
    param_def = [
        ['name', Type.String, None,
         'Name of the bookmark to go to'],
        ['parallel', Type.Boolean, False,
         'Move motors sequentially (False, default) or parallel (True)'],
        ['exclude', [[
            'filter', Type.String, Optional, 'Name or pattern of motors'
            ]],
            Optional, 'Motors to exclude from movement'
        ]
    ]
    interactive = True

    def run(self, name, parallel, exclude):
        self.load_from_env()
        if name not in self.bm:
            self.warning(f'{name} is not a defined bookmark.')
            return

        bookmark = self.bm[name]
        excluded = []
        for ex in exclude:
            if ex is not None:
                motors = self.findObjs(ex, Type.Moveable, reserve=False)
                excluded += [m.getName() for m in motors]
        
        mode = 'parallel' if parallel else 'sequential'
        self.output(f'{mode} movement to bookmark {name}\n')
        
        self.lsbm(name, True)
        if len(excluded) > 0:
            self.output(f'excluded motors: {excluded}')

        ans = self.input('\nProceed (Y/n)?', default_value='y')
        if ans.lower() == 'y':
            if parallel:
                self.move_parallel(bookmark, excluded)
            else:
                self.move_sequential(bookmark, excluded)
        else:
            self.output('Aborted')
        
    def move_parallel(self, bookmark, excluded):
        mv_arg = []
        for m in bookmark:
            if m['name'] not in excluded:
                mv_arg.append(m['name'])
                mv_arg.append(m['position'])
        self.execMacro([self.mv_cmd] + mv_arg)
    
    def move_sequential(self, bookmark, excluded):
        for m in bookmark:
            if m['name'] not in excluded:
                self.execMacro([self.mv_cmd, m['name'], m['position']])
                self.output('')  # avoids output being overwritten
            


class lsbm(_bm):
    '''List existing bookmarks'''
    param_def = [
        ['filter', Type.String, Optional, 'regex to filter bookmarks'],
        ['show_current', Type.Boolean, Optional, 'show current positions']
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
    '''Save motor positions under name. Supports wildcards for motor names.'''
    param_def = [
        ['name', Type.String, None, 'Name of the bookmark'],
        [
            'motornames',
            [['filter', Type.String, None, 'Name or pattern of motors']],
            None, 'Motors'
        ]
    ]

    def run(self, name, motornames):
        self.load_from_env()
        new_bm = []
        motors = []
        for n in motornames:
            motors += self.findObjs(n, Type.Moveable, reserve=False)
        for motor in motors:
            pos = motor.getPosition()
            motorname = motor.getName()
            if pos is None:
                self.warning(f'Error: {motorname} has no position. Aborting.')
                return
            else:
                new_bm.append(dict(name=motorname, position=pos))
        if name in self.bm:
            self.info(f'Updating existing bookmark {name}')
        self.bm.update({name: new_bm})
        if self.autosavefile is not None:
            self.execMacro(['bm_export', self.autosavefile])
    

class bm_setmv(_bm):
    '''Set macro to be used for motor movement.'''
    param_def = [
        ['macroname', Type.String, None, 'Macro to use for motor movement'],
    ]

    def run(self, macroname):
        self.load_from_env()
        if macroname in self.getMacroNames():
            self.bm_dict['mv_cmd'] = macroname
        else:
            self.warning(f'{macroname} is not a macro')
        self.info(f'move command is {self.bm_dict["mv_cmd"]}')


class bm_export(_bm):
    '''Export bookmarks to json file.'''
    param_def = [
        ['fname', Type.String, Optional, 'json file name'],
    ]

    def run(self, fname):
        self.load_from_env()
        if fname is None:
            if self.autosavefile is None:
                self.warning('No filename given and backup file not set. '
                             'Aborting.')
                return
            fname = self.autosavefile
        if not fname.endswith('.json'):
                fname += '.json'
        with open(fname, 'w') as f:
            json.dump(self.bm_dict, f)
        self.info(f'Saved bookmarks to {fname}')


class bm_import(_bm):
    '''Import bookmarks from json file.'''
    param_def = [
        ['fname', Type.String, None, 'json file name']
    ]

    def run(self, fname):
        self.load_from_env()
        try:
            with open(fname, 'r') as f:
                bm = json.load(f)
            self.bm_dict.update(bm)
            self.info(f'Loaded bookmarks from {fname}')
        except FileNotFoundError:
            self.warning(f'{fname} not found')


class bm_remove(_bm):
    '''Remove bookmark from list.'''
    param_def = [
        ['name', Type.String, None, 'Name of the bookmark'],
    ]

    def run(self, name):
        self.load_from_env()
        try:
            self.bm.pop(name)
            self.info(f'Removed bookmark {name}.')
        except KeyError:
            self.warning(f'{name} is not a defined bookmark.')

class bm_backupfile(_bm):
    '''Query and set automatic backupfile'''
    param_def = [
        ['fname', Type.String, Optional, 'path to backupfile'],
    ]

    def run(self, fname):
        self.load_from_env()
        if fname is not None:
            fname = fname if fname.endswith('json') else fname + '.json'
            self.autosavefile = fname
            self.bm_dict.update(autosavefile=fname)
        self.output(f'Automatic backup file: {self.autosavefile}')
