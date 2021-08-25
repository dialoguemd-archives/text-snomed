#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

from os.path import abspath
import subprocess

__author__ = "Srikanth Mujjiga"
__copyright__ = "Srikanth Mujjiga"
__license__ = "mit"

class MetamapCommand:
    def __init__(self, metamap_path, input_file, output_file,use_only_snomed, debug):
        self.metamap_path = abspath(metamap_path)
        self.input_file = input_file
        self.output_file = output_file
        self.debug = debug
        self.use_only_snomed=use_only_snomed
        self.command = self._get_command()
       
        

    def _get_command(self):
        cmd = [self.metamap_path, "-c", "-Q", "4", "-y", "-K", "--sldi", "-I", "--XMLf1", "--negex"]
        if self.use_only_snomed:
            cmd+=['-R','SNOMEDCT_US']
        if not self.debug:
            cmd += ["--silent"]
        #cmd += [self.input_file, self.output_file]
        return cmd
        
    def conv_command(self,input_file):
        if self.debug:
            print('Converting file...')
        cmd = ['java','-jar','replace_utf8.jar']
        output_file = input_file.split('.')[0]+'conv.'+input_file.split('.')[1]
        '''
        #Not doing this since we make the user do it manually.
        cmd+=[input_file,output_file]
        
        if not self.debug:
            cmd += ["--silent"]
        if self.debug:
            print(cmd)
            print(' '.join(cmd))
        #if not self.debug:
        proc = subprocess.Popen(cmd)
        #else:
        #proc = subprocess.Popen(cmd)
        proc.wait()
        '''
        return output_file
        

    def execute(self,input_file, timeout=10):
        self.input_file = self.conv_command(input_file)
        #self.input_file = input_file
        self.command+= [self.input_file, self.output_file]
        if self.debug:
            print (self.command)
            print(' '.join(self.command))
        if not self.debug:
            proc = subprocess.Popen(self.command , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            proc = subprocess.Popen(self.command)
        proc.wait()
        #try:
        #    outs, errs = proc.communicate(timeout=timeout)
        #finally:
        #    proc.kill()
