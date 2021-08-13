# CryptoTracker

A simple tracker for current holdings in crypto currencies. Will display the coin, amount owned, total price paid, average price of each coin held, current price for a single coin, current valuation of your holding, and the profit/loss for that specific coin holding.

The database allows transacting between any 'ticker' as this field is entered manually and not from a pool of actual coins. This means you can use 'GBP' (£) as your source 'coin' and input any other receiving coin. At present, 'GBP' is the only source coin that will not be displayed as a currency holding on the application, but more will be added (USD, EURO, etc).

# Features to be added

First and foremost will be the 'Transact' function and associated GUI that will allow you to add transactions without having to interface with the DB directly (using such tools like DB Browser SQLite).

High on the list is to add regular updates via Threading or tkinter's .after() function. As it stands the application only refreshes the valuations when an option within the 'Order By' dropdown is selected (can be the same selection as the current selection).

Adding in matplotlib to display graphs showcasing the coin's history, and potentially adding your P/L valuation over the coin's history too.

A transaction history to show what has been traded with what, and when. Further improvements could include showing only transactions of a specific coin, as well as showing a timeline of trades made to allow frequency of purchases visualisation.
