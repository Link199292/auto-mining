# **auto-miner**

auto-miner is a python script which allows you to automate the process of ETH mining based on the current gas value. This may be useful for those people who live in places with an unfavourable electricity bill and who want to optimize the revenue.

## Reminders

- You have to **modify the wallet by your self**. To make things clear there's no single line in the code which interact with your wallet (no reading, no modification, ...)
- Some users suggested that if the miner is closed before a certain amount of time, the risk is that you won't get all the eth you would get if you would have kept the miner on instead. For this reason, a quick fix would be to **avoid "intermittent mining"**: this happens if the "wait_time_active" parameter is too small (e.g. 10 seconds). in fact, if the gas value fluctuates too much, you could face a situation for which the miner starts and stops repeatedly, falling in the situation mentioned above. Practically speaking, I would suggest you to keep a "wait_time_active" parameter high (e.g. 1 hour == 3600 seconds).
- Remember that this script's purpose is to **optimize your revenue**, taking into account also your GPU stress, not to maximize it.

## config.txt

The script is compatible with **lolminer** and **t-rex**. It run properly on **Windows** only.
In this file you are going to find a python dictionary which contains 6 keys:

- **'start_gas_threshold'**, it accepts a numerical value which defines the threshold after which the miner starts.
- **'stop_gas_threshold'**, it accepts a numerical value which defines the threshold after which the miner stops.
- **'wait_time_inactive'**, it accepts a numerical value, which defines how much time the script should wait for each gas value check (in seconds), when miner is OFF (I suggest to put an integer to get a better progress bar visualization).
- **'wait_time_active'**, it accepts a numerical value, which defines how much time the script should wait for each gas value check (in seconds), when miner is ON (I suggest to put an integer to get a better progress bar visualization).
- **API**, it accepts an API token from https://etherscan.io/apis#gastracker, you could try to put 'YourApiKeyToken', but this way you have some time limitations.
- **gas_oracle**, you have 3 options: 'SafeGasPrice', 'ProposeGasPrice', 'FastGasPrice' to choose from.

## logs.txt

A log file which takes note of the main events while the script is in execution is going to be created.
Events which are recorded: 
- a new update is available
- the miner has started and the gas value at that moment
- the miner has stopped and the gas value at that moment

## directory.txt

At beginning this is just an empty txt file. You could manually insert the position of the .bat file as plain text (e.g. C:\Users\username\miner\lolMiner_v1.28a_Win64\1.28a\mine_eth.bat), or just start the script and let it ask for the desired one (this is going to write and read from the first line of config.txt).
This script is provided with an auto-check of the latest version available (it means that you are going to be warned in the terminal and in the logs.txt file if your version differs to the latest available).
To avoid issues with this feature I suggest you to stick to the following structure:

lolminer:
- \Miner
    - \lolMiner_v1.28a_Win64
        - 1.28a
            - \eth_mine.bat

t-rex:
- \Miner
    - \t-rex-0.20.3-win
        - \ETH-ethermine.bat

## requirements.txt

list of packages required
 
## new stuff implemented

Now the script automatically retry connection (100 times) before stopping itself. This may happen if the server is not reachable in the moment you're trying to retrieve gas value's information from the API.
