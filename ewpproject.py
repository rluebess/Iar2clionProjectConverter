# -*- coding: utf-8 -*-

""" Module for converting EWP project format file
    @file
"""

import os
import json
import sys
from lxml import objectify


class EWPProject(object):
    """ Class for converting EWP project format file
    """

    def __init__(self, xmlFile):
        self.project = {}
        self.path, self.xmlFile = os.path.split(xmlFile)
        xmltree = objectify.parse(xmlFile)
        self.root = xmltree.getroot()

    def parseProject(self):
        """ Parses EWP project file for project settings
        """
        self.project['workspace name'] = self.root.configuration.name
        self.project['name'] = os.path.splitext(self.xmlFile)[0]

        # self.project['srcs_base'] = os.path.dirname(self.path)
        self.project['srcs_base'] = self.path
        self.project['srcs_base'] = self.myNormCase(self.project['srcs_base'])

        # Check for iar-vsc.json
        vsc_json_path = os.path.join(self.project['srcs_base'],  '.vscode', 'iar-vsc.json')
        if not os.path.exists(vsc_json_path):
            print(f"Error: {vsc_json_path} not found. Please import the project into VS Code first.")
            sys.exit(1)

        try:
            with open(vsc_json_path, 'r') as f:
                vsc_data = json.load(f)
                workbench_path = vsc_data['workbench']['path']
                self.project['toolkit_dir'] = os.path.join(workbench_path, 'arm')
        except Exception as e:
            print(f"Error reading {vsc_json_path}: {e}")
            sys.exit(1)
        self.project['toolkit_dir'] = self.myNormCase(self.project['toolkit_dir'])

        self.project['srcs'] = []
        self.expandGroups(self.root, self.project['srcs'])

        self.project['chip'] = ''
        self.project['defs'] = []
        self.project['incs'] = []
        self.project['dlib_config'] = ''
        self.project['diag_suppress'] = ''
        self.project['diag_error'] = ''
        self.project['linker_icf'] = ''
        self.project['linker_symbols'] = []
        for settings in self.root.configuration.iterchildren(tag='settings'):
            for option in settings.data.iterchildren(tag='option'):
                if option.name.text == 'OGChipSelectEditMenu':
                    self.project['chip'] = str(option.state)
                elif option.name.text == 'CCDefines':
                    for a_define in option.iterchildren(tag='state'):
                        self.project['defs'].append(a_define.text)
                elif option.name.text == 'CCDiagSuppress':
                    self.project['diag_suppress'] = str(option.state)
                elif option.name.text == 'CCDiagError':
                    self.project['diag_error'] = str(option.state)
                elif option.name.text == 'CCIncludePath2':
                    for a_include in option.iterchildren(tag='state'):
                        s = a_include.text
                        s = self.myNormCase(s)
                        self.project['incs'].append(s)
                elif option.name.text == 'RTConfigPath2':
                    s = str(option.state)
                    s = self.myNormCase(s)
                    s = s.replace('$TOOLKIT_DIR$', '')
                    self.project['dlib_config'] = s
                elif option.name.text == 'IlinkIcfFile':
                    s = str(option.state)
                    s = self.myNormCase(s)
                    self.project['linker_icf'] = s
                elif option.name.text == 'IlinkKeepSymbols':
                    for a_symbol in option.iterchildren(tag='state'):
                        self.project['linker_symbols'].append(a_symbol.text)

    def displaySummary(self):
        """ Display summary of parsed project settings
        """
        print('Project Workspace Name:' + self.project['workspace name'])
        print('Project Name:' + self.project['name'])
        print('Project toolkit dir:' + self.project['toolkit_dir'])
        print('Project chip:' + self.project['chip'])
        print('Project includes: ' + ' '.join(self.project['incs']))
        print('Project defines: ' + ' '.join(self.project['defs']))
        print('Project srcs: ' + ' '.join(self.project['srcs']))
        print('Project linker icf file:' + self.project['linker_icf'])
        print('Project linker symbols: ' + ' '.join(str(item)
              for item in self.project['linker_symbols']))

    def expandGroups(self, xml, sources):
        """ SearchGroups - project folders
        @param xml XML file element tagged 'group'
        @param sources List containing source files
        """
        if hasattr(xml, 'excluded'):
            return
        for el in xml.iterchildren(tag='file'):
            if hasattr(el, 'excluded'):
                continue
            s = str(el.name)
            s = self.myNormCase(s)
            sources.append(s)

        for el in xml.iterchildren(tag='group'):
            self.expandGroups(el, sources)

    def myNormCase(self, s):
        s = s.replace('\\', '/')
        s = s.replace('$PROJ_DIR$', '/')
        if s.startswith('/'):
            s = s[1:]
        os.path.normcase(s)
        return s

    def getProject(self):
        """ Return parsed project settings stored as dictionary
        @return Dictionary containing project settings
        """
        return self.project
