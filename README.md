<h1 align="center">Scroll Soft</h1>

Script to interact with contracts in Scroll. 

<b>TG:</b> https://t.me/cryptoscripts

<b>Donations:</b> 0x763cDEa4a54991Cd85bFAd1FD47E9c175f53090B

---

<h2> Modules </h2>

1. Main Bridge (deposit/withdraw)

2. Orbiter bridge

3. Swaps on PunkSwap, SkyDrome, SpaceFi

4. Liquidity on PunkSwap, SkyDrome, SpaceFi

5. Dmail

6. Zerius (Mint + Bridge)

7. Deposit from OKX / Withdraw to OKX 

8. All transactions are saved to the database.

---
<h2>Some information</h2>

The routes are made randomly so that the patterns on the wallets do not match.
There is a random pause between module executions, which can also be configured.
You can also adjust the maximum gas value, thereby reducing transaction fees.
The script implements a circular system with output to OKX sub-accounts,
you can simply launch the bot with a balance on OKX, and it will scroll 
through all your wallets. In order for the cycle system to work, you need to enable 
at least one bridge each with deposit and withdrawal variables. 
In the future, we will be able to immediately withdraw money to OKX 
as soon as they add such an option. Also, all transactions will be stored in a
database. The database will also contain information about how many interactions 
there were with a certain contract and the volumes on it.

---
<h2>Settings</h2>

To configure modules you need to go to the file config.py. 
Inside there will be information on each variable in a specific module type. For other modules, for example, 
for another swap on some dex, the settings work in the same way
