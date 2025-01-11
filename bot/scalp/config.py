
timeframe = '5m'
leverage = 20
invest = 10 # in USDT


amount_usdt = invest * leverage  # Amount in USDT to spend



accounts = [
    # {
    #     'username': 'amir',
    #     'api_key': 'h5J8MK5WP5t2DKADpFvOhoE98chuKJxsSB7ny239DWaO49amJmkmzFgus7wEZPpH',        
    #     'api_secret': 'JEk6zkYmIrwOS1JswoIdPfwndqpfXRsfc00dS4F8rJS6c93qa8PRpLecOpCc8peb'
    # },
    # {
    #   	'username': 'shuhaib',
    #     'api_key': '1Cno4uAqF0XMZ5nNTCy2wSXL7wG4cXypnNVGnXdtELkadzhr0N2TJANVVqCRG7yV',        
    #     'api_secret': 'Sc96uxWOVP2XboZZgsIOEASoaEnq1spMMTpUx1axvV2noZ3tAbPGkRBhpE4SAhVQ'
    # },
    # {
    #     'username': 'robin',
    #     'api_key': 'Pisn0yAZzygK789YadoN42wc3r7400aYPmsuLc65i2pHdlrIcj6b0fjG2nWD0PuJ',        
    #     'api_secret': 'SFIp83nmWHogArpQMN6saTnq6OH5pMpKwdHwZNOt6CPIuItnIVMyS4t9hiTnvue0'
    # }
]

# symbols = ['LTC/USDT']

symbols = [
           'ETH/USDT',
           'BNB/USDT',
           'LTC/USDT',
           'SOL/USDT',
           'XRP/USDT',
           'ADA/USDT',
           'DASH/USDT',
           'DOT/USDT',
           'FTM/USDT',
           'NEAR/USDT',
           'AAVE/USDT',
           'GALA/USDT',
           'FET/USDT',
        ]


# no_btc_dependent = ['ADA/USDT', 'FTM/USDT', 'AAVE/USDT',  'FET/USDT']
no_btc_dependent = []

# BOT 
bot_name = "Scalping Bot"
notify = True # False for server run 

support_resist_bar_width = 40


# from_date = '2024-12-28 00:00:00'
from_date = None
