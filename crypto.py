from tkinter import *
import sqlite3
from tkinter import messagebox
import requests
import time
from threading import Thread

root = Tk()
root.title('Crypto')
root.iconbitmap('images/icon.ico')

# Instantiate/Initialise variabls
sort_by = ["Coin (A-Z)","Coin (Z-A)", "Amount (L-H)", "Amount (H-L)", "Paid (L-H)", "Paid (H-L)", "Value (L-H)", "Value (H-L)", "Profit (L-H)", "Profit (H-L)"]
sort_value = StringVar()
sort_value.set(sort_by[0])
global coins, coin_totals, coin_costs, coin_avgs, coin_value, coin_price, coin_profitloss
coins = []
coin_totals = {}
coin_costs = {}
coin_avgs = {}
coin_value = {}
coin_price = {}
coin_profitloss = {}
list_of_labels = []

# Methods
def buildData():
	global coins, coin_totals, coin_costs, coin_avgs
	conn = sqlite3.connect('database/database.db')
	c = conn.cursor()
	c.execute("SELECT * FROM transactions")
	data = c.fetchall()
	c.execute("SELECT * FROM transactions WHERE from_ = 'GBP' ORDER BY date_yy, date_mm, date_dd")
	gbp_data = c.fetchall()
	c.execute("SELECT * FROM transactions WHERE from_ <> 'GBP' ORDER BY date_yy, date_mm, date_dd")
	not_gbp_data = c.fetchall()
	c.execute("SELECT * FROM transactions WHERE to_ = 'GBP' ORDER BY date_yy, date_mm, date_dd")
	paid_out_data = c.fetchall()
	conn.commit()
	conn.close()

	# Get unique coins
	for row in data:
		coins.append(row[2])
	coins = list(set(coins))
	coins.sort()

	# Get coin totals where GBP was used to acquire
	for coin in coins:
		total = 0
		cost = 0
		for row in gbp_data:
			if row[2] == coin:
				total += row[3]
				cost += row[4]
		coin_totals[coin] = total
		coin_costs[coin] = cost

	# Ammend coin totals where non-GBP was used to acquire (inter-trading of coins)
	for row in not_gbp_data:
		coin_costs[row[0]] = coin_costs[row[0]] * (1 - (row[1] / coin_totals[row[0]]))
		coin_totals[row[0]] = coin_totals[row[0]] - row[1]
		coin_costs[row[2]] = coin_costs[row[2]] + row[4]
		coin_totals[row[2]] = coin_totals[row[2]] + row[3]

	for row in paid_out_data:
		# coin_totals[row[0]] = coin_totals[row[0]] - row[1]
		if row[4] > coin_costs[row[0]]:
			coin_costs[row[0]] = 0
		else:
			coin_costs[row[0]] = coin_costs[row[0]] - row[4]

	for coin in coins:
		if coin_totals[coin] == 0:
			coins.remove(coin)

	# Calculate average cost per coin
	for coin in coins:
		if coin_totals[coin] > 0:
			if coin_totals[coin] < 1:
				coin_avgs[coin] = coin_costs[coin]
			else:
				coin_avgs[coin] = coin_costs[coin] / coin_totals[coin]
		else:
			coin_avgs[coin] = 0


	m_title_coin = Label(frame_coins, text="Coin", anchor=W)
	m_title_amount = Label(frame_coins, text="Amount", anchor=W)
	m_title_paid = Label(frame_coins, text="Paid", anchor=W)
	m_title_avg = Label(frame_coins, text="Average", anchor=W)
	m_title_price = Label(frame_coins, text="Price ea", anchor=W)
	m_title_value = Label(frame_coins, text="Value", anchor=W)
	m_title_pl = Label(frame_coins, text="P/L", anchor=W)

	m_title_coin.grid(row=0,column=0, sticky=EW)
	m_title_amount.grid(row=0,column=1, sticky=EW)
	m_title_paid.grid(row=0,column=2, sticky=EW)
	m_title_avg.grid(row=0,column=3, sticky=EW)
	m_title_price.grid(row=0,column=4, sticky=EW)
	m_title_value.grid(row=0,column=5, sticky=EW)
	m_title_pl.grid(row=0,column=6, sticky=EW)
	try:
		getData()
	except Exception as e:
		messagebox.showwarning("No Data","There is no data to display just yet - add transactions via the DB (function implementation in development).\r\nError shows:\r\n" + str(e))

