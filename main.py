from tkinter import Tk
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
import requests
import os
import time
import subprocess
import datetime
from tqdm import tqdm
from pprint import pprint

def get_value(oracle, api):
    api = api
    url = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={api}'
    x = requests.get(url)
    x = eval(x.text)
    if 'result' not in x:
        print('could not retrieve information about gas value')
        count = 1
        reconnect = False
        while count < 101 and 'result' not in x:
            print(f'trying to reconnect: {count}/100 attempts', end = 'r', flush = True)
            x = requests.get(url)
            x = eval(x.text)
            if 'result' in x:
                reconnect = True
                x = x['result']
            count += 1
    else:
        x = x['result']
        reconnect = True

    if reconnect:
        return int(x[oracle])

    x = datetime.datetime.now()
    current = x.strftime('%D - %H:%M:%S')
    with open('logs.txt', 'a', encoding = 'utf-8') as w:
        w.write(f'{current} - miner STOPPED because it was not possible to retrieve any gas value information')
    raise ValueError('Connection Error: It was not possible to retrieve informations about gas value.\nPlease restart the script.')

def get_file_directory():
    '''get miner's bat dir or ask for one if not in directory.txt
       then return it
    '''
    position = False
    with open('directory.txt', encoding = 'utf-8') as r:
        line = r.readline()
        if line != '':
            position = True
            folder = line
    if not position:
        r = Tk()
        r.withdraw()
        folder = askopenfilename(title = "Select the miner's bat file")
        with open('directory.txt', 'w', encoding = 'utf-8') as w:
            w.write(folder)
    return folder

def which_miner():
    """return a bool:
       True : lolminer
       False : trex
    """
    path = get_file_directory()
    name = path.split('/')[-1]
    if name == 'mine_eth.bat':
        return True
    elif name == 'ETH-ethermine.bat':
        return False
    else:
        raise ValueError(f'your bat file {name} is not supported')

def available_version_lolminer():
    """return current available version of lolminer from Github
    """
    url = 'https://github.com/Lolliedieb/lolMiner-releases/releases'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', href = True)
    for link in links:
        if link['href'].startswith('/Lolliedieb/lolMiner-releases/releases/tag/'):
            available = link['href']
            break #break at the first link which satisfies the conditions (this must be the latest)
    available = available.split('/')[-1]
    return available

def available_version_trex():
    """return current available version of trex from their website
    """
    url = 'https://trex-miner.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page. content, 'html.parser')
    divs = soup.find_all('div', {'class' : 'dwn-item__name d-inline-flex'})
    available = [i.text.strip() for i in divs][0]
    available = available.split()
    return available[-1]

def current_version():
    """return current most recent folder and current most
       recent version of the miner
    """
    miner = which_miner()
    with open('directory.txt', encoding = 'utf-8') as r:
        current = r.readline()
    if miner:
        current = current.split('/')[-2] #take parent folder of the bat file
        current = ''.join([i for i in current if not i.isalpha()]) #take version's value and exclude alpha
        return current
    else:
        current = current.split('/')[-2] #take parent folder
        current = current.split('-')[-2] #take version's value
        return current

def read_config():
    '''read config values, store it in diz and return it
    '''
    with open('config.txt', encoding = 'utf-8') as r:
        file = r.read()
        diz = eval(file)
    return diz

def start_miner():
    curr = current_version()
    with open('directory.txt', encoding = 'utf-8') as r:
        path = r.readline()
    pos = path.rfind('/')
    folder, file = path[:pos + 1], path[pos + 1:]
    save = os.getcwd()
    os.chdir(folder)
    os.system(f'start cmd /k {file}')
    os.chdir(save)

def stop_miner(process_name):
    command = f'taskkill /im {process_name} /t /f'
    string = subprocess.getoutput(command)
    string = string.split('(')[-1]
    string = ''.join([i for i in string if i.isnumeric()])
    os.system(f'taskkill /pid {string} /t /f')

################################################################################

diz = read_config()

print(f'Your current settings:\n')
pprint(diz)
print('')

start_gas, stop_gas = diz['start_gas_threshold'], diz['stop_gas_threshold']
active_wait = diz['wait_time_active']
inactive_wait = diz['wait_time_inactive']
api = diz['API']
oracle = diz['gas_oracle']


miner = which_miner()

if miner:
    process_name = 'lolMiner.exe'
    av = available_version_lolminer()
    cr = current_version()
    if cr != av:
        print(f'*WARNING* You should update lolminer, {cr} >> {av}\n')
    else:
        print(f'lolminer is up to date {cr}\n')
else:
    process_name = 't-rex.exe'
    av = available_version_trex()
    cr = current_version()
    if av != cr:
        print(f'*WARNING* You should update trex, {cr} >> {av}\n')
    else:
        print(f'trex is up to date {cr}\n')

started = False

gas = get_value(oracle, api)
if gas > start_gas:
    start_miner()
    print(f'miner STARTED - gas value: {start_gas}')
    x = datetime.datetime.now()
    current = x.strftime('%D - %H:%M:%S')
    with open('logs.txt', 'a', encoding = 'utf-8') as w:
        w.write(f'{current} - miner STARTED - gas value {start_gas}\n')
    started = True

while True:
    if not started:
        for i in tqdm(range(inactive_wait), desc = 'Waiting to check gas value', ascii = True):
            time.sleep(1)
        gas = get_value(oracle, api)
        if gas >= start_gas:
            start_miner()
            print(f'miner STARTED with the following gas value: {gas}')
            x = datetime.datetime.now()
            current = x.strftime('%D - %H:%M:%S')
            with open('logs.txt', 'a', encoding = 'utf-8') as w:
                w.write(f'{current} - miner STARTED - gas value: {gas}\n')
            started = True
        else:
            print(f'found {gas}, expected {start_gas} to start\n')
    else:
        for j in tqdm(range(active_wait), desc = 'Time to check gas value', ascii = True):
            time.sleep(1)
        gas = get_value(oracle, api)
        if gas <= stop_gas:
            stop_miner(process_name)
            print(f'MINER STOPPED with the following gas value: {gas}')
            x = datetime.datetime.now()
            current = x.strftime('%D - %H:%M:%S')
            with open('logs.txt', 'a', encoding = 'utf-8') as w:
                w.write(f'{current} - miner STOPPED - gas value: {gas}\n')
            started = False
        else:
            print('found {gas}, expected {stop_gas} to stop\n')