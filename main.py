from tkinter.filedialog import askdirectory
from bs4 import BeautifulSoup
import requests
import os
import ast
import time
import subprocess
import datetime
from tqdm import tqdm

def get_value():
    """Get current gas value and return it as int
    """
    url = 'https://ethgasstation.info/index.php'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    divs = soup.find_all('div', {'class' : 'count standard'})

    value = [i.text.strip() for i in divs][0]
    return int(value)

def get_main_directory():
    '''get miner's dir or ask for one if not in directory.txt
       then return it
    '''
    position = False
    with open('directory.txt', encoding = 'utf-8') as r:
        line = r.readline()
        if line != '':
            position = True
            folder = line
    if not position:
        folder = askdirectory(title = "Select miner's folder")
        with open('directory.txt', 'w', encoding = 'utf-8') as w:
            w.write(folder)
    return folder

def current_version():
    """return current most recent folder and current most
       recent version of the miner
    """
    with open('directory.txt', encoding = 'utf-8') as r:
        path = r.readline()
        possible_versions = os.listdir(path)

    new = []
    for possible in possible_versions:
        folder_name = possible
        version_name = folder_name.split('_')[1].replace('v', '')
        version_name = ''.join([i for i in version_name if not i.isalpha()])
        new.append((folder_name, version_name))
    folder, version = sorted(new, key = lambda x : x[0])[-1]
    return folder, version

def available_version():
    """return current available version of miner from Github
    """
    url = 'https://github.com/Lolliedieb/lolMiner-releases/tags'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', href = True)
    for link in links:
        if link['href'].startswith('/Lolliedieb/lolMiner-releases/releases/tag/'):
            available = link['href']
            break
    available = available.split('/')[-1]
    return available

def read_config():
    '''read config values, store it in diz and return it
    '''
    with open('config.txt', encoding = 'utf-8') as r:
        file = r.read()
        diz = ast.literal_eval(file)
    return diz

def start_miner():
    with open('directory.txt', encoding = 'utf-8') as r:
        path = r.readline()
    dirs = os.listdir(path)
    folder_to_open = current_version()[0]
    for d in dirs:
        if folder_to_open in d:
            folder_to_open = d
    last = os.listdir(os.path.join(path, folder_to_open))[0]
    res = os.path.join(path, folder_to_open, last).replace('/', '\\')
    os.chdir(res)
    # os.system('mine_eth.bat')
    os.system('start cmd /k mine_eth.bat')

def stop_miner():
    command = 'taskkill /im lolMiner.exe /t /f'
    string = subprocess.getoutput(command) #execute and get output
    string = string.split('(')[-1]
    string = ''.join([i for i in string if i.isnumeric()])
    os.system(f'taskkill /pid {string} /f')

################################################################################

#read config file
diz = read_config()

print(diz)

#get threshold gas value
threshold = diz['fuel_threshold']
active_wait = (int(diz['wait_time_active'] / 100), 100)
inactive_wait = (int(diz['wait_time_inactive'] / 100), 100)

#get main dir of miner
first_dir_layer = get_main_directory()

#get dir which contains the versions and get the most updated version from folder
second_dir_layer, current= current_version()

available = available_version()

#ask to update miner if a new update is available
if current != available:
    print('*WARNING* You should update your miner')
    x = datetime.datetime.now()
    current = x.strftime('%D - %H:%M:%S')
    with open('logs.txt', 'a', encoding = 'utf-8') as w:
        w.write(f'{current}, you should UPDATE your miner\n')
else:
    print('Your miner is up to date')
print(f'Waiting for an appropriate gas value >= {threshold}')


started = False

#check gas value and start miner if gas value meets threshold value
gas = get_value()
if gas > threshold:
    start_miner()
    print(f'MINER STARTED with the following gas value: {gas}')
    x = datetime.datetime.now()
    current = x.strftime('%D - %H:%M:%S')
    with open('logs.txt', 'a', encoding = 'utf-8') as w:
        w.write(f'{current} - miner STARTED - gas value: {gas}\n')
    started = True


#Start miner or stop it depending on the threshold condition:
#    -If miner is active, check each hour the gas value (if the threshold condition is met,
#     shut the miner down).
#    -If miner is inactive, check each five minutes if the gas value meets the threshold
#     (and eventually turn the miner on).

while True:
    if not started:
        for i in tqdm(range(inactive_wait[1]), desc = 'Time to check gas value'):
            time.sleep(inactive_wait[0])
        gas = get_value()
        if gas >= threshold:
            start_miner()
            print(f'miner STARTED with the following gas value: {gas}')
            x = datetime.datetime.now()
            current = x.strftime('%D - %H:%M:%S')
            with open('logs.txt', 'a', encoding = 'utf-8') as w:
                w.write(f'{current} - miner STARTED - gas value: {gas}\n')
            started = True
    else:
        for j in tqdm(range(active_wait[1]), desc = 'Time to check gas value'):
            time.sleep(active_wait[0])
        gas = get_value()
        if gas < threshold:
            stop_miner()
            print(f'MINER STOPPED with the following gas value: {gas}')
            x = datetime.datetime.now()
            current = x.strftime('%D - %H:%M:%S')
            with open('logs.txt', 'a', encoding = 'utf-8') as w:
                w.write(f'{current} - miner STOPPED - gas value: {gas}\n')
            started = False