def getData():
	requ_arg = ''
	for coin in coins:
		if coin != "HNT":
			requ_arg += coin + ','
		else:
			requ_arg += "HELIUM" + ','
	requ_arg = requ_arg[:len(requ_arg)-1]
	print("Request Args:", requ_arg)

	response = requests.get("https://api.nomics.com/v1/currencies/ticker?key=43850ebeec9012189124eb63e9effa2602f41bee&ids="+requ_arg)
	if response:
		for r in response.json():
			if r['id'] == 'HELIUM':
				r['id'] = 'HNT'
			print(r['id'],r['price'])
			coin_price[r['id']] = r['price']
			coin_value[r['id']] = float(r['price'])*float(coin_totals[r['id']])
			coin_profitloss[r['id']] = float(coin_value[r['id']]) - float(coin_costs[r['id']])
		row = 1
		portfolio_value = 0.0
		portfolio_cost = 0.0
		# m_portfolio_cost_value_label.grid_forget()
		# m_portfolio_value_value_label.grid_forget()
		for coin in coins:
			print(coin)
			if coin == 'GBP':
				continue
			portfolio_value += float(coin_value[coin])
			portfolio_cost += float(coin_costs[coin])
			row_of_labels = []
			m_coin_name = Label(frame_coins, text=coin, anchor=W)
			row_of_labels.append(m_coin_name)
			m_coin_amount = Label(frame_coins, text=round(coin_totals[coin],8), anchor=W)
			row_of_labels.append(m_coin_amount)
			m_coin_paid = Label(frame_coins, text=round(coin_costs[coin],2), anchor=W)
			row_of_labels.append(m_coin_paid)
			m_coin_avg = Label(frame_coins, text=round(coin_avgs[coin],4), anchor=W)
			row_of_labels.append(m_coin_avg)
			m_coin_price = Label(frame_coins, text=round(float(coin_price[coin]),4), anchor=W)
			row_of_labels.append(m_coin_price)
			if float(coin_value[coin]) < float(coin_costs[coin]):
				bg = 'red'
			else:
				bg = 'green'
			m_coin_value = Label(frame_coins, text=round(float(coin_value[coin]),4), anchor=W, bg=bg)
			row_of_labels.append(m_coin_value)
			m_coin_pl = Label(frame_coins, text=round(float(coin_profitloss[coin]), 4), anchor=W, bg=bg)
			row_of_labels.append(m_coin_pl)
			m_coin_name.grid(row=row,column=0, sticky=EW)
			m_coin_amount.grid(row=row,column=1, sticky=EW)
			m_coin_paid.grid(row=row,column=2, sticky=EW)
			m_coin_avg.grid(row=row,column=3, sticky=EW)
			m_coin_price.grid(row=row,column=4, sticky=EW)
			m_coin_value.grid(row=row,column=5, sticky=EW)
			m_coin_pl.grid(row=row,column=6, sticky=EW)
			list_of_labels.append(row_of_labels)
			row += 1
		if portfolio_value > portfolio_cost:
			bg = 'green'
		else:
			bg = 'red'
		percentage = (portfolio_value / portfolio_cost * 100) - 100
		m_portfolio_value_value_label = Label(root,text=round(float(portfolio_value),2),bg=bg)
		m_portfolio_cost_value_label = Label(root,text=str(round(float(portfolio_cost),2)) + " / " + str(round(float(percentage),2)) + "%",bg=bg)
		m_portfolio_value_value_label.grid(row=0, column=3)
		m_portfolio_cost_value_label.grid(row=1, column=3)
	else:
		print("Failed Response:", response.status_code)
	print("-----Done-----")
	Tk.update(root)
	# root.after(10000, getData())

def printCoins():
	for coin in coins:
		print(coin, coin_totals[coin], coin_costs[coin])	
	print("---")

def clearDisplay():
	for row in list_of_labels:
		for label in row:
			label.grid_forget()	
	m_portfolio_value_value_label.grid_forget()	
	m_portfolio_cost_value_label.grid_forget()	

def selfSort(coins_list, htol):
	global coins
	sorted_list = []
	i = 0
	for vals in coins_list.items():
		if vals[1] == 0:
			continue
		if i == 0:
			sorted_list.insert(0, (vals[0],vals[1]))
		else:
			index = 0
			for sorts in sorted_list:
				if "(L-H)" in htol:
					if vals[1] < sorts[1]:
						continue
					else:
						index += 1
				else:
					if vals[1] > sorts[1]:
						continue
					else:
						index += 1
			sorted_list.insert(index, (vals[0],vals[1]))
		i += 1
	coins = []
	for vals in sorted_list:
		coins.append(vals[0])

def sort(value):
	global coins
	print("ok", value)
	clearDisplay()
	if value == "Coin (A-Z)":
		coins.sort()
	if value == "Coin (Z-A)":
		coins.sort(reverse=True)
	if value == "Amount (L-H)":
		selfSort(coin_totals, "Amount (L-H)")
	if value == "Amount (H-L)":
		selfSort(coin_totals, "Amount (H-L)")
	if value == "Paid (L-H)":
		selfSort(coin_costs, "Paid (L-H)")
	if value == "Paid (H-L)":
		selfSort(coin_costs, "Paid (H-L)")
	if value == "Value (L-H)":
		selfSort(coin_value, "Value (L-H)")
	if value == "Value (H-L)":
		selfSort(coin_value, "Value (H-L)")
	if value == "Profit (L-H)":
		selfSort(coin_profitloss, "Value (L-H)")
	if value == "Profit (H-L)":
		selfSort(coin_profitloss, "Value (H-L)")
	getData()

# Instantiate root GUI objects
m_transact_button = Button(root, text="Transact")
m_transaction_history_button = Button(root, text="Transaction History")
m_sort_by_label = Label(root, text="Sort by:")
m_sort_by_dropdown = OptionMenu(root, sort_value, *sort_by, command=sort)
m_portfolio_value_label = Label(root, text="Portfolio Value:", anchor=W)
m_portfolio_cost_label = Label(root, text="Cost / PL:", anchor=W)
m_portfolio_value_value_label = Label(root,text="0.0")
m_portfolio_cost_value_label = Label(root,text="0.0 / 0%")

# Grid root GUI objects
m_transact_button.grid(row=0, column=0, padx=(5,0), pady=(5,0))
m_transaction_history_button.grid(row=0, column=1, padx=(0,5), pady=(5,0), sticky=EW)
m_sort_by_label.grid(row=1, column=0, padx=5)
m_sort_by_dropdown.grid(row=1, column=1, padx=5, sticky=EW)
m_portfolio_value_label.grid(row=0, column=2, stick=EW)
m_portfolio_cost_label.grid(row=1, column=2, stick=EW)
m_portfolio_value_value_label.grid(row=0, column=3)
m_portfolio_cost_value_label.grid(row=1, column=3)

frame_coins = LabelFrame(root, text="Coins", padx=5, pady=5)
frame_coins.grid(row=2,column=0, columnspan=10)

buildData()

mainloop()