
# Copyright (c) 2015 Calin Crisan
# This file is part of motionEyeOS.
#
# motionEyeOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 

import logging
import os.path

from config import additional_config

import streameyectl


CONFIG_TXT = '/boot/config.txt'

OVERCLOCK = {
    700: '700|250|400|0',
    800: '800|250|400|0',
    900: '900|250|450|0',
    950: '950|250|450|0',
    1000: '1000|500|600|6',
    1001: '1001|500|500|2'
}

def _get_board_settings():
    gpu_mem = 128
    camera_led = True
    arm_freq = 700

    if os.path.exists(CONFIG_TXT):
        logging.debug('reading board settings from %s' % CONFIG_TXT)

        with open(CONFIG_TXT) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split('=', 1)
                if len(parts) != 2:
                    continue
                
                name, value = parts
                name = name.strip()
                value = value.strip()

                if name == 'gpu_mem':
                    gpu_mem = int(value)
                
                elif name == 'arm_freq':
                    arm_freq = int(value)
                    
                elif name == 'disable_camera_led':
                    camera_led = value == '0'
    
    #overclock = OVERCLOCK.get(arm_freq, '700|250|400|0')

    s = {
        'gpuMem': gpu_mem,
        #'overclock': overclock,
        'cameraLed': camera_led
    }

    #logging.debug('board settings: gpu_mem=%(gpuMem)s, overclock=%(overclock)s, camera_led=%(cameraLed)s' % s)
    logging.debug('board settings: gpu_mem=%(gpuMem)s, camera_led=%(cameraLed)s' % s)

    return s


def _set_board_settings(s):
    s.setdefault('gpuMem', 128)
    #s.setdefault('overclock', '700|250|400|0')
    s.setdefault('cameraLed', True)
    
    old_settings = _get_board_settings()
    if s == old_settings:
        return # nothing has changed

    seen = set()

    #logging.debug('writing board settings to %s: ' % CONFIG_TXT + 
    #        'gpu_mem=%(gpuMem)s, overclock=%(overclock)s, camera_led=%(cameraLed)s' % s)
    logging.debug('writing board settings to %s: ' % CONFIG_TXT + 
            'gpu_mem=%(gpuMem)s, camera_led=%(cameraLed)s' % s)
    
    #arm_freq, gpu_freq, sdram_freq, over_voltage = s['overclock'].split('|')

    lines = []
    if os.path.exists(CONFIG_TXT):
        with open(CONFIG_TXT) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            line = line.strip('#')

            try:
                name, _ = line.split('=', 1)
                name = name.strip()

            except:
                continue
            
            seen.add(name)

            if name == 'gpu_mem':
                lines[i] = '%s=%s' % (name, s['gpuMem'])

            #elif name == 'arm_freq':
            #    lines[i] = 'arm_freq=%s' % arm_freq
            #    
            #elif name in ['gpu_freq', 'core_freq']:
            #    lines[i] = '%s=%s' % (name, gpu_freq)
            #    
            #elif name == 'sdram_freq':
            #    lines[i] = 'sdram_freq=%s' % sdram_freq
            #    
            #elif name == 'over_voltage':
            #    lines[i] = 'over_voltage=%s' % over_voltage
                
            elif name == 'disable_camera_led':
                lines[i] = 'disable_camera_led=%s' % ['1', '0'][s['cameraLed']]

    if 'gpu_mem' not in seen:
        lines.append('gpu_mem=%s' % s['gpuMem'])

    #if 'arm_freq' not in seen:
    #    lines.append('arm_freq=%s' % arm_freq)

    #if 'gpu_freq' not in seen:
    #    lines.append('gpu_freq=%s' % gpu_freq)

    #if 'sdram_freq' not in seen:
    #    lines.append('sdram_freq=%s' % sdram_freq)

    #if 'over_voltage' not in seen:
    #    lines.append('over_voltage=%s' % over_voltage)

    if 'disable_camera_led' not in seen:
        lines.append('disable_camera_led=%s' % ['1', '0'][s['cameraLed']])
        
    logging.debug('remounting /boot read-write')
    if os.system('mount -o remount,rw /boot'):
        logging.error('failed to remount /boot read-write')

    with open(CONFIG_TXT, 'w') as f:
        for line in lines:
            if not line.strip():
                continue
            if not line.endswith('\n'):
                line += '\n'
            f.write(line)


@additional_config
def boardSeparator():
    return {
        'type': 'separator',
        'section': 'expertSettings',
        'advanced': True
    }


@additional_config
def gpuMem():
    return {
        'label': 'GPU Memory',
        'description': 'set the amount of memory reserved for the GPU (choose at least 96MB if you use the CSI camera board)',
        'type': 'number',
        'min': '16',
        'max': '944',
        'section': 'expertSettings',
        'advanced': True,
        'reboot': True,
        'get': _get_board_settings,
        'set': _set_board_settings,
        'get_set_dict': True
    }


@additional_config
def cameraLed():
    return {
        'label': 'Enable CSI Camera Led',
        'description': 'control the led on the CSI camera board',
        'type': 'bool',
        'section': 'expertSettings',
        'advanced': True,
        'reboot': True,
        'get': _get_board_settings,
        'set': _set_board_settings,
        'get_set_dict': True
    }


#@additional_config
#def overclock():
#    return {
#        'label': 'Overclocking',
#        'description': 'choose an overclocking preset for your Raspberry PI',
#        'type': 'choices',
#        'choices': [
#            ('700|250|400|0', 'none (700/250/400/0)'),
#            ('800|250|400|0', 'modest (800/250/400/0)'),
#            ('900|250|450|0', 'medium (900/250/450/0)'),
#            ('950|250|450|0', 'high (950/250/450/0)'),
#            ('1000|500|600|6', 'turbo (1000/500/600/6)'),
#            ('1001|500|500|2', 'Pi2 (1000/500/500/2)')
#        ],
#        'section': 'expertSettings',
#        'advanced': True,
#        'reboot': True,
#        'get': _get_board_settings,
#        'set': _set_board_settings,
#        'get_set_dict': True
#    }

