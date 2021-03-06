#!/usr/bin/python

import sys, os, re
from pyudev import Context


def ini_get(key, cfg_file):
    pattern = r'[ |\t]*' + key + r'[ |\t]*=[ |\t]*'
    value_m = r'"*([^"\|\r]*)"*'
    value = ""
    with open(cfg_file, "r") as ini_file:
        for line in ini_file:
            if re.match(pattern, line):
                value = re.sub(pattern + value_m + '.*\n', r'\1', line)
                break
    return value


def get_btn_num(btn, config_file):
    for cfg in config_file, "/opt/retropie/configs/all/retroarch.cfg":
        num = ini_get('input_' + btn + '_btn', cfg)
        if num: return num
        num = ini_get('input_player1_' + btn + '_btn', cfg)
        if num: return num
    return ""


def get_button_codes(dev_path):
    retroarch_cfg = "/opt/retropie/configs/all/retroarch.cfg"
    js_cfg_dir = "/opt/retropie/configs/all/retroarch-joypads/"
    enter_btn = "a"
    tab_btn = "b"
    btn_codes = []
    default_codes = ['\n', '\t']
    js_cfg = ""
    dev_name = ""

    # getting joystick name
    for device in Context().list_devices(DEVNAME=dev_path):
        dev_name_file = device.get('DEVPATH')
        dev_name_file = '/sys' + os.path.dirname(dev_name_file) + '/name'
        for line in open(dev_name_file, "r"):
            dev_name = line.rstrip('\n')
            break
    if not dev_name:
        return default_codes

    # getting retroarch config file for joystick
    for f in os.listdir(js_cfg_dir):
        if f.endswith(".cfg"):
            if ini_get('input_device', js_cfg_dir + f) == dev_name:
                js_cfg = js_cfg_dir + f
                break
    if not js_cfg:
        return default_codes

    # getting configs for "a" and "b" buttons
    if ini_get('menu_swap_ok_cancel_buttons', retroarch_cfg) == "true":
        enter_btn = "b"
        tab_btn = "a"
    enter_btn_num = get_btn_num(enter_btn, js_cfg)
    if not enter_btn_num:
        return default_codes
    tab_btn_num = get_btn_num(tab_btn, js_cfg)
    if not tab_btn_num or tab_btn_num == enter_btn_num:
        return default_codes

    enter_btn_num = int(enter_btn_num)
    tab_btn_num = int(tab_btn_num)

    # building the button codes list
    biggest_num = tab_btn_num if tab_btn_num > enter_btn_num else enter_btn_num
    for i in range(biggest_num + 1):
        if i == enter_btn_num:
            btn_codes.append('\n')
        elif i == tab_btn_num:
            btn_codes.append('\t')
        else:
            btn_codes.append("")
        
    return btn_codes


codes = []
codes = get_button_codes(sys.argv[1])
print codes
