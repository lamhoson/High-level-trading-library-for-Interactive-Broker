# -*- coding: utf-8 -*-
""" NEVER use time.sleep in ib_insync related functions, use ibs.IB.sleep(seconds) 
Version tested with de-normalised dayTrade1Training&Test which version MUST >=3.9

DeTa libraries: !! CONST_PAD_SIZE=2 instead of 1, fr 11feb2020 !!
Axiom:
1) Sentiment factors reflected in morning prices.
    1.1) Price, volume spatial relationships reflecting price uptrend probability
2) Portfolio management principle applies across a big enough capital market(s)
3) Afternoon, two time-points provide a time-window for price-up. 
    3.1) Short time-window has less so-called profitable, but the rate of price-up is greater.

Theorem:
1) Transaction costs profitable stock-day is independent of an individual stock.
2) Availability of profitable-day is independent of OVERALL capital market sentiments
    2.1) TENTATIVE ONLY may also independent of the capital market as these are traders' behavior.

Note:
1) In reality, bought stock may need several trades to be sold across an hour or hours and
    cannot be fully sold before market close, 5nov2020.
    
@author: Admin
ver1.0, 25Jul2019: - added two trading related constants
ver1.1, 4Aug2019: - added dataset save and read functions for functional encapsulation. Used H5 format
ver1.1, 3Feb2020: - added the Classifier, Dave, price-volumn tuple imageify related constants
Ver1.2, 11Feb2020: - CONST_PAD_SIZE=2 instead of 1 FROM this version ONWARD
Ver1.3, 14feb2020: - added minlength=2 to np.bincount() in fix runtime bug if only one class in the data input. And print recall in CM plot.
Ver1.4, 4Mar2020: - added PRICES_PER_DAY_4PM=PRICES_PER_DAY_0105PM +(60+60+60-5) # Up to 4:00p, 3mar2020
                    PRICE_4_00p = 390
Ver2.0, 6Mar2020  - change all PRICE_XX_XX index location after cut 12:00-12:59 dummy prices info
ver3.0, 9Mar2020 - handle 9:30a-4:08p FULL daily price NEW FORMAT
Ver3.1, 17Mar2020 - added Classes Dave and DaveBaseClass
Ver3.2, 23Mar2020 - add DaveBaseClass, Deleted DaveLite Class and added classfiPredictDf()
Ver3.4, 1Apr2020 - additional return max price and max volumn
Ver3.5, 14Apr2020 - Not "DaveOutput.xlsx" output anymore in Dave.classfiPredict()  
Ver3.6, 16Apr2020 - Add:
                    In additional to .predict_class(), use .predict() as a similarity measure on the predicted profitstock to what the NN learnt from trainset
                    results[SIM_MEASURE]=similarity # prediction result probability as similarity measures for prioritisation or etc..
Ver3.6.1, 14may2020 - add SLICE_MORN_END=PRICE_11_59a+1 for master control of 11:59a or 1:05p for morning trainset. Other touch-ups
Ver3.7  19may2020 - add SIM_MEASURE in modifying Dave.predict() profitable output from default 0.5 to SIM_MEASURE
                    add getHkexStockList()
Ver3.7.1 21may2020 - add noticeTraders() by email.
Ver3.8 22may2020 - make Dave's classifier prediction-output probability threhold variable
                   with default at 0.8 from Keras's 0.5
Ver3.8 26may2020 - add getDetaConfig(), removed SLICE_MORN_END
ver3.8.1 29amy2020 - getDetaConfig() return one list instead of six variables
ver3.8.2 29may2020 - Use getDetaConfig() for sliceTimeStart, sliceTimeEnd instead PRICE_XX constants
ver3.9 4jun2020 -  All predict()s output prices&volumn DENORMALIZED
                      Changed name of the getProfitaleDf() to getProfitDfDenormal() in emphrasing O/P prices&volumn denormalized by multipy Maxs
ver4.0 4jun2020 - First version tested with denormalised dayTrado1Training&Test which version MUST >=3.9
ver4.2 8jun2020 - Variable priceVolDf price-volumn length, e.g. 9_00a to 4_08p or 11:59a or others are feasible, (PRICE_END+1 -PRICE_START)
                  It is the variable aDayLength # oneDay price-vol lenght, default=(PRICE_END+1 -PRICE_START=0) but can be modified when necessary.
ver5.0 12june2020 - used styleframe for Excel. Move-in decideBuyLotSize(), transactionFee(), amTradingAmountCalculation() from semiAutoDayTrade01.py
ver5.3 14-15jun2020 - added checkTestMaxRoi(), setTargetRunDateTime(), MMD is added.
ver5.3.1 16jun2020 - fitSaveStyleFrame(), fixed StyleFrame bug 16jun2020:'numpy.ndarray' object has no attribute 'style'
ver5.3.3 6jul2020 - add checkIsTradeDay(), joinIntoCwPath() and other touch ups.
ver5.3.4 8jul2020 - add retry into getHkexStockList()
ver5.3.5 13jun2020 - add httpDownloadNSaveExcel() which getHkexStockList() reliable with email alert to admin.
ver6.0 18jul2020 - add getSehkTickSize(), sehkTickRoundPrice()
ver6.1 20jul2020 - add contracts=creatTradeContracts(),bOrders=creatBracketOrders(),bTrades=placeBracketOrders()
                   and added getDetaConfig()'s, 7)Time index to cancel&replace all Bracket order as Market Sell order
ver7.0 27jul2020 - with all key IB trading functions API. Added WARNING_AMD as a temp fix.
ver7.1 28jul2020 - add closePositions() and other touch ups
ver7.2, 29jul2020 - move-in getHKExStocksPrice() with connectionError handlings
ver7.3 5aug2020 - fixed some realtime related trading functions' bugs.
ver7.4 10aug2020 - add dropNonHkdSec(), fixed a key bug in priceTrunc(), search 10aug2020 for details
                   stockVsOthersAdjPriceInc(), profitDf2IntCode(profitDf)
ver7.5 11aug2020 - Add S_FACTOR=2(lotsize Up). bugdet=0.108880*1e6. Add constants BUY_PRICE, SELL_PRICE, STOP_PRICE='maxDrawdownPrice'
ver7.6 16aug2020 - enabled IB's margin function and used it in the daytrade01 algo.
ver7.7 26aug2020 - use bTrades[s][dt.BLIMIT_BUY_IX].order instead of bOrders[s][dt.BLIMIT_BUY_IX] for cancelOrder()
                 - MDD changed from 20% to 8%
ver7.8 28aug2020 - add sleep(IB_DELAY) ,0.027s, to slow-down socket-send when cancel orders. Message to IB MUST < 50 msg/second
                    Fix, Warning: Approaching max rate of 50 messages per second (44). https://interactivebrokers.github.io/tws-api/order_limitations.html
ver7.9 30aug2020 - checkTestMaxRoi(). testMaxRoi <=0.0001
ver8.0 10sep2020 - add getDelayFrozenPrice(). MDD=12%
ver8.1 15sep2020 - add IBC’s StartGateway.bat, Stop.bat [auto login]
ver8.2 17sep2020 - add Class Gateway() [manual login], MDD=8%
ver8.3 21sep2020 - add investmentsNew in placeBracketOrders()
                    fix modified todayStocksDf in outer calling function
ver8.4 28sep2020 - strongBeep() added silent mode
ver8.5 5nov2020 - use urgent sell market order in unsoldOrdCancelNplaceMktOrd().
                  Do not cancel open orders in mSureNoStockHolded, just place additional mkt orders.
                      search '5nov2020' for chopped stock issue related changes.
                  EmailAdmin many times if connectIB failed, emailAdmin(f'Login IB..) 
ver8.5.1 8nov2020 - getCwdPath() support Ubunta/Linux if LINUX=True
ver8.5.2 19nov2020 - fix an fileOpen exception problem,19nov2020
ver8.5.3 27nov2020 - email Admin if cannot get new trading calendar when acrossing new year
ver8.6.1 30Nov2020 - allow some print_ _ TradeStatus() APIs print to logFileName instead of console screen
                    added CONSOLE_M to getDetaConfig() for controlling this prints
                    Fixed print to logfile closed after "with" block problem. 
ver8.6.2 2dec2020 - add back compensate, should be a bug. 2Dec2020
                    use back 'Normal' sell, search 2dec2020
ver8.6.3 3dec2020 - add SMALLEST_SEHK_ETF, SMALLEST_SEHK_STK for handling abnormal asset prices.
ver8.6.4 12dec2020 - compensate = 2*size CHANGED to compensate = size
ver8.7 18dec2020    - scaleUp=1 if test's ROI is -ve, 18dec2020
ver8.7.1 23dec2020 - use back 'Urgent' sell in closePositions() as chopped stock still happened in 1611
                    disabled Urgent Market Order: search 23dec2020 or "No need if unsold stock replaced" ...
ver8.7.2 25dec2020 - checkIsTradeDay() can cut half-day from valid trading days,25dec2020 
                    modified transactionFee(), add  commission mode, stock or warrant .
ver9.0 28dec2020 - add self._classfi() which classify input train dataset and output so-called
                    profitable "classfi-fulldayDS4Predict.csv" dataset
                    for new dataflow approach.
ver9.1 30dec2020 - added tf.config.list_physical_devices('GPU') to make sure models load into GPU
                     as new dataflow Classfi's inference is much slow due to big dataset
                   fix checkIsTradeDay() roll over bug when 30Dec2020 but until 2 days 1Jan2021
                     it alway find 2020 and cannot get 2021-Calendar_csv_e.csv
ver9.1.1 31dec2020 - Print clearly the dynamic thresholding value's used in classification:
                        print(f'Binary classification threshold-value used:{self.simThreshold}') # 31dec2020
                        NoDefault simThreshold in Class Dave, search 31dec2020, for the new dataflow method
ver9.1.2 6jan2021 - change boughtOnlyOcnL.append to boughtNoneOcnL.append
ver9.2 12jan2021  - able to support price predictor use RNN-LSTM deep model
ver9.2.1 13jan2021 - try "Ignore todayInvestLimt, 13jan2021, stop by IB margin limit instead".
                        same change in autoDayTrade01.py ver5.5.1.1. search 13jan2021
ver10.0 25jan2021  - terminate the program if cannot login IB successfully.  And send 3 warning emails.
                       connectIB() retry 1050 times, ~15min
ver10.1 6feb2021 - add   asset=STK_MODE option in decideBuyLotSize()
ver10.2 12feb2021 - add count=100 in loopOrdStatusUntil() and loopBracketOrdStatusUntil 
                    change timeLimit >= maxTry-1 to timeLimit >= maxTry 
ver11   13feb2021 - add some warrant trading APIs
                    add initChromeDriver() for Selenium
ver11.1 16feb2021   changed all .....TradesStatus() to ...TradesStatus(..logFileHandler, mode='BOTH')
ver 12 17feb2021 - add Class TrailOrder() and estPricesFrCommission()
                    change all contract.symbol to contract.localSymbol
ver12.1 22feb2021 - add chrome_options.add_experimental_option("prefs".. and with default paths
ver12.2 23feb2021 - deepCopy to avoid warning:   A value is trying to be set on a copy of a slice from a DataFrame.
                        Try using .loc[row_indexer,col_indexer] = value instead
                    in (stockVsOthersAdjPriceInc())
ver13.0 1mar2021  - add  stockToWarStk()
                        initChromeDriver() used ChromeDriverManager()
ver13.1 6mar2021 - rewrite estPricesFrCommission() and make it as perfect as possible.
ver13.2 8mar2021 - add stockVsOthersAdjPriceIncII()
ver13.3 12mar2021 - add base Class OcaSellBase which can change take/stop % and sell time.
ver14.0 26mar2021 - timeSellOrd() used GTC instead DAY.
ver15 25apr2021  - getYahooFinanceDataByCode()
                    Creat GLOBAL log file handler for usage of ALL functions the API
                    Search:  GLOBAL_logHandler
ver15.1 2aug2021 - add extra retry & timeout delays in httpDownloadNSaveExcel's timeout & maxTry
ver15.2 5sep2021 - fixed the problem of program stop when no any profitable stock is found,
                    if similarity is not fixed at 0.8 but big as 0.88/0.96 etc.
                    search texts 5sep2021 to see the corresponding changes
ver15.3 19oct2021   add getCwdPath() to all pd.read_excel() call in making sure look in current working dir
ver16   9dec2021  - fall back to stock only, +7,-7 => +3,-3 and HKD1M budget instead
ver16.1 13dec2021 - added dataFrIb2Csv(), by IB paid data services
ver16.2 14dec2021 - add getSymbol() and dataFrIB()
                    Globally use +7%,-7% and 0.12M HKD only. 
                    Need indiviudal minus 4% to get +/-3% (7-4)
ver17 21dec2021  -  Add ib2DetaFormat1D(), modified dataFrIb(.. ,startDay, stopDay,..)
ver17.1 21dec2021 - added 'if dt >= startDay:' to fix a bug.
                    changed from END_HR, END_MIN=16, 0  to     END_HR, END_MIN=16, 8
ver17.2 3jan2022 - used timeIndexSource = TIMEINDEX to replace the timeIndex.xlsx #3jan2022
                    creatQliTradeContracts() creat WAR contract by 6 parameters.
ver17.3 8jan2022 - Removed to used timeIndexSource = TIMEINDEX to replace the timeIndex.xlsx #6jan2022
ver17.4 8May2023 - special changes

"""
import tensorflow as tf
from tensorflow.python.client import device_lib #  get GPU model
import numpy as np; import pandas as pd; import yagmail #A6, email #import xlrd; 
import subprocess as spro
from multiprocessing import cpu_count # cpu & speed info
import matplotlib.pyplot as plt; import matplotlib as mpl #; import PySimpleGUI as sg
from sklearn.metrics import confusion_matrix; import os ;import seaborn as sns #; import math
from styleframe import StyleFrame #, Styler, utils   # for pd.ExcelWriter & style settings
from datetime import datetime, timedelta, timezone; import winsound; import yfinance as yf
import requests; import sys
import ib_insync as ibs # background ibs.util.startLoop() is handled by the calling Code instead here.

from selenium import webdriver   #從library中引入webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select; from selenium.common.exceptions import WebDriverException #8mar2021-Grace
from webdriver_manager.chrome import ChromeDriverManager #auto get rigt chrome driver
import time

from threading import Lock # multi-task Lock Class.
import uuid # gen unique ID from clk&MAC
from abc import ABC, abstractmethod #; from dataclasses import dataclass

EST, SUB_DATA=0,1 #estimate from commission, from subscribed data
WAR_CODE_NAME, UNDERLY_SYM, LAST_T_YDM, STRIKE, RIGHT, MULTIP=0,1,2,3,4,5 # warrant full definition
DEBUG_ATT=True #True # ATTached orders debug usages
            ### STP_LOSS_PERCENT '-' INTERNALLY !!! 15dec2021###
TAKE_PERCENT, STP_LOSS_PERCENT = +7, +7 #3,3 #9dec2021. Stop use '-' INTERNALLY. 7, 7 # xx %, 3,3 for test

# ===ENTRY, TAKE, STOP order index(0,1,2) MUST sync with limt's ...._IX order for sharing bracket order APIs====
# Indexs: ENTRY= buy order, TAKE= profit sell order, STOP= stop loss sell order
BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX=0, 1, 2 
ENTRY, TAKE, STOP= BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX
TIME_CONDI=STOP+1
REPLACE_byMKTSELL_HR=15 #9+dt.getDetaConfig()[7]//60 # 15:00, 3p. 0 is 9:30am
REPLACE_byMKTSELL_MIN=30
# =========================================================================================================

#CONSTANTS
# 1) General
LINEAR=0 # Normally MUST use this for PREDICT_MODEL
CNN1D=1; RNN=2 # for the new dataflow method ONLY in auto-ClassfiPredictParaTrainTest.py
PREDICT_MODEL=LINEAR # Will affect reshape of trainSet, 12jan2020
                 
SIM_FIX_08=False #True # fix parameter search similarity==0.8
SIM_THRE=0.8 # 0.8(GOOD) MUST >=0.7 no-matter 1_05p/11_59a. C4lassfi()'s recognition similary threshold as profitable. 13may2020

LINUX=False; CONSOLE_M=False # False => only print to logfile in .\prd-outputs, else to console screen.
ADM_EMAILS=['tograceli@hotmail.com']#, 'hoson@live.hk']
BUY=1; SELL=0; HOLD= -1
NOT_READY= -2  # system is not ready

# 2) Ref: timeIndex-6mar2020.xlsx in DeTa-wrtGrace\sourceCodes\WIP directory. Excel Dataframe related
PRICE_START = 0 
PRICE_11_59a= 149
PRICE_1_00p = 210
PRICE_1_01p = 211
PRICE_1_05p = 215  # IF USE as END-INDEX, user: _1_05p + 1
PRICE_1_15p = 225 
PRICE_3_00p = 330
PRICE_3_30p = 360
PRICE_4_00p = 390
PRICE_END   = 398 # LAST trade end at 4:00p=390 BUT reference price END UNTIL 4:08p=398. Refer to timeIndex.xlsx

TIMEINDEX=pd.date_range(start=pd.Timestamp('09:30:00'), end=pd.Timestamp('16:08:00'), freq='1T') #20dec2021
    ### Columns' Name Strings ###
LABEL_PRICE="Last Traded Price"
LABEL_VOL="Volume"
LABEL_MAX_PRICE="The Max Price"
LABEL_MAX_VOL="The Max Volume"
STOCK_CODEDATE="Stock Code&Date"
LOT_SIZE='買賣單位' # no. of share per lot for a stock. e.g. 1 hand lot size 300 shares
COM_NAME='公司' # company name's column string
C_SEHK='分類' # col for different of asset, stock-et-reit
C_STOCK='股本' #C_STOCK/C_ETF= 'STK' = Stock (or ETF). C_WAR= 'WAR' = Warrant. (from ib_synce sourceCode)
C_ETF='交易所買賣產品' #C_STOCK/C_ETF= 'STK' = Stock (or ETF). C_WAR= 'WAR' = Warrant. (from ib_synce sourceCode)
C_REIT='房地產投資信託基金'
C_WAR='衍生權證'  #衍生權證 #C_STOCK/C_ETF= 'STK' = Stock (or ETF). C_WAR= 'WAR' = Warrant. (from ib_synce sourceCode)
PREDICT_1ST="1stPredict Price" #first predicted price from Predict NN
PREDICT_2ND="2ndPredict Price" #second predicted price from Predict NN
SIM_MEASURE="Similarity Measure" # predict()'s probability as a similarity measures for prioritisation or etc..
BUY_PRICE='Sugggest Buy-Price'
SELL_PRICE='Suggest Sell-Price'
STOP_PRICE='maxDrawdownPrice' #stop loss selling price

PRICE_FILE_H = '' # Price file's heading
PRICE_FILE_T = '.xlsx' # Price file's tails
MAX_BACK_FILL_DATE =3 # !! small value for debug ONLY

# 4) Trading rules related
PROFIT_MARGIN=50 # HKD, $
MDD=0.08 # 20->8%->12%->8% 21sep2020, Max Drawn Down.
BUY_PERCENT=0.03 # 3% of predicted gap (3:00p-1:15p). Buy: price <= predict1:15p + 3%
SELL_PERCENT=0.03 # Sell: price > predict300p - 3%
SORT_KEY='amTradingAmount' # key to sort the price-vol dataframe/table
SORT_KEY_WAR='成交額 (千元)' # col name for warrant
BROKER_BEQ=1; BROKER_CCASS_BEQ=2 # Default is 1 =calculate BreakEven Qty by broker comission ONLY. 2=by broker & CCASS
STAMP_DUTY=0.001; STAMP_DUTY_WAR=0.0 # zero for warrant
SFC_CHARGE=0.000027
HKSE_CHARGE=0.00005
HKSE_SYS_CHARGE=0.5
CCASS_COMIT=0.00002 # HKSEx ccass commission. https://www.interactivebrokers.com/en/index.php?f=1315
CCASS_MIN=2; CCASS_MAX=100
BROKER_COMIT=0.0008  # IB broker commission 0.08%, https://www.interactivebrokers.com.hk/en/index.php?f=1590&p=stocks1
BROKER_MIN=18; BROKER_MIN_WAR=10 # min-COMIT, only HKD10 for warrant but HKD18 for stock
ASSET_MIN_COM={'STK':BROKER_MIN, 'WAR':BROKER_MIN_WAR} #'STK' = Stock (or ETF), 'WAR' = Warrant (ib_synce sourceCode)
STK_MODE=0; WAR_MODE=1 # Modes for comission calculation, 25dec2020
SMALLEST_SEHK_STK=0.001 # smallest ticker size
SMALLEST_SEHK_ETF=0.001 # smallest ticker size

S_FACTOR=2 # for lotsize scale-up factor, budget 120,000 12jan2021
DA_EXCEED_AMT=0.2* 1e6  # 1e6=$1M, 0.2*1e6 in semiAuto but 0.48*1e6 in autoByDayTrade01.py, 27jul2020
BUDGET_SET=0.12*1e6 #Ref:0.1*1e6=100,000. HKD currency. 0.088* 1e6 #0.088/0.1, 
### IB real-time trading related
LIVE, FROZEN, DELAYED, DELAYED_FROZEN=1, 2, 3, 4 #IB's market data type, https://interactivebrokers.github.io/tws-api/market_data_type.html
mDtypeStack=[LIVE] #stack default is live. use append push on stack. https://www.educative.io/edpresso/how-to-implement-stack-in-python
LK_UP = {BLIMIT_BUY_IX: 'Lmt Buy', BLIMIT_SELL_IX: 'Lmt Sell', BSTOP_SELL_IX: 'Stp Sell'}

IB_DELAY=0.026   # +10%=>0.0275, 4%=>0.026 second delay. Max 50msg/s =0.025s at least
AUTO_BY_IBC=False   # auto start gateWay by IBC. False must manual start IB's Gateway once per week
EC2=True # disable strongBeep or else that EC2 can't do.

# 5) Classifier, Dave, Imageify related
COL=2 #2 is from (price,volume)-tuple
CONST_PAD_SIZE=2 #2 MUST!, NOT 1,11FEB2020. 2=2-columns, EACH side.
BEFORE_C=0; AFTER_C=0 # The constants PAD before and after the four edges. 0=zero padding, CC =>[00-top, 0CC0, 00-bottom]. 0.0.5,1 same effects
TOTALCOL=CONST_PAD_SIZE+ COL +CONST_PAD_SIZE
CHANNEL=1 # simulate a gray image therefore have channel=1 of RGB
PROFITABLE=1; NON_PROFITABLE=0

def getDetaConfig():
    """
      Parameters: None
      Returns: Shared GLOBAL configuration parameters --
          0) Market trading time start. e.g 9:30a, sliceTimeStart
          1) Morning cut-off time for training. e.g. 11:59a/1:15p, sliceTimeEnd
          2) First afternoon reference point of time. 1st time-point.  e.g Time to buy, predict1stTime
          3) Second afternoon reference point of time. 2nd time-point. e.g predict2ndTime
          4) Profit margin for defining a profitable stock. e.g. HKD50, profitMargin
          5) bfill's number of back days. e.g 3, , nbBfill
          6) MDD, Max Drawn Down, price is added. StopLossSell price
          7) Time index to cancel&replace all Bracket order as Market Sell order
          8) Smaller than DA_EXCEED_AMT in morning trading, will be removed for the picked stock list,
              1e6=$1M, 0.2*1e6 in semiAuto but 0.48*1e6 in Auto. 27jul2020
          9) BUDGET_SET is upperLimit of budget spending for  buying stocks.
          10) S_FACTOR, scaleUp factor for lotSize
          11) Print CONSOLE_M mode if True, else to log file.
          12) SIM_THRE is similarity measure use in Classfi()
          13) TAKE_PERCEN is the percent to take profit pair with 14) for stop loss.
          14) STP_LOSS_PERCENT is stopLoss orders, trail/stop/oca etc. Pair with 13) for take profit
        Example: sliceTimeStart=getDetaConfig()[0], sliceTimeEnd=getDetaConfig()[1] is PRICE_11_59a+1
    """
    return [ PRICE_START, PRICE_11_59a+1, PRICE_1_00p, PRICE_3_00p, PROFIT_MARGIN, #getDetaConfig()[0-4]
             MAX_BACK_FILL_DATE, MDD, PRICE_3_30p, DA_EXCEED_AMT, BUDGET_SET, #getDetaConfig()[5-9]
             S_FACTOR, CONSOLE_M, SIM_THRE, TAKE_PERCENT, STP_LOSS_PERCENT #getDetaConfig()[10-14]
           ]


def stockToWarStkII(todayPickDf):
    """
        From todayPickDf to generate corresponding warrants(no yet tentatively)

    Chrome Driver update to match system chrom browser is handled automatically.
    Parameters
    ----------
    todayPickDf : dataframe after dropped RMB&USD and value <HKD1.0 assets
    warrantListAll : dataframe downloaded from http://......
    Returns
    -------
        Modified cols:
                todayPickDf['Name']
                todayPickDf['Code']
                todayPickDf['分類']
                todayPickDf['買賣單位']
        Added cols:
                todayPickDf['購/沽']
                todayPickDf['實際槓桿']
                todayPickDf['價內/價外 (%)']
                todayPickDf['到期日 (年-月-日)']
                todayPickDf['行使價']
                todayPickDf['街貨量 (%)']
                todayPickDf['成交額 (千元)']
               
    '[]' empty-array if unable to generate warrants or the success dataframe
    '[]' with Type Error/Value Error due to todayPickDf =Dataframe with wrong index 
    '[]' with WebDriverException due to internet disconnection leading to selenium chrome browser stopped
    '[]' with FileNotFoundError due to sudden disconnect internet when selenium download warrant list
    Assert Error will lead to programme stopped
    """
    # download warrant List from 法興 webiste
    # return the warrantListAll Dataframe
    def downloadWarrantList(): # by-hoson, 12feb2021
        """ Use Selenium to control Chrome to download warrant info from 15 Issuers from 法興 webiste
        Use Selenium to capture warrant table of Selected Issuers:
        Action of Chrome Browser:
        1. Open Chrome Brower
        2. Go to website
        3. Change issuers of drop down list to Selected Issuers
        4. for each selected issuers, 
            -Download excel list
            -Open excel with pandas
            -Append the warrant list to consolidated warrant dataframe
            -Remove the file name 

        Remarks:
        -User time.sleep to act like human, 
        -Download file takes time, 
        -May have change open excel is do first than download and incur error

        Selected Issuers:
        SG-法興 / BI-中銀 / BP-法巴 / CS-瑞信 / CT-花旗 / EA-東亞 / GJ-國君 / GS-高盛/ HS-匯豐 / 
        HT-海通 / JP-摩通 / MB-麥銀 / MS-摩利 / UB-瑞銀 /VT-瑞通
        
        :param:  NONE
        :return: NONE , warrantListALL will be saved as excel in current directory
        """
        
        # #
        WARRANT_URL = "https://hk.warrants.com/tc/warrant/search"
        EXCEL_DOWNLOAD_NAME = 'warrant_search_result_xls.xlsx'
        issuerList=["SG","BI","BP","CS","CT","EA","GJ","GS","HS","HT","JP","MB","MS","UB","VT"]  #2aug2020
        warrantListAll = pd.DataFrame(columns=[])  # create empty dataframe
        
        # Select the Issuer Drop Box List Value, Click Download, return dataframe of downloaded excel
        def downloadBasedOnDropBoxValue(issuerValue): #, EXCEL_DOWNLOAD_NAME):
            s1=Select(driver.find_element_by_id('issuer'))  #Go to Drop Down List Value
            s1.select_by_value(issuerValue) # Choose "CS 瑞信 as Drop Down List Value     
            # delay the click actions to act like human
            np.random.seed(); delay=np.abs(np.random.normal(0.3, 0.13)) # mean=0.3, std=0.13
            time.sleep(delay)
            driver.find_element_by_class_name('export').click()
        
        driver=initChromeDriver()    
        driver.get(WARRANT_URL)
        for issuer in issuerList:
            # warrantList = downloadBasedOnDropBoxValue(issuer,EXCEL_DOWNLOAD_NAME)
            downloadBasedOnDropBoxValue(issuer) #, EXCEL_DOWNLOAD_NAME) # 4mar2021
            time.sleep(3.5) 
            warrantList=pd.read_excel(getCwdPath()+EXCEL_DOWNLOAD_NAME)
            warrantListAll = warrantListAll.append(warrantList)
            os.remove(EXCEL_DOWNLOAD_NAME) #delete the download file after append to dataframe, to avoid the same file name in folder  
        warrantListAll.to_excel("warrantListAll.xlsx") #2aug2020
        driver.quit() #exit the chrome browser

    def getHkexAssetList(): # download all HKEx stocks info and save into AllStockTable.xwlsx
        """Return a  dataframe with ALL HKEx products including stock, warrant, cow and bear, other derivatives products
        :param:  NONE
        :return: stockList1 Dataframe
        """    
        LOT_SIZE='買賣單位'     
        COM_NAME='公司'
        #### Download with retries and error checking/reporting by lower level http request instead by pandas directly.
        fileName=httpDownloadNSaveExcel('https://www.hkex.com.hk/chi/services/trading/securities/securitieslists/ListOfSecurities_c.xlsx')   
        # fileName='https://www.hkex.com.hk/chi/services/trading/securities/securitieslists/ListOfSecurities_c.xlsx'
 
        # Get Date
        stockList = pd.read_excel(getCwdPath()+fileName, index_col=0) #read SEHK's original raw list in current folder. New or maybe old
        date = stockList.index[0]
        date= date.replace("截 至 ","")  # get 截 至 27/06/2019'
        date= date.split("/")[2] + date.split("/")[1] + date.split("/")[0] # convert to 20190627
        
        # copy a new stockList and change the column name
        stockList1=stockList.copy()
        stockList1.columns = stockList1.iloc[1] # Change column name as second row
        stockList1= stockList1[2:] #ignore the first 2 rows

        # format data 
        stockList1.index = stockList1.index.astype(int)   # convert '00001' to integer 1
        stockList1[LOT_SIZE] = stockList1[LOT_SIZE].str.replace(',', '') # change 1,000 to "1000"
        stockList1[LOT_SIZE] = stockList1[LOT_SIZE].astype(int) # change "1000" to integer 1000
        
        stockList1.index.names = ['股票代號']
        stockList1.rename(columns = {'股份名稱':COM_NAME}, inplace = True)
        # stockList1.to_excel("AllStockTable.xlsx")
            
        return stockList1            
    
    def returnWarrantNumberCriteriaByStockCode(warrantListAll,stock):    
        """
        Parameters
        ----------
        warrantListAll : dataframw downloaded from https://hk.warrants.com/tc/warrant/search,  index should be the warrant code as pd.read(... index_col=2)
        stock: int stock code    
        Returns
        --------
        resultWarrantCode : return int warrant code of that stock,  or 0 if no suitable warrant for stock
        """
        stockCodeColName="正股編號"
        notApplicableName="不適用"
        # warrantCodeColName="編號"
        descendingColName="成交額 (千元)"
        warrantCodes=[] 
        if int(stock) in list(warrantListAll[stockCodeColName]): #22feb2021 - change to int(stock)
            warrantListAll = warrantListAll[warrantListAll[stockCodeColName]==int(stock)] #22feb2021- change to int(stock), filter warrant related to specific stock #9aug2020
            warrantListAll = warrantListAll[warrantListAll[descendingColName]!=notApplicableName] #remove the unecessary
            warrantListAll = warrantListAll.sort_values(by=[descendingColName],ascending=False)  #sort the highest leverage
            warrantCodes = list(warrantListAll.index)
            # if len(warrantCodes) >0: #if a list of warrant codeds w.r.t stock code is not empty
            resultWarrantCode = int(warrantCodes[0])  #22feb2021 - pick the top one with the highest trading amount
        else:
            resultWarrantCode = 0 #22feb2021- no suitable warrant code for that particular stock
        return resultWarrantCode 
    
    assert isinstance(todayPickDf,pd.DataFrame), "The input variable todayPickDf is not dataframe."
    if len(todayPickDf)> 0: #8mar2021-grace
        try:
            codeIntList=profitDf2IntCode(todayPickDf) #28feb2021, by-hoson #8mar2021-grace
            todayPickDf['Code']=codeIntList #28feb2021, by-hoson #8mar2021-grace
            
            warrantCodeDateList=[] #29july2020 for retrieve consolidated 
            warrantCodeList=[]
            todayPickDf["originalCode"]=todayPickDf.index #29july2020 - save the original stock code for reference
            downloadWarrantList() #13feb2021- download warrant list from 法興website
            warrantListAll = pd.read_excel(getCwdPath()+"warrantListAll.xlsx",index_col=2) #13feb2021 - index_col =2 to make sure the index is warrant code
        
            allHKExStocks= getHkexAssetList() #by Hoson, 15feb2021
            stocksLotSize = allHKExStocks.iloc[:,0:4] #15feb2021 
            
            for codeDate in todayPickDf.index:
                stockCode = codeDate.split("_")[0]
                resultWarrantCode = returnWarrantNumberCriteriaByStockCode(warrantListAll,stockCode)
                if (resultWarrantCode != 0) :  #29july2020 , 0 means cannot find sutiable warrantCode due to file not exist or file exist BUT empty file(no trading record) #15dec2020, if result warrant code both in warrantList and Allstocktable, otherwise, not replace.
                    newCode = str(resultWarrantCode) + "_" + codeDate.split("_")[1] #29july2020
                    todayPickDf = todayPickDf.rename(index={codeDate:newCode })     #29july2020   
                    warrantCodeDateList.append(newCode) #save the list of e.g ["12543_2020812","23245_2020812","14566_2020812"]
                    warrantCodeList.append(resultWarrantCode) #save the list of warrant codes e.g [12543,23245,14566]
                    
            if warrantCodeList: # if the list is not empty then do the follow #30july2020
                todayPickDf.loc[warrantCodeDateList,'Name'] =list(warrantListAll.loc[warrantCodeList,'名稱'])
                todayPickDf.loc[warrantCodeDateList,'分類'] = "衍生權證"
                todayPickDf.loc[warrantCodeDateList,'買賣單位']=[stocksLotSize.loc[code,'買賣單位'] if code in stocksLotSize.index else 0 for code in warrantCodeList]  #0 means the warrantcode cannot be found in current allstocktable(maybe delisted). 
                todayPickDf.loc[warrantCodeDateList,'購/沽']=list(warrantListAll.loc[warrantCodeList,'購/沽'])
                todayPickDf.loc[warrantCodeDateList,'實際槓桿']=list(warrantListAll.loc[warrantCodeList,'實際槓桿'])
                todayPickDf.loc[warrantCodeDateList,'價內/價外 (%)']=list(warrantListAll.loc[warrantCodeList,'價內/價外 (%)'])
                todayPickDf.loc[warrantCodeDateList,'到期日 (年-月-日)']=list(warrantListAll.loc[warrantCodeList,'到期日 (年-月-日)'])
                todayPickDf.loc[warrantCodeDateList,'行使價']=list(warrantListAll.loc[warrantCodeList,'行使價'])
                todayPickDf.loc[warrantCodeDateList,'街貨量 (%)']=list(warrantListAll.loc[warrantCodeList,'街貨量 (%)'])
                todayPickDf.loc[warrantCodeDateList,'成交額 (千元)']=list(warrantListAll.loc[warrantCodeList,'成交額 (千元)'])
               
                todayPickDf=todayPickDf[['Code','Name', C_SEHK, '買賣單位', '購/沽',
                                         '實際槓桿','價內/價外 (%)', '到期日 (年-月-日)', '行使價',
                                         '街貨量 (%)', '成交額 (千元)'
                                         ]].copy(deep=True)
        
        except (TypeError, ValueError): #8mar2021-grace
            print("TypeError/ValueError: todayPickDf index may have wrong type or wrong format. ")  #8mar2021-grace
            todayPickDf=[]
        
        except WebDriverException: #8mar2021-grace
            print("WebDriverException: Maybe network problem or cannot open selenium chrome browser. ")  #8mar2021-grace
            todayPickDf=[]
            
        except FileNotFoundError: #8mar2021-grace
            print("FileNotFoundError: Cannot find the warrant_search_result_xls.xlsx for read into dataframe.Maybe due to sudden network disconnect to disable chrome driver to proceed")  #8mar2021-grace
            todayPickDf=[]
    else: 
        todayPickDf=[] #set to an empty list #8mar2021-grace

#### replace stock code by warrant code.
    if len(todayPickDf) > 0: 
        codeIntList=profitDf2IntCode(todayPickDf) #18mar2021, by-hoson
        todayPickDf['Code']=codeIntList #28feb2021, by-hoson
    else: todayStockDf=[] #set to an empty list        
    
    return todayPickDf # 13feb2021 - modified todayPickDf with warrant codes


def warNonWarContracts(todayPickDf, ses, exchange: str='SEHK', currency: str='HKD'):  #The input Df MUST has the column C_SEHK (分類), SELL/STOP/BUY_PRICE
    """
    Create and qualify contracts for trading. Support STK, WAR, ETF, REIT.
    Parameters
    ----------
    todayPickDf : Dataframe of the assets
    ses : IB session handler

    Returns
    -------
    List of qualified contracts
    
    """
    symbols=list(map(str, todayPickDf['Code'].to_list()))  # convert trading symbol-code to strings, e.g.'1', '1282'
    secTypes=list(map(str, todayPickDf[C_SEHK].to_list()))
    
    contracts=[]
    for sym, sec in zip(symbols, secTypes):
        if sec==C_WAR:
            c=ibs.Warrant(localSymbol=sym, exchange=exchange, currency=currency)
            ses.qualifyContracts(c)  # qualifyContracts() Create conId. check & auto fill-in missing datas etc..
            contracts.append(c)
        elif sec in (C_STOCK, C_ETF, C_REIT):
            c=ibs.Stock(sym, exchange, currency)
            ses.qualifyContracts(c)
            contracts.append(c)
        else: sys.exit('Not support this security type yet !!!')
        
    return contracts

def getTodayAlgoSellTime():
    now=datetime.now() #; print("Now is:", now.strftime('%Y-%b-%d %H:%M'), "(HK Time only!)") #A12,get&print current time
    timeCancelNplaceOrds=now.replace(hour=REPLACE_byMKTSELL_HR,
                                      minute=REPLACE_byMKTSELL_MIN,
                                      second=0, microsecond=0) #A4, replace to target runtime
    # tUTC=timeCancelNplaceOrds.astimezone(timezone.utc).strftime("%Y%m%d %H:%M:%S")
    tLocal=timeCancelNplaceOrds.strftime("%Y%m%d %H:%M:%S")

    return tLocal

class TrailOrder(ibs.Order):
    def __init__(self, action, totalQuantity, trailingPercent, orderId, **kwargs): #auxPrice=absolute trail amount
        ibs.Order.__init__(
            self, orderType='TRAIL', action=action,
            totalQuantity=totalQuantity, trailingPercent=trailingPercent, orderId=orderId, **kwargs)

class OcaSellBase(ABC):
    """
    Abstract class as parent for any future market-attach-OCA order placing mechansim.
    http://masnun.rocks/2017/04/15/interfaces-in-python-protocols-and-abcs/. 
    https://www.geeksforgeeks.org/abstract-classes-in-python/
    Usage:
        class  NewClass(OcaSellBase):
            ......; ....
            def _takeProfitOrd(self, totalShares, takeProfit, orderId):
                ... actual method implement for the Abstract base class ...; ....
            
            def _stopLossOrd(self, totalShares, stopPrice, orderId):
                ... actual method implement for the Abstract base class ...; ....
  
            def _timeSellOrd(self, totalShares, sellTime, orderId):
                ... actual method implement for the Abstract base class ...; ....       
                
    Usage:
        for i in [1,2,3]: #index of assets to be bought
            coRoutineInstance=dt.NewClass(ses, contracts[i], monitor='Filled',
                                takePercent=7, stopPercent=7, # +/-7%
                                sellTime='15:30' # hh:mm of e.g. '20210303 15:30', local time must
                                )
            mktTrade=ses.placeOrder(contracts[i], mOrders[i])
            mktTrade.filledEvent+= coRoutineInstance.fireAttachSells
                
    Ref above 'self' keyword: A reference to the current instance of the class, used to access VARIABLE that belongs to the class.
        https://www.w3schools.com/python/gloss_python_self.asp#:~:text=The%20self%20parameter%20is%20a,that%20belongs%20to%20the%20class.
    """
### THINK DOUBLE before making any changes here, very sensitive GLOBAL class variables to work in the event handler!!
    name='AttClasses' # attach 3 sell orders class
    counts=0 # 0= One instance created. Class variable, same for all instances gen fr the Class    
    GLOBAL_records=[] # original-entry, take, stop-loss. 
    LOCK=Lock() # creat lock instance from threading module. Lock() is init as unlocked by Python. https://docs.python.org/3/library/threading.html#lock-objects
### THINK DOUBLE before making any changes here, very sensitive GLOBAL class variables to work in the event handler!!
    def __init__(self, ses, contract, monitor:str ='Filled',  #common Concrete method, https://stackoverflow.com/questions/56960959/what-is-the-purpose-of-concrete-methods-in-abstract-classes-in-python
                  refTrade=None,
                  takePercent=TAKE_PERCENT, stopPercent=STP_LOSS_PERCENT, # +/-7% for PRICES calculations
                  sellTime='15:30', # hh:mm of e.g. '20210303 15:30', local time must
                  ):
        OcaSellBase.counts +=1  #can't use self.counts, debug 11mar2021. #inc for next instance. _init_ is sequential and reEntrance
        self.ses=ses
        self.monitor=monitor
        self.refTrade=refTrade # entryTrade(s)-info. If necessary, for bracketOrders or list of order instance internal access.
        self.rawContract=contract # Raw qualified contract  
        self.id=OcaSellBase.counts #can't use self.counts, debug 11mar2021. # id no. ready for new instance use, 
        self.takePercent=takePercent; self.stopPercent=stopPercent
        self.sellTime=sellTime #local time to sell all positions

        super().__init__() #call parent ABC's _init_(), https://www.python-course.eu/python3_abstract_classes.php

    def __str__ (self):
        return f"Instance:{self.id}, Monitor:{self.monitor}." #print(theClass) to show this signature
    
    @abstractmethod #https://towardsdatascience.com/abstract-base-classes-in-python-fundamentals-for-data-scientists-3c164803224b
    def _takeProfitOrd(self, totalShares, takeProfit, orderId): #Abstract method for child to define
        raise NotImplementedError('TakeProfit fn did not overwrite correctly.')
    
    @abstractmethod
    def _stopLossOrd(self, totalShares, stopPrice, orderId): #Abstract method for child to define
        raise NotImplementedError('stopLoss fn did not overwrite correctly.')
    
    @abstractmethod    
    def _timeSellOrd(self, totalShares, sellTime, orderId): #Abstract method for child to define
        raise NotImplementedError('timeSell fn did not overwrite correctly.')
     
    @staticmethod
    def _resetStates(counts=0, recList=[]):
        OcaSellBase.counts=counts # 0= One instance created. Class variable, same for all instances gen fr the Class    
        OcaSellBase.GLOBAL_records=recList        

    # @abstractmethod, CAN'T do this, debug 10mar2021
    def _fireAttachSells(self, entryTrade): #common Concrete method, https://stackoverflow.com/questions/56960959/what-is-the-purpose-of-concrete-methods-in-abstract-classes-in-python
        """
        Monitor entry trade orderStatus and attach orders in an OCA group. *OCA can't support all IB Algo orders.'
        The entry Trade can be mkt trade, refTrade[BLIMIT_BUY_IX] of the three limit trades-orders etc.

        Parameters
        ----------
        entryTrade : A trade

        Returns
        -------
        None BUT modified the Class's  GLOBAL_records=[] and counts

        """
        if entryTrade.orderStatus.status == self.monitor:
            if DEBUG_ATT: 
                print(f'EnrtyTrade- conId:{entryTrade.contract.conId}, priExchange:{entryTrade.contract.primaryExchange}')
                print(f'Saved- conId:{self.rawContract.conId}, priExchange:{self.rawContract.primaryExchange}')

            totalShares=0; totalInvestment=0
            for fill in entryTrade.fills:
                totalShares +=fill.execution.shares
                totalInvestment +=fill.execution.shares*fill.execution.price

            myAvgPrice=round(totalInvestment/totalShares, 4)
            if DEBUG_ATT: print(f'{fill.execution.side} {fill.contract.localSymbol} {totalShares} shares@MyAvg-Price:{myAvgPrice} by {len(entryTrade.fills)} fills.')  
            stpLoss= sehkTickRoundPrice(myAvgPrice*(1- self.stopPercent/100), 'SELL') #can't for ETF
            takeProfit= sehkTickRoundPrice(myAvgPrice*(1+ self.takePercent/100), 'SELL') # BUY will make price higher than 'SELL' little-bit 16feb2021. for STK- REIT- warrant ONLY!
            # stpLoss= sehkTickRoundPrice(myAvgPrice*(1- STP_LOSS_PERCENT/100), 'SELL') #can't for ETF
            # takeProfit= sehkTickRoundPrice(myAvgPrice*(1+ TAKE_PERCENT/100), 'SELL') # BUY will make price higher than 'SELL' little-bit 16feb2021. for STK- REIT- warrant ONLY!
            stpLoss= incDecSehk(stpLoss, 'DEC', 1) #decrement, make sure lower. STK- REIT- warrant ONLY, ..SehkETF() instead.
            takeProfit= incDecSehk(takeProfit, 'INC', 3) #3 increments, make sure higher even small price value        

            ##### Prepare sell orders       
            takeOrd=self._takeProfitOrd(totalShares, takeProfit, orderId=self.ses.client.getReqId())
            stpLossOrd=self._stopLossOrd(totalShares, stpLoss, orderId=self.ses.client.getReqId())
            conditionOrd=self._timeSellOrd(totalShares, self.sellTime, orderId=self.ses.client.getReqId())

            OCAid=str(uuid.uuid1()) #must use long-enough random string
            ordersForAtt=self.ses.oneCancelsAll([takeOrd, stpLossOrd, conditionOrd], OCAid, ocaType=1) # str must unique for each-group. 1=Cancel all remaining orders with block
            # if DEBUG_ATT: print(f'Take, StpLoss prices:{takeProfit}, {stpLoss}.') # 1.7e+308 is sysDefaultValue')
  
            tradesGroup=[self.refTrade] # trade set by external function, e.g. placed Mkt/Bracket trade/listOftrades
            while OcaSellBase.LOCK.locked(): # wait until lock released.
                print(f'Waiting in instance:{self.id}, for unlocking...') # keep looping if locked.

            # Execute when the lock released
            with OcaSellBase.LOCK: # LOCK.acquire(), then LOCK.release() from the 'WITH' block
# ==============# auto-locked by LOCK.acquire() before access, make sure NO two API use same time.                
                for order in ordersForAtt: # place sell orders
                    tradesGroup.append(self.ses.placeOrder(self.rawContract, order)) #; ibs.IB.sleep(IB_DELAY)

                OcaSellBase.GLOBAL_records.append(tradesGroup) #debug must 0,1 direct. 1mar2021
# =============# auto-unlocked by LOCK.release() before leave
            ibs.IB.sleep(IB_DELAY*len(tradesGroup)) #when many instances to avoid > 50msg/second, outside 'with' to min lock duration         
            if DEBUG_ATT: print(f'Exist attach-orders routine of instance:{self.id}. TakeProfit@ {takeProfit}, StopLoss@ {stpLoss}.')
        

class  OcaSell_10a(OcaSellBase): #1=LMT, 0=stp, a=time condition
    """ 
        Naming convention:
        OcaSell_(S0 S1 S2), position 0 indicates for takeProfit, 1 for stopLoss, 2 for timeEnd Sell Orders. Values 0-9a-z
        e.g. OcaSell_10a is takeProfit Limit order sell, stopLoss Stop order sell and Time Order sell
        
        0   : Stop Order type.  e.g. ibs.StopOrder(...), ib_synce default
        1   : Limit Order type.      ibs.LimitOrder(...)
        2   : Trailing Stop Order Type. e.g dt.TrailOrder(...), CUSTOM made by detalibs.py
        3   : Trailing Stop Limit Order. TBD
        4   : Stop Limit Order.      ibs.StopLimitOrder
        5-9 : reserved for future usages
        
        a - Time condition Market Order type (OCA can't support IB Algo orders, e.g VWAP. mar2021 confirm by IB)
        b - Time condition Sweep-to-Fill Order type

    Implement:
            takeProfit & stopLoss methods
            timeConditional sell by sell at hh:mm:ss 24hr-format
            
    Usage:
        for i in [1,2,3]: #index of assets to be bought
            coRoutineInstance=dt.OcaSell_10a(ses, contracts[i], monitor='Filled',
                                takePercent=7, stopPercent=7, # +/-7%
                                sellTime='15:30' # hh:mm of e.g. '20210303 15:30', local time must
                                )
            mktTrade=ses.placeOrder(contracts[i], mOrders[i])
            mktTrade.filledEvent+= coRoutineInstance.fireAttachSells
    """
    # super().__init__() #default will call it base class _init_
    def _takeProfitOrd(self, totalShares, takeProfit, orderId): #overwrite parent abstract method
        # takeOrd=ibs.StopOrder(action='SELL', totalQuantity=totalShares, stopPrice=takeProfit, orderId=orderId )# in client.py, transmit=?? MUST by OCA 
        takeOrd=ibs.LimitOrder(action='SELL', totalQuantity=totalShares, lmtPrice=takeProfit, orderId=orderId )# in client.py, transmit=?? MUST by OCA
        return takeOrd
    
    def _stopLossOrd(self, totalShares, stopPrice, orderId): #overwrite parent abstract method
    # dt.TrailOrder or etc..
        stpLossOrd=ibs.StopOrder(action='SELL', totalQuantity=totalShares, stopPrice=stopPrice, orderId=orderId)
        return stpLossOrd
    
    def _timeSellOrd(self, totalShares, sellTime, orderId): #overwrite parent abstract method
        now=datetime.now(); hour=int(sellTime.split(':')[0]); minute=int(sellTime.split(':')[1]) #; second=minute=sellTime.split(':')[2]
        tLocal=now.replace(hour=hour, minute=minute, second=0, microsecond=0) #A4, replace to target runtime
        tLocal=tLocal.strftime("%Y%m%d %H:%M:%S") #e.g'20210303 15:30', local-time, IB confirmed 5mar2021
        conditionOrd=ibs.MarketOrder(action='SELL', totalQuantity=totalShares, #OCA can't support algoStrategy/Params, 3mar2021
                                         orderId=orderId, #conId=entryTrade.contract.conId, #contract ID, NO need for price condition
                                         tif="GTC") #or GTC/DAY, Good-Til-Canceled. No 'Adaptive' only support DAY!,31jul2020# in client.py, transmit=?? MUST by OCA
        conditionOrd.conditions = [ibs.TimeCondition(conjunction='o', # Or(o),  default AND (a)
                                                         isMore=True,  #greater. # conId=entryTrade.contract.conId, #No here
                                                         time=tLocal)] #time='20210303 22:15:00' #LOCALtime, default AND. Ewald, https://groups.io/g/insync/topic/16426818?p=Created,,,20,2,0,0 

        return conditionOrd

    @staticmethod #https://docs.python.org/3/library/functions.html#staticmethod
    def resetStates(counts=0, recList=[]):
        OcaSellBase._resetStates(counts=0, recList=[]) #super._ can't, must for instance instead static classMethod.

    def fireAttachSells(self, entryTrade): # _call()_ do'nt work here
        super()._fireAttachSells(entryTrade) #call the tentative implemented abstract method in parent class. Can extend in future.


def getRealPrices(contracts, ses):
    print('Mode=Get price from paid IB data service.')
    
    # mktDataType=mDtypeStack[-1] #get current top of the stack, use append push on stack. https://www.educative.io/edpresso/how-to-implement-stack-in-python
    ses.reqMarketDataType(FROZEN) #Frozen snapshot price.
    symbols=[]; prices=[]; tickers=[]; commiS=[]#commisions
    for c in contracts: # estimate market price from commission
        symbols.append(c.localSymbol)
        commiS.append(10000) # DUMMY, 10000 means not estimated from comission 
        tickers.append(ses.reqMktData(c) ); ibs.IB.sleep(IB_DELAY) #need total delay > IB_DELAY, refer to retTickerPrice() for details
        
    for ticker in tickers: #delayed above, no need to wait further for data arrival here.
        prices.append(retTickerPrice(ticker) ) #retTickerPrice will MAKE sure price available by retries.
        # prices.append(ticker.marketPrice() )
    
    ibs.IB.sleep(IB_DELAY) #ensure the last ticker has total delay more than 2*IB_DELAY
    # ses.reqMarketDataType(mktDataType) #reset to default market data type mode (live).
    return pd.DataFrame(list(zip(symbols, prices, commiS)), columns =['symbols', 'estPrices', 'commiS']) # all None will become Nan after return, check by df.isnull()

        ###### IB Data Service Related APIs, 5jan2022 ################
def reqAllMktData(contracts, ses, mode=FROZEN):
    print('Will get price from paid IB data service.')
    ses.reqMarketDataType(mode) #Frozen snapshot price.
    symbols=[]; tickers=[]
    for c in contracts:
        symbols.append(c.localSymbol)
        tickers.append(ses.reqMktData(c) ); ibs.IB.sleep(IB_DELAY) #avoid >50msg per second.

    ibs.IB.sleep(IB_DELAY*2) #add extra delay for last ticker data arrival, need >1.99 if it is WAR as worst case, 20dec2021.
    return symbols, tickers
##BUG in .reqTickers(), 6jan2022
# def reqAllMktDataFrozen(contracts, ses): #Ref: https://github.com/erdewit/ib_insync/blob/master/examples/qt_ticker_table.py
#     ses.reqMarketDataType(FROZEN) #Frozen snapshot price.
#     tickers=ses.reqTickers(contracts, regulatorySnapshot=False) #BUG6jan2022. Return a list of snapshot tickers until all ready. Blocking API
#         #get symbols when the ticker is already filled.
#     localSymbols=[t.contract.localSymbol for t in tickers] #e.g/ .contract.secType/currency/symbol
#     return localSymbols, tickers

def retTickerPrice(ticker):
    """
    Make sure not Nan before return the price

    Parameters
    ----------
    ticker : stock ticker

    Returns: curren realtime price

    """
    DEBUG=True

    i=0; 
    while i<1000:
        price=ticker.marketPrice() #may consider use pendingTickersEvent(), 5jan2021
        if np.isnan(price): #check price is NOT Nan. MAKE sure price available by retries
            if i%10==0: print(f'Invalid Price={ticker.marketPrice()} during loop:{i}')
            # ibs.IB.sleep(IB_DELAY); i+=1
            ibs.IB.sleep(IB_DELAY/5); i+=1
        else: # got a valid price, NOT Nan
            if DEBUG: print(f'Got the price at loop {i}.')
            break
        # print(f'Cannot get the price after {i} trys !!!')
    
    return price

def reqAllPrices(tickers):
    """
    Delay BEFORE call this API is NECESSARY. Otherwise many tickers will return Nan without price Information.
        OTHERWISE need to use async-wait, example
            async for t in ticker.updateEvent:
                if t.hasBidAsk():
                    print(t.bid, t.ask)

    Parameters
    ----------
    tickers : IB ticker class

    Returns
    -------
    prices : float

    """
    prices=[]
    for ticker in tickers: #delayed BEFORE call this API, no need to wait further for data arrival here.
        prices.append(retTickerPrice(ticker) ) #retTickerPrice will MAKE sure price available by retries.

    return prices

def cancelAllMktData(contracts, ses):
    for c in contracts: # cancel all background monitoring.
        ses.cancelMktData(c); ibs.IB.sleep(IB_DELAY)
        
def oldFormatPrices(symbols, prices):
    commiS= [10000 for s in symbols] #DUMMY commisions, , 10000 means not estimated from comission 
        
    return pd.DataFrame(list(zip(symbols, prices, commiS)), columns =['symbols', 'estPrices', 'commiS'])
        ###### IB Data Service Related APIs ################

def estPricesFrCommission(contracts, oneLotQtys, ses, mode=EST): #, secType='WAR'):
    """   
    CAUTION: Quantities MUST big enough to AVOID using minimun commission, 
        otherwise estimation will be WRONG and exception will be raised to stop the programe!
        A search method is used to address this potential risk with an assumed UPPER bounds.

    Estimate price for Stock STK, ETF, and Warrant WAR from reported commission.
    Parameters
    ----------
    contracts : list of contracts
    oneLotQtys : array list of exchange's "lot-size" for diff assets/stocks etc..
                    oneLotQtys MUST np.ndarray (isinstance(x, np.ndarray)=True) instead of simple list. https://numpy.org/doc/stable/reference/generated/numpy.multiply.html

    ses : IB connection session handler
    mode: EST=estimate price by commission, SUB_DATA=direct get price from IB paid data service.
    
    Raises: NotImplementedError: If unsupported exchange
    Returns:dataframe with columns ['symbols', 'estPrices', 'CommiS']
    """
    if mode==SUB_DATA: print('Mode=Get price from paid IB data service.')
    elif mode==EST: print('Mode=Estimate price from commission.')
    else: print('Invalid mode..')
    
    MAXTRY=50 #max trys if not commission info get
    assert isinstance(oneLotQtys, np.ndarray), 'Error, Input not numpy array!' # Check!
    exchange=contracts[0].exchange
    assert exchange == contracts[-1].exchange, 'Exchanges seem different, error.' # double check all exchanges MUST same.    
            #1k, 2k, 5k are common. Scale up ALL to ~120k
    quantities= np.where(oneLotQtys < 2001, oneLotQtys*60, oneLotQtys) #(condition, True, False). 1k=>30k only!
    quantities= np.where(quantities < 5001, quantities*36, quantities) #10001 too big, ScaleUP.https://numpy.org/doc/stable/reference/generated/numpy.where.html
    quantities= np.where(quantities < 10001, quantities*18, quantities) #reduce loop below as lot are 10,000 which gen minCom finally.
    # assert len(contracts)==len(quantities), 'Size misMatchs!' #safety inputs check only.
    rate = ( BROKER_COMIT if (exchange=='SEHK') else #same rate. doff min (stk, warrant, option etc..). https://www.interactivebrokers.com/en/index.php?f=1590&p=stocks1
              # 0.0005 if (exchange=='LSE') else #UK Approx ONLY!!, https://www.interactivebrokers.com/en/index.php?f=1590&p=stocks1
             None 
           )
    if rate is None: raise NotImplementedError(f'Not yet for {exchange}')
    upperBounds=  np.multiply(np.multiply(quantities, 10000.0), ASSET_MIN_COM['STK']) # xx.0 force to bound float, debug 6mar2021.
                                                                        # qty*10k*min.. .Assumed stock price < 9995(10000)
    
    mktOrders = [ ibs.MarketOrder(action='BUY', totalQuantity=quantity ) for quantity in quantities ] #creat orders for virtual checks
    symbols=[]; estPrices=[]; tickers=[]; commiS=[]#commisions
    for c, o, q, ub in zip(contracts, mktOrders, quantities, upperBounds): # estimate market price from commission
        symbols.append(c.localSymbol)
        minCom=ASSET_MIN_COM[c.secType]  #'STK' = Stock (or ETF), 'WAR' = Warrant (ib_synce sourceCode)
        i=0; threeTimes=False # init control variables

        if mode==EST: ##### estimation from commission #####
            while True:
                i +=1 # count trys and prevent potential dead looping
                if i>MAXTRY: # 200 is too big if many assets have same problem. 100 to MAKE it wait for price offering,23mae2021
                    print(f'Tried {i} times, unreasonable and stop.')
                    commiS.append(None); msg=f"Ignored SYM:{c.localSymbol} asset. No commission/price estimated!"
                    estPrices.append(None) # No commission => no estimate price
                    print(msg); emailAdmin(msg, ' From:'+sys.argv[0])             
                    break # IGNORED, tried too much
                    
                # Actual calculations start here
                result=ses.whatIfOrder(c, o) #estimate commission, margin etc...
                if not result: #debug 4mar2021. whatIf..() return result=[] nothing
                    msg=f"Warning! SYM:{c.localSymbol} asset did'nt response to commission query, retry!"
                    # commiS.append(None); estPrices.append(None) # No commission => no estimate price
                    if i%(MAXTRY/2)==0: print(msg); emailAdmin(msg, ' From:'+sys.argv[0])
                    continue #retry 
                elif ub > result.commission > minCom: ### Actual calculations ###
                    estPrices.append(result.commission/(q*rate) ) #formula
                    commiS.append(result.commission) # .commissionCurrency/ equityWithLoanAfter/Before /maintMarginAfter/Before
                    break # DONE, great !
                elif result.commission <= minCom:
                    q = q*3; threeTimes=True # x3 try again, increase qty
                    o=ibs.MarketOrder(action='BUY', totalQuantity=q )
                    continue #retry
                else: # the only case remind is overflow the bounds
                    if threeTimes is True: q = int(q/3)*2; threeTimes=False # revert to x2 try again
                    o=ibs.MarketOrder(action='BUY', totalQuantity=q )
                    msg=f"Warning! SYM:{c.localSymbol}-${result.commission} commission may overflow, retry."
                    if i%(MAXTRY/2)==0: print(msg); emailAdmin(msg, ' From:'+sys.argv[0]) #must lower than upper bounds reasonably
                continue #retry
                
        elif mode==SUB_DATA: ##### get from subscription paid data, 13dec2021 #####
            commiS.append(10000) # DUMMY, 10000 means not estimated from comission 
            tickers.append(ses.reqMktData(c) ); ibs.IB.sleep(IB_DELAY) #need total delay > IB_DELAY, refer to retTickerPrice() for details
        else: print('Invalid mode, done nothing......')
        
    if mode==SUB_DATA: #build the list of estPrices before return
        for ticker in tickers: #delayed above, no need to wait further for data arrival here.
            estPrices.append(ticker.marketPrice() )
        ibs.IB.sleep(IB_DELAY) #ensure the last ticker has total delay more than 2*IB_DELAY
 
    return pd.DataFrame(list(zip(symbols, estPrices, commiS)), columns =['symbols', 'estPrices', 'commiS']) # all None will become Nan after return, check by df.isnull()


def httpDownloadNSaveExcel(url: str): # download ur, return &save to filename
    maxTry=13 #7 #5 #try 5 times at most                    
    filename=url.split('/')[-1] #ListOfSecurities_c.xlsx, last element of the splited url list
    for attempts in range(1,maxTry+1): #try max+1 times
        try:
            print("Retrying to update with lastest",filename, attempts, end="Run. ")
            # htmlResult=requests.get(url, timeout=(2, 15), allow_redirects=True) #A14, Max wait 2s for connect, 15s for downloand
            htmlResult=requests.get(url, timeout=(5, 25), allow_redirects=True) #3aug2021. A14, Max wait 4s for connect, 25s for downloand
            with open(filename, 'wb') as r: 
                r.write(htmlResult.content) #write the target Excel in the specified filename
                r.close() # tidy-up,19nov2020
        except Exception as e:
            print(e, '. Retrying...'); ibs.IB.sleep(0.15) #sleep 0.15second before retry.
            continue # continue the loop to next attempt. https://www.programiz.com/python-programming/break-continue
        break # break the loop immediately.

    if attempts < maxTry:
        print("Download Success.")     
    else:
        print("!!!!!!!!! Update failed, use old version temporary!!!!!!!!!!!!!!")
        emailAdmin('Error in download '+filename+' use old version temporary!!', '  From:'+sys.argv[0])
    
    return filename

def ib2DetaFormat1D(symbol:str, df:pd.DataFrame, nowaday:str) -> pd.DataFrame: #now().strftime("%Y%m%d") # formate as 5_20211220 i.e stockcode_yyyymmdd
    """
    Convert from IB format to Deta normalised price-volumn format

    Parameters
    ----------
    symbol: string, e.g. '5' for HSBC, '26377' for warrant of Ping-On
    df : pandas dataframe

    Returns: pandas dataframe

    """
    # df1=df.copy(deep=True)
    df=df.set_index("date")
    df.index = pd.to_datetime(df.index)
    timeIndexSource = pd.DataFrame(index=TIMEINDEX) # a blank dataframe with timeindex for merge

    
    ##merge with timeindex from 9:30 to 16:08
    pCol=pd.merge(timeIndexSource, df['close'], left_index=True, right_index=True, how='outer')
    vCol=pd.merge(timeIndexSource, df['volume'], left_index=True, right_index=True, how='outer')

    ##Fill the nan value by forward fill and backward fill
    pCol.fillna(method = 'ffill', inplace=True) #do forward fill first
    pCol.fillna(method = 'bfill', inplace=True) #if there is still nan after forward fill, then do backward fill
    if vCol.isna().values.any(): #20191219 detect if there are any nan values in any element
        vCol.fillna(0.0, inplace=True)   # fill all NaN by zeros, Hoson 11Dec
    
    ##Normalize the price and volume
    maxPrice= pCol.iloc[0:PRICE_11_59a+1].max()[0]  #only find the morninig max, store the max for each column
    maxVol = vCol.iloc[0:PRICE_11_59a+1].max()[0] # [0] mean get series first row value and become float
    pCol = pCol.div(maxPrice) #normalize Price
    if maxVol !=0:  vCol = vCol.div(maxVol) #normalize Volume
    
    ##Create Dave format Dataframe for a single stock
    temp=timeIndexSource.copy(deep=True)
    temp[LABEL_PRICE] = pCol
    temp[STOCK_CODEDATE] = symbol+'_'+ nowaday # formate as 5_20211220 i.e stockcode_yyyymmdd
    # temp[STOCK_CODEDATE] = symbol+'_'+ datetime.now().strftime("%Y%m%d") # formate as 5_20211220 i.e stockcode_yyyymmdd
    temp[LABEL_MAX_PRICE] = maxPrice
    temp[LABEL_MAX_VOL] = maxVol
    temp[LABEL_VOL] = vCol
    temp.index=temp.index.time
    return temp #return dataframe in Dave-format for a single stock FROM IB Data

# # def getHKExStocksPrice(allHKExStocksDf,startDate, endDate):
# def ibDnLoadPrices1D(allHKExStocksDf,  oneDay, ses, sample=False):
#     """
#     For getting all HKEx traded stocks prices, during lunch time.
#         'Currently only support for 1day operation only.' due to ib2DetaFormat1D()

#     Parameters
#     ----------
#     allHKExStocksDf : dataframe load from Excel CSV
#     startDate : the python standard datatime datatype
#     endDate : the python standard datatime datatype
#     ses : IB connected session handler
#     sample: False => download all.  N => download 1st N stocks only

#     Returns: todayStockDf. a dataframe

#     """  
#     RETRY_MAX=3 #max times of retry to download the oneDay data.
#     ## Creat GLOBAL log file handler for usage of ALL functions within this API, 25apr2021 hsl
#     ibLogPath=getCwdPath()+'prd-outputs\\'+'ibLog'+datetime.now().strftime('%Y-%b-%d')+'.txt' # log file with time stamp
#     GLOBAL_logHandler=openFileEmailAdm(ibLogPath) # open writeable file and emailAdm if error    

#     todayStockDf = pd.DataFrame(columns=[LABEL_PRICE, STOCK_CODEDATE, LABEL_MAX_PRICE,
#             LABEL_MAX_VOL, LABEL_VOL]) #create a blank dataframe

#     failed=[]; nowaday=datetime.now().strftime("%Y%m%d")
#     stockCodes=list(allHKExStocksDf.index) if not sample else list(range(sample))
#     for code in stockCodes:  #22dec2021
#             #i/p: code must in a list. o/p contract is also a list, [0] to get the only element from the list
#         code=str(code) # int to string
#         contract=creatQliTradeContracts([code], ses, secType='STK')[0] 

#         j=0
#         while j < RETRY_MAX:            
#             stockDf, symbol=dataFrIb1D(ses, oneDay, contract)  #i/p: a contract, can't be a list. https://interactivebrokers.github.io/tws-api/historical_limitations.html
#             if not isinstance(stockDf, pd.DataFrame): #fail
#                 j +=1; continue #retry
#             else: #success
#                 stockDf=ib2DetaFormat1D(code, stockDf, nowaday) #convert from IB format to Deta format.
#                 todayStockDf = todayStockDf.append(stockDf) #merge vertically, https://stackoverflow.com/questions/41181779/merging-2-dataframes-vertically
#                 print(f"Asset-symbol:{code} done."); break   

#         if j >= RETRY_MAX:
#             print(f'Asset-symbol:{symbol} fail!. Not a valid dataframe, skipped.'); failed.append(symbol)
#             # print('asset-stock:'+ str(code) + ' download skipped.', file=GLOBAL_logHandler) 

#     dict = {'symbols': failed}  
#     df = pd.DataFrame(dict) ; df.to_csv(getCwdPath()+ 'failedAsset-Stock.csv')
#     body='Assets(symbols): No data available, IB data service found nothing. Stock suspended, no-trades or bugs!'
#     noticeTraders(body, ADM_EMAILS, ['failedAsset-Stock.csv'], 'Failed records.')
    
#     print('Finished download IB data!', file=GLOBAL_logHandler); print('Finished download the IB data!') #25apr2021 hsl
#     GLOBAL_logHandler.close() #make sure file closed file-buffer before email&exist #25apr2021 hsl
#     return todayStockDf

def getHKExStocksPrice(allHKExStocksDf,startDate, endDate):
    ## Creat GLOBAL log file handler for usage of ALL functions within this API, 25apr2021 hsl
    yahooLogPath=getCwdPath()+'prd-outputs\\'+'yahoolog'+datetime.now().strftime('%Y-%b-%d')+'.txt' # log file with time stamp
    GLOBAL_logHandler=openFileEmailAdm(yahooLogPath) # open writeable file and emailAdm if error    
    
    PRICE_COL=0; VOL_COL=1 #"0" = price column or "1" = volume column
    # timeIndexSource = TIMEINDEX #3jan2022
    timeIndexSource =pd.read_excel(getCwdPath()+'timeIndex.xlsx',index_col=0) #6jan2022, CANNOT replace the timeIndex.xlsx. Big difference between two ways.
    mergeP = timeIndexSource.copy(deep=True)  #clear the entry after process one code
    mergeV = timeIndexSource.copy(deep=True)

    def fillDataFrameValue(dfP, dfV):
        dfP.fillna(method = 'ffill', inplace=True)
        dfP.fillna(method = 'bfill', inplace=True)

        if dfV.isna().values.any(): #20191219 detect if there are any nan values in any element
            dfV.fillna(0.0, inplace=True)   # fill all NaN by zeros, Hoson 11Dec

        return

    def getYahooFinanceDataByCode(code,startDate,endDate):
        maxTry=10 #try 10 times at most
        INTERVAL = '1m' # 1m = 1 minute data
        codeFormat = '{:d}'.format(code).zfill(4) + '.HK' # format to 0000, if stockCode= 1, then 0001.HK    print(code)

        for attempts in range(maxTry): #try max+1 times
            try:
                df= yf.download(tickers=codeFormat, start=startDate, end=endDate, interval=INTERVAL, progress=False) #ret empty df if no-data at all, H
                df.index = pd.to_datetime(df.index)  #convert index to datetime format
                df.index = df.index.tz_localize(None) #remove the time zone information while keeping the local time (not converted to UTC)
            # except Exception:
            except ConnectionError as e:
                print(e); print(e, file=GLOBAL_logHandler) #25apr2021 hsl
                continue # continue the loop to next attempt.               
            except ValueError as e:
                print (e); print(e, file=GLOBAL_logHandler) #25apr2021 hsl
                print(str(code) + ' may have Value Error, symbol may be delisted', file=GLOBAL_logHandler) #25apr2021 hsl
                break # break the loop immediately.
            break #stop loop immediately

        if attempts > maxTry:
            print("!!!!!!!!! yf.download() failed after several tries !!!!!!!!!!!!!!", file=GLOBAL_logHandler) #25apr2021 hsl
            emailAdmin('Error in yf.download()', '  From:'+sys.argv[0])

        return df


    def returnSingleAmPM(pCol,vCol,code):
        # logFile = open('log.txt','w')  #record the log in text file #2020May3

        try:
            maxPrice= pCol.iloc[0:PRICE_11_59a+1].max()[0]  #only find the morninig max, store the max for each column
            maxVol = vCol.iloc[0:PRICE_11_59a+1].max()[0] # [0] mean get series first row value and become float

            ###Revised the location of timeindex.xlsx 20May2020
            temp = timeIndexSource #clear the temp file
            # for each column
            pCol = pCol.div(maxPrice) #normalize Price
            if maxVol !=0:  vCol = vCol.div(maxVol) #normalize Volume
            temp[LABEL_PRICE] = pCol
            temp[STOCK_CODEDATE] = pCol.columns[0]   #20191111  # Revised for this semi-auto
            temp[LABEL_MAX_PRICE] = maxPrice
            temp[LABEL_MAX_VOL] = maxVol
            temp[LABEL_VOL] = vCol

        except ValueError:
            print('Value Error returnSingleAmPM: ' + str(code) )
            print('Value Error returnSingleAmPM: ' + str(code), file=GLOBAL_logHandler) #fix an fileOpen exception problem,19nov2020

        # logFile.close() #tidy-up,19nov2020
        return temp.iloc[0:PRICE_END+1, :]   #20May2020 reduced the output files to 2

    def transformYahooFinanceToHKEXFormat(yahooStockDf):
        if not yahooStockDf.empty: #if the excel file is not empty
            HKEXstockDf=yahooStockDf.copy()
            HKEXstockDf.index = HKEXstockDf.index.strftime('%Y/%m/%d %H:%M')

            HKEXstockDf = HKEXstockDf.iloc[:,4:6] # only Adj Close and Volume left
            HKEXstockDf.columns = [LABEL_PRICE, LABEL_VOL]  # Formatted dataframe matched with HKEX, transformed yahoo finance data
        return HKEXstockDf

    #Check if yahoo finance records has duplicate/incorrect axis
    def checkYahooDateDuplicateDates(HKEXstockDf,code): #9June2020 - add code as input
        HKEXstockDf['date']=HKEXstockDf.index.date
        if len(HKEXstockDf['date'].value_counts().index) > 1:  # >1 means there are duplicate dates, the dataset contain incorrect data needed to remove
            print('Code: ' + str(code) + ' has duplicate dates', file=GLOBAL_logHandler)
            correctIndex = HKEXstockDf['date'].value_counts().idxmax()
            incorrectIndexList = HKEXstockDf[HKEXstockDf['date']!=correctIndex].index.tolist()
            for incorrectIndex in incorrectIndexList:
                dropList=HKEXstockDf[HKEXstockDf['date']==incorrectIndex].index.tolist()
                for i in dropList:
                    HKEXstockDf = HKEXstockDf.drop(index=i)
        HKEXstockDf = HKEXstockDf.drop(['date'], axis=1)
        return HKEXstockDf

    # df is the current stock excel , change the format of input file before merging
    def changeExcelFormat(df,date,code):
        df.columns = [str(code) +'_'+ date, str(code) +'_'+ date]   # column changed to 20190502
        df.index = df.index.time
        df.index.names = ['Index']
        return df

    todayStockDf = pd.DataFrame(columns=[LABEL_PRICE, STOCK_CODEDATE, LABEL_MAX_PRICE,
           LABEL_MAX_VOL, LABEL_VOL]) #create a blank dataframe

    for i in range(len(allHKExStocksDf.index)):  #27May2020

        code = allHKExStocksDf.index[i] #27May2020
        codeFormat = '{:d}'.format(code).zfill(4) + '.HK' # format to 0000, if stockCode= 1, then 0001.HK    print(code)
        try:
            yahooStockDf= yf.download(tickers = codeFormat,  start= startDate, end= endDate , interval = '1m') ## 1m = 1 minute data, ret empty df if no-data at all, H
            yahooStockDf.index = pd.to_datetime(yahooStockDf.index)  #convert index to datetime format, remove the time zone information while keeping the local time (not converted to UTC)
            yahooStockDf.index = yahooStockDf.index.tz_localize(None) #remove the time zone information while keeping the local time (not converted to UTC)
        except Exception:
            print(str(code) + ' may have Value Error, symbol may be delisted', file=GLOBAL_logHandler) #25apr2021 hsl
            print(str(code) + ' may have Value Error, symbol may be delisted')

        if not yahooStockDf.empty:  #if No data found for this code, maybe delisted or no trading on that day
            HKEXstockDf = transformYahooFinanceToHKEXFormat(yahooStockDf) #transform yahoo to HKEX format
            HKEXstockDf.index = pd.to_datetime(HKEXstockDf.index) #change index to datetime format, otherwise, it is string type

            #Check if yahoo finance records has duplicate/incoorect axis
            HKEXstockDf = checkYahooDateDuplicateDates(HKEXstockDf,code)

            # Change Dave train set format
            date = str(HKEXstockDf.index.date[0]).replace('-', '')
            HKEXstockDf = changeExcelFormat(HKEXstockDf, date, code)

            # Fit the index from 9:30am to 16:08pm , total length of index would be 399
            pCol = pd.merge(mergeP, HKEXstockDf.iloc[:,PRICE_COL], left_index=True, right_index=True, how='outer')
            vCol = pd.merge(mergeV, HKEXstockDf.iloc[:,VOL_COL], left_index=True, right_index=True, how='outer')

            # Fill na value
            fillDataFrameValue(pCol,vCol)

            testSet = returnSingleAmPM(pCol,vCol,code)

            # Append the stcok code data to the result testSet for Dave
            todayStockDf = todayStockDf.append(testSet)

    print('Finished download the yahoo data!', file=GLOBAL_logHandler); print('Finished download the yahoo data!') #25apr2021 hsl
    GLOBAL_logHandler.close() #make sure file closed file-buffer before email&exist #25apr2021 hsl
    return todayStockDf

def getHkexStockList(): # download all HKEx stocks info and save into AllStockTable.xwlsx
    #### Download with retries and error checking/reporting by lower level http request instead by pandas directly.   
    fileName=httpDownloadNSaveExcel('https://www.hkex.com.hk/chi/services/trading/securities/securitieslists/ListOfSecurities_c.xlsx')   
    # Get Date
    stockList = pd.read_excel(getCwdPath()+fileName, index_col=0) #read SEHK's original raw list in current folder. New or maybe old
    # date = stockList.index[0]
    # date= date.replace("截 至 ","")  # get 截 至 27/06/2019'
    # date= date.split("/")[2] + date.split("/")[1] + date.split("/")[0] # convert to 20190627
    
    # copy a new stockList and change the column name
    stockList1=stockList.copy()
    stockList1.columns = stockList1.iloc[1] # Change column name as second row
    stockList1= stockList1[2:] #ignore the first 2 rows
    
    #filter the rows
    array = [C_STOCK, C_ETF, C_REIT] #only show stock, ETF & REIT
    stockList1=stockList1.loc[stockList1[C_SEHK].isin(array)]
    
    # format data 
    stockList1.index = stockList1.index.astype(int)   # convert '00001' to integer 1
    stockList1[LOT_SIZE] = stockList1[LOT_SIZE].str.replace(',', '') # change 1,000 to "1000"
    stockList1[LOT_SIZE] = stockList1[LOT_SIZE].astype(int) # change "1000" to integer 1000
    
    stockList1.index.names = ['股票代號']
    stockList1.rename(columns = {'股份名稱':COM_NAME}, inplace = True)
    stockList1.to_excel("AllStockTable.xlsx")
        
    return stockList1

def getSymbol(contract): #work no matter WAR or STK, 13dec2021
    if contract.secType=='STK':
        symB=contract.symbol #stock use original stock symbol
    else: symB=contract.localSymbol #warrant, others use localSymbol

    return symB

# def retTickerPrice(ticker):
#     """
#     Make sure not Nan before return the price

#     Parameters
#     ----------
#     ticker : stock ticker

#     Returns: curren realtime price

#     """
#     DEBUG=True
#     # if ticker.contract.secType=='STK':
#     #     ibs.IB.sleep(IB_DELAY*1.22) #need >1.21, 20dec2021. Enough delay make 1st try success.
#     # else: ibs.IB.sleep(IB_DELAY*2) #need >1.99, 20dec2021.

#     i=0; 
#     while i<1000:
#         price=ticker.marketPrice()
#         if np.isnan(price): #check price is NOT Nan. MAKE sure price available by retries
#             if i%10==0: print(f'Invalid Price={ticker.marketPrice()} during loop:{i}')
#             # ibs.IB.sleep(IB_DELAY); i+=1
#             ibs.IB.sleep(IB_DELAY/5); i+=1
#         else: # got a valid price, NOT Nan
#             if DEBUG: print(f'Got the price at loop {i}.')
#             break
#         # print(f'Cannot get the price after {i} trys !!!')
    
#     return price

def dataFrIb1D(ses, oneDay, contract): #12dec2021
    """
    Download 1 day historical data from IB, in according to a contract.
        
    Parameters
    ----------
    oneDay: The day to get data
    contract : one contract
    Returns
    -------
    the dataframe downloaded from IB.

    """
    # END_HR, END_MIN=16, 8 #end time of stop getting historical data
    oneDay=oneDay.replace(hour=16, minute=8) #end time of stop getting historical data
    symB=getSymbol(contract) #auto handle stock or warrant

    # print(f'Downloading asset-symbol:{symB} data.')
    bar = ses.reqHistoricalData( #limitation: https://interactivebrokers.github.io/tws-api/historical_limitations.html
                        contract,
                        endDateTime=oneDay,  # empty string indicates current present moment
                        durationStr='1 D', #'20 D', #S, D, W, M, Y.  https://interactivebrokers.github.io/tws-api/historical_bars.html
                        barSizeSetting='1 min', #down to 1s and up to 1month
                        whatToShow='TRADES', # TRADES/ADJUSTED_LAST /MIDPOINT
                        useRTH=False, #True, #True set to retrieve data generated only within Regular Trading Hours (RTH)
                        formatDate=1,#only yyyyMMdd format is available.
                        keepUpToDate=False, #NO REALtime update
                                )
    df=None if not bar else ibs.util.df(bar) #None indicate got nothing wrt an invalid dataframe

    ses.cancelHistoricalData(bar) #reduce simulatantously opened requests.
    return df, symB

# def getHKExStocksPrice(allHKExStocksDf,startDate, endDate):
def ibDnLoadPrices1D(allHKExStocksDf,  oneDay, ses, sample=False):
    """
    For getting all HKEx traded stocks prices, during lunch time.
        'Currently only support for 1day operation only.' due to ib2DetaFormat1D()

    Parameters
    ----------
    allHKExStocksDf : dataframe load from Excel CSV
    startDate : the python standard datatime datatype
    endDate : the python standard datatime datatype
    ses : IB connected session handler
    sample: False => download all.  N => download 1st N stocks only

    Returns: todayStockDf. a dataframe

    """  
    RETRY_MAX=2 #max times of retry to download the oneDay data.
    ## Creat GLOBAL log file handler for usage of ALL functions within this API, 25apr2021 hsl
    ibLogPath=getCwdPath()+'prd-outputs\\'+'ibLog'+datetime.now().strftime('%Y-%b-%d')+'.txt' # log file with time stamp
    GLOBAL_logHandler=openFileEmailAdm(ibLogPath) # open writeable file and emailAdm if error    

    todayStockDf = pd.DataFrame(columns=[LABEL_PRICE, STOCK_CODEDATE, LABEL_MAX_PRICE,
            LABEL_MAX_VOL, LABEL_VOL]) #create a blank dataframe

    failed=[]; nowaday=datetime.now().strftime("%Y%m%d")
    stockCodes=list(allHKExStocksDf.index) if not sample else list(range(sample))
    for code in stockCodes:  #22dec2021
            #i/p: code must in a list. o/p contract is also a list, [0] to get the only element from the list
        code=str(code) # int to string
        contract=creatQliTradeContracts([code], ses, secType='STK')[0] 

        j=0
        while j < RETRY_MAX:            
            stockDf, symbol=dataFrIb1D(ses, oneDay, contract)  #i/p: a contract, can't be a list. https://interactivebrokers.github.io/tws-api/historical_limitations.html
            if not isinstance(stockDf, pd.DataFrame): #fail
                print(f'===============> Tried {j+1} time stockcode {code}'); j +=1;  continue
            else: #success
                stockDf=ib2DetaFormat1D(code, stockDf, nowaday) #convert from IB format to Deta format.
                todayStockDf = todayStockDf.append(stockDf) #merge vertically, https://stackoverflow.com/questions/41181779/merging-2-dataframes-vertically
                print(f"Asset-symbol:{code} done."); break   

        if j >= RETRY_MAX:
            print(f'Asset-symbol:{symbol} failed at {j+1} times again!. Not a valid dataframe, skipped.'); failed.append(symbol)
            # print('asset-stock:'+ str(code) + ' download skipped.', file=GLOBAL_logHandler) 

    dict = {'symbols': failed}  
    df = pd.DataFrame(dict) ; df.to_csv(getCwdPath()+ 'failedAsset-Stock.csv')
    body='Assets(symbols): No data available, IB data service found nothing. Stock suspended, no-trades or bugs!'
    noticeTraders(body, ADM_EMAILS, ['failedAsset-Stock.csv'], 'Failed records.')
    
    print('Finished download IB data!', file=GLOBAL_logHandler); print('Finished download the IB data!') #25apr2021 hsl
    GLOBAL_logHandler.close() #make sure file closed file-buffer before email&exist #25apr2021 hsl
    return todayStockDf

def dataFrIb(ses, startDay, stopDay, contract, MAX_FAIL=45): #12dec2021
    """
    Download historical data from IB, in according to a contract.
        Get data from [startDay, stopDay), excluded stopDay in Python start:stop practise.
    
    Parameters
    ----------
    startDay : StartDay. formated-datetime,  first date to download (go backward, download and stop when reached first date)
    stopDay : StopDay. formated-datetime, last date that download NOTHING.
    contract : one contract
    MAX_FAIL: no of consecutive failed trys, before stop the download for a contract

    Returns
    -------
    the dataframe downloaded from IB.

    """
    assert startDay != stopDay, 'Invalid start:stop dates.'
    
    END_HR, END_MIN=16, 8 #end time of stop getting historical data

    stopDay=stopDay - timedelta(days=1)
    startDay=startDay.replace(hour=END_HR, minute=END_MIN)
    stopDay=stopDay.replace(hour=END_HR, minute=END_MIN)

    symB=getSymbol(contract)
    dt=stopDay; dtSuccess=dt
    barsList=[]; i=0 #retry counts
    while True:
        print(f'Downloading asset with symbol: {symB} ')
        bars = ses.reqHistoricalData(
            contract,
            endDateTime=dt,  # empty string indicates current present moment
            durationStr='1 D', #'20 D', #S, D, W, M, Y.  https://interactivebrokers.github.io/tws-api/historical_bars.html
            barSizeSetting='1 min', #down to 1s and up to 1month
            whatToShow='TRADES', # TRADES/ADJUSTED_LAST /MIDPOINT
            useRTH=False, #True, #True set to retrieve data generated only within Regular Trading Hours (RTH)
            formatDate=1,) #only yyyyMMdd format is available.
            # keepUpToDate=False) # True to return updates of unfinished real time bars as they are available
        if not bars: #nothing got from reqHistoricalData()
            dt=dt - timedelta(days=1) #go back 1day
            print(f'Fail {symB}: {i}. Go back 1 more day.'); i +=1
            if i >MAX_FAIL: #stop getting data after 10 consective days.
                print(f'Stop after {i} trys.')
                break
        else:
            i=0 #reset count
            barsList.append(bars)
            dt = bars[0].date
            dtSuccess=dt; dtSuccess=dtSuccess.replace(hour=END_HR, minute=END_MIN)
            print(f'Success {symB}: {i}. Got data from {dtSuccess}.')
            if dtSuccess <= startDay: #smaller or equal to
                break
        
        # save to a CSV file
    allBars = [b for bars in reversed(barsList) for b in bars] #e.g. newList = [ expression for item in list ], reversed([2, 3, 5, 7[]) => [7,..]
    df = ibs.util.df(allBars)
    return df, symB

def dataFrIb2Csv(ses, startDay, endDay, contract, MAX_FAIL=45):
    df, symB=dataFrIb(ses, startDay, endDay, contract, MAX_FAIL=45) #get data up to current minute-second
    df.to_csv( symB + '_'+endDay.strftime('%Y-%b-%d')+ '.csv', index=False)
    return

def reRegisterEmail():
    yagmail.register('detadaytrade01@gmail.com', 'xxxxx') #9may2023
    yag = yagmail.SMTP('detadaytrade01@gmail.com')

    # # file=getCwdPath().split('2-sourceCodes')[0]+'\\detalibs\\gmail.json' #location of the json file
    # yag = yagmail.SMTP('detadaytrade01@gmail.com', oauth2_file='yagmail.json')
    # yag.send(subject="Great!")
    
    print('Registered ya-gmail log data....')
    return yag

def noticeTraders(emailBody, bccEmails, fileList, subjectAddInto): #send email to bcc emails & attach files
    maxTry=10 # resend email at most 10times
    for attempts in range(maxTry): #creat [0,1,2...9] if maxTry=10
        try:
            yag = yagmail.SMTP("detaDayTrade01@gmail.com"); print("Sending emails & attachments", fileList, end="..!")
            yag.send(to="detaDayTrade01@gmail.com", bcc=bccEmails,
                     subject="Email and attachments from DeTa's fund manager " + subjectAddInto,
                     contents=emailBody,
                     attachments=fileList)
        except Exception as e:
            print(e)
            continue  # continue the loop to next attempt.
        break  # break the loop immediately.

    if attempts < maxTry:
        print(f'Email success send at {attempts+1} tries.')
    else: print('Cannot send the email, by noticeTraders() !')

def emailAdmin(subjectMsg: str, body: str=''):
    """ Email system admins defined by ADM_EMAILS
    :param subjectMsg: email subject
    :param body: email content
    :return: None
    """
    email2List(ADM_EMAILS, subjectMsg, body)
    # maxTry=10 # resend email at most 10times
    # for attempts in range(maxTry): #creat [0,1,2...9] if maxTry=10
    #     try:
    #         yag = yagmail.SMTP("detaDayTrade01@gmail.com")
    #         yag.send(to="detaDayTrade01@gmail.com", bcc=ADM_EMAILS,
    #                  subject=subjectMsg,
    #                  contents=body + '\nAt UTC time=' + datetime.now().astimezone(timezone.utc).strftime(
    #                      '%Y-%m-%d %H:%M:%S') + ' +8hrs is HKT'
    #                  )
    #     except Exception as e:
    #         print(e)
    #         continue  # continue the loop to next attempt.
    #     break  # break the loop immediately.

    # if attempts < maxTry-1:
    #     print(f'Email success send at {attempts+1} tries.')
    # else: print('Cannot send the email, emailAdmin() !')

def email2List(emails:list, subjectMsg: str, body: str=''):
    """ Email system admins defined by ADM_EMAILS
    :param subjectMsg: email subject
    :param body: email content
    :return: None
    """
    maxTry=10 # resend email at most 10times
    for attempts in range(maxTry): #creat [0,1,2...9] if maxTry=10
        try:
            yag = yagmail.SMTP("detaDayTrade01@gmail.com")
            yag.send(to="detaDayTrade01@gmail.com", bcc=emails,
                     subject=subjectMsg,
                     contents=body + '\nAt UTC time=' + datetime.now().astimezone(timezone.utc).strftime(
                         '%Y-%m-%d %H:%M:%S') + ' +8hrs is HKT'
                     )
        except Exception as e:
            print(e)
            continue  # continue the loop to next attempt.
        break  # break the loop immediately.

    if attempts < maxTry-1:
        print(f'Email success send at {attempts+1} tries.')
    else: print('Cannot send the email, emailAdmin() !')
    
    return


def dict2DfEmailAdm(d: dict, subject:str, body: str):
    """ Convert Dict to Dataframe and email the dataframe to admin
    :param d: is a dictionary of column labels and values
    :param subject: The email subject content
    :param body: The email body content
    :return: None
    """
    df = pd.DataFrame(d); tempfile='temp_temp.csv'
    df.to_csv(tempfile); print(df)
    noticeTraders(body, ADM_EMAILS, tempfile, subject) # email an Excel file to Admin

def getProfitDfDenormal(priceVolDf, similarity, aDayLengthEnd, profitableIndex, predictTwoPrices): #O/P prices DENORMALIZED
# ======= Preprocess Indexes, de-normalise output prices and find the right stock codes for saving-up results ====================
    if predictTwoPrices is not None: #debug 5sep2021. fix when not stocks found
        profitStockIndex=np.multiply(profitableIndex, aDayLengthEnd) #A3 broadcast multiply 4_08p+1/11:59a+1 into the array
        profitStockIndex=profitStockIndex.flatten() #A4, convert to 1D for iloc in followings
        results=priceVolDf[ [STOCK_CODEDATE, LABEL_MAX_PRICE, LABEL_MAX_VOL] ] # Python auto-creat a copy as the new value results is used. 
        results=results.iloc[profitStockIndex, :] #A2, slice out Only profitable
        results[PREDICT_1ST] =np.around(predictTwoPrices[:,0]*results[LABEL_MAX_PRICE],decimals=2) #DENORMALIZED by multipy MAX and round to xx.yy as aastock/yahoo/HKEx,  4jun2020
        results[PREDICT_2ND] =np.around(predictTwoPrices[:,1]*results[LABEL_MAX_PRICE],decimals=2) #buy-in, sell-out time. 1:00p,3:00p but force sellOut at 3:30p. 4jun2020
        results[SIM_MEASURE] =similarity # Keras model.predict()'s probability as a similarity measures for prioritisation or else..
    else: results=None
    
    return results #O/P prices DENORMALIZED by multiply MAX_PRICE. Keep o/p MAX_VOL for trading amount prioritisation purpose.

def constructDf(df, profitIndex:tuple, length:int):
    """
    construct a dataframe from the input dataframe, df, in according to the
    fixed length stock-day data
    Parameters
    ----------
    df : pandas dataframe, e.g. df from the "all-fulldayDS4Predict.csv"
        DESCRIPTION.
    profitIndex : list of int index to which stock-day are found profitable.
        DESCRIPTION. Index to the fixed length stock-day data, [0] is 1st, [1] is 2nd etc..
    length : number of data points per stock-day.
        DESCRIPTION.

    Returns the reconstructed dataframe
    -------
Ref:    Last Traded Price	Stock Code&Date	The Max Price	The Max Volume	Volume
    """
    profitIndex=list(profitIndex[0]) # tuple to list conversion. profitIndex is a tuple[1,x]
    # colNames = [LABEL_PRICE, STOCK_CODEDATE, LABEL_MAX_PRICE, LABEL_MAX_VOL, LABEL_VOL] 
    newDf = pd.DataFrame(columns=df.columns) # auto-gen with index 0,1,2... after fill in data
    tmpDf = pd.DataFrame(columns=df.columns)
    
    for idx in profitIndex:
        start= int(idx*length); stop= int(start + length) #force integer for safe
        tmpDf=df.iloc[start:stop, :] #view only
        newDf=newDf.append(tmpDf, ignore_index = False) # follow newDf index, ignore tmpDf index. Copy creat

    return newDf # the constructed profit only dataframe

class DaveBaseClass(object): # The Dave output variables ONLY, no excel files
    name="Mr. DaveBase002" # Class variable, same for all instances of fr the Class, A7
    
    def __init__(self, classfiModel, predictModel, simThreshold, aDayLengthEnd): # A7, self meanings
        """
        Load NNs and init similarity thresholding value (default 0.5)
        Parameters
        ----------
        classfiModel : pandas dataframe
        predictModel : int which represent time from 9:30am (0)
        simThreshold : similarity threshold value for the classifier
        aDayLengthEnd :

        Returns: None
        -------
        """
        self.classfiNN=classfiModel 
        self.predictNN=predictModel
        self.simThreshold=simThreshold # classification probabi lity used other than Kera's default 0.5, each class instance is difference
        self.aDayLengthEnd=aDayLengthEnd # oneDay price-vol lenght, default=PRICE_END=4:08p but can be modified when necessary.

    def _getProfitIdxSim(self, priceVolDf, sliceTimeStart, sliceTimeEnd):  #O/P predict prices are still normalized ratio
        """
        Classfi and get profitable index to the stock-day data and corresponding similarity 

        Parameters
        ----------
        priceVolDf : pandas dataframe
        sliceTimeStart : int which represent time from 9:30am (0)
        sliceTimeEnd : int which represent time from 11:59am (150)

        Returns
        -------
        profitableIndex : list
        similarity : list

        """
        # For the Classifier, Classfi
        temp=priceVolToChopImages(priceVolDf, self.aDayLengthEnd, sliceTimeStart, sliceTimeEnd) # I/P full-lenght daily price-vol (9:30a-4:08p) but output CHOPPED
        # Spyder View variable: temp =temp.reshape(temp.shape[0], sliceTimeEnd, TOTALCOL)
        temp =temp.reshape(temp.shape[0], sliceTimeEnd, TOTALCOL, CHANNEL) #reshape for CNN1D API, add CHANNEL=1
                                                # Classify Profitable Stocks
        similarity=self.classfiNN.predict(temp, verbose=0) #2D array[i][p0,p1], A4
        predictProfitability=np.full(similarity.shape[0], NON_PROFITABLE) #default init as NON_PROFITABLE, 19may2020
        tempBoolean=similarity[:,PROFITABLE] > self.simThreshold #A5, creat True/False array if > the simThreshold, 22may2020
        # print(f'Binary classification threshold-value using:{self.simThreshold}') # 31dec2020
        print(f"Found stocks with (similarity > similarityThreshold:{self.simThreshold}): {np.count_nonzero(tempBoolean)}") #5sep2021, 0 will cause problem onward
        predictProfitability[tuple([tempBoolean])]=PROFITABLE #set as profitable for TRUE entry, 19may2020. Use tuple() to remove a Future warning.
        
        profitableIndex= np.where(predictProfitability==PROFITABLE) #a tuple[0,x]. index of elements with value PROFITABLE
        similarity=similarity[profitableIndex, :] #slice out the corresponding profitable stock probabilities as a similarity measures
        similarity=similarity[0,:,PROFITABLE] #(1,size(profitableIndex),2), get the probability at profitColumn [x,x,1]
        
        return profitableIndex, similarity #5sep2021, profitableIndex=0 will cause problem
     
    def _classfi(self, priceVolDf, sliceTimeStart=getDetaConfig()[0], sliceTimeEnd=getDetaConfig()[1]):
        """                 Use only in 'auto-ClassfiPredictParaTrainTest.py'
        Classify priceVolDf and extract profitable stock-day data in linear fashion(not array tensors)
        for training dataset type of usage.
        Parameters
        ----------
        priceVolDf : panda dataframe
        sliceTimeStart : optional
            DESCRIPTION. The default is getDetaConfig()[0].
        sliceTimeEnd : optional
            DESCRIPTION. The default is getDetaConfig()[1].

        Returns
        -------
        profitableExtract : dataframe
        """
        profitableIndex, _ =self._getProfitIdxSim(priceVolDf, sliceTimeStart, sliceTimeEnd)
        profitableExtract=constructDf(priceVolDf, profitableIndex, self.aDayLengthEnd)
        return profitableExtract # O/P predict prices are still normalized ratio.

    def _classfiPredict(self, priceVolDf, sliceTimeStart, sliceTimeEnd): #O/P predict prices are still normalized ratio
        profitableIndex, similarity =self._getProfitIdxSim(priceVolDf, sliceTimeStart, sliceTimeEnd)

        # For the Predictor, Predict. fxx.. for 9:30a-4:08p. xx.. for 9:30a-1:05p
        pricesExtract=np.array( priceVolDf[ LABEL_PRICE ].values, dtype="float32" ) # turn to np array, price-max pair. ! .to_numpy() DO'nt work
 
# =============================================================================
         # pricesExtract=pricesExtract.reshape(int(pricesExtract.shape[0]/self.aDayLengthEnd), self.aDayLengthEnd) #PRICE_4_08p+1=price per full-day
        if PREDICT_MODEL==CNN1D or PREDICT_MODEL==RNN: # 12jan2021
            pricesExtract=pricesExtract.reshape(int(pricesExtract.shape[0]/self.aDayLengthEnd),
                                                 self.aDayLengthEnd, 1) # (time-step, features per step)
            print('Reshaped data for CNN1D or RNN model in shape:', pricesExtract.shape)
        else:
            pricesExtract=pricesExtract.reshape(int(pricesExtract.shape[0]/self.aDayLengthEnd), self.aDayLengthEnd) #PRICE_4_08p+1=price per full-day 
            print('Reshaped data for Linear Model in shape:', pricesExtract.shape)
# =============================================================================
        profitableExtract=pricesExtract[profitableIndex]
                                                # PREDICT PRICES from the classified profitable stocks
        profitableExtract=profitableExtract[:, sliceTimeStart:sliceTimeEnd] #for NN API, sliceout 9:30a-11:59a without 12:00n-12:59p. A5
        if len(profitableExtract) >0: #debug 5sep2021 when NO profitable stock found with the similarity greater than the threshold require
            predictTwoPrices=self.predictNN.predict(profitableExtract, verbose=0) #Normalized prices only, not real prices
        else: predictTwoPrices= None # ret None instead, 5sep2021
        
        return profitableExtract, predictTwoPrices, profitableIndex, similarity, self.aDayLengthEnd # O/P predict prices are still normalized ratio. profitableIndex can use to access raw input "priceVolDf" dataframe

class Dave(DaveBaseClass): # O/P prices&volumn DENORMALIZED. Output predictions results summary and profit dataframe with all price-vol
    def __init__(self, classfiModelFilename, predictModelFilename, simThreshold, aDayLengthEnd=(PRICE_END+1 -PRICE_START) ): #NoDefault simThre..,31Dec2020

        self.path=getCwdPath(); print("Two NN models for predictions MUST in same current directory of this Code !!")
        if tf.config.list_physical_devices('GPU'): # 30dec2020
            with tf.device("/GPU:0"): # make sure load into GPU
                classfiModel= tf.keras.models.load_model(self.path+ classfiModelFilename)
                predictModel= tf.keras.models.load_model(self.path+ predictModelFilename)
                print("Both Classfi & Predict models are loaded into GPU")
        else:
            classfiModel= tf.keras.models.load_model(self.path+ classfiModelFilename)
            predictModel= tf.keras.models.load_model(self.path+ predictModelFilename)
            print("GPU not available ! Loaded into default processing unit.")
            
        super().__init__(classfiModel, predictModel, simThreshold, aDayLengthEnd) # load models &initialize parent object

    def classfiPredictDf(self, priceVolDf): #O/P prices&volumn DENORMALIZED by multipy MAX_PRICE. Input is a dataframe, not file.
        """
        Classfi & Predict price-vol information which are converted as images and denormalize the prices and volumns
        :param priceVolDf: price-vol trading information dataframe
        :return: denormalized dataframe or two Nones if not profitable stocks found (5sep2021).
        """
        sliceTimeStart=getDetaConfig()[0]; sliceTimeEnd=getDetaConfig()[1]
        profitableExtract, predictTwoPrices, profitableIndex, similarity, aDayLengthEnd=super()._classfiPredict(priceVolDf,
                                                                                       sliceTimeStart, sliceTimeEnd) #A9, super()
        results=getProfitDfDenormal(priceVolDf, similarity, aDayLengthEnd, profitableIndex, predictTwoPrices) #Find the right profitb stock codes for saving-up DENORMALIZED prices results
        if results is not None: #debug 5sep2021
            # DENORMALIZE Prices and Volumns for outputs.
            deNormDf=priceVolDf.copy(deep=True) #21sep2020 fix modified todayStocksDf in calling function
            deNormDf[LABEL_PRICE]=priceVolDf[LABEL_PRICE]*priceVolDf[LABEL_MAX_PRICE] #4jun2020, 21sep2020
            deNormDf[LABEL_VOL]=priceVolDf[LABEL_VOL]*priceVolDf[LABEL_MAX_VOL]  #4jun2020, 21sep2020
            results=results[[STOCK_CODEDATE, PREDICT_1ST, PREDICT_2ND, SIM_MEASURE]]
        else: 
            deNormDf=None; results=None
        
        return deNormDf, results #O/P prices DENORMALIZED by multipy MAX_PRICE in getProfitable(). Keep o/p MAX_VOL for trading amount prioritisation purpose.
        
    def classfiPredict(self, priceFileName): #O/P prices&volumn DENORMALIZED by multipy MAX_PRICE. Input is a FILE in current directory.
        """
        Classfi & Predict price-vol information which are converted as images and denormalize the prices and volumns
        :param priceVolDf: price-vol trading csv file.
        :return: denormalized dataframe or two Nones if not profitable stocks found (5sep2021).
        """
        priceVolDf=loadDataset(self.path+ priceFileName); print("Pricefile for predictions MUST in same current directory of this Code !!")
        return self.classfiPredictDf(priceVolDf) #O/P prices DENORMALIZED by multipy MAX_PRICE. A8, call methods within same class
                                                 # if not stocks found, return two None

def printSysConfig():
    print("TF ver:", tf.__version__, end =" "); print(" ,Keras ver=",tf.keras.__version__, end =' ,')
    print(spro.check_output(["wmic","cpu","get", "name"])[46:87], end =' ,' ); print("No CPUs=",cpu_count())
    print("Python:", sys.version, end =' '); print("Ver:", sys.version_info)
#    print("\nCPU settings: ", device_lib.list_local_devices()[0]) # print NV GPU model
    if len(device_lib.list_local_devices())<2:
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
        print("!!!!!!!!!!! GPU is unavailable YET, TF & Cuda & cuDnn Versions MUST matched !!!!!!!!!!!!!!!!")
    else: print("\nGPU is: ", device_lib.list_local_devices()[1].physical_device_desc[16:38]) # print NV GPU model

def plotHistoryNValLoss(history, mString): # plot accuracy Vs validation loss convergency trend 
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    
    plt.figure() # Create a new invisible figure
    plt.title( "[0]:TrainSet in loop= " + mString)
    plt.xlabel('Epoch') #prepare x axis info
    plt.ylabel('Train Accuracy&loss') #prepare y axis info
    # plt.ylim([0,1.1]) # set y-axis largest limit, acc <=1, 1.1 ok bot not loss
    plt.plot(hist['epoch'], hist['acc'], label='TrainAcc') #plot(x,y with a label)
    plt.plot(hist['epoch'], hist['loss'],label = 'TrainLoss')
    plt.legend() #Place the x-y legends on the axes. Invisible unitl plt.show()
    
    if 'val_loss' in hist.columns: # plot only in validation mode SET
        plt.figure() # cmp validation set's acc Vs loss
        plt.title("[1]:Validation Set in loop= " + mString)
        plt.xlabel('Epoch')
        plt.ylabel('Validation Accuracy&Loss')
        plt.plot(hist['epoch'], hist['val_acc'], label='ValidAcc')  #A4
        plt.plot(hist['epoch'], hist['val_loss'], label = 'ValidLoss')
        plt.legend()
    else: print("Warning: Not validation data available for ploting")       
    
    plt.show(); plt.close(fig='all') #Display, close all figure.

def plotHistoryNValLossTF2(history, mString): # plot accuracy Vs validation loss convergency trend 
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    
    plt.figure() # Create a new invisible figure
    plt.title( "[0]:TrainSet in loop= " + mString)
    plt.xlabel('Epoch') #prepare x axis info
    plt.ylabel('Train Accuracy&loss') #prepare y axis info
    # plt.ylim([0,1.1]) # set y-axis largest limit, acc <=1, 1.1 ok bot not loss
    plt.plot(hist['epoch'], hist['accuracy'], label='TrainAcc') #plot(x,y with a label)
    plt.plot(hist['epoch'], hist['loss'],label = 'TrainLoss')
    plt.legend() #Place the x-y legends on the axes. Invisible unitl plt.show()
    
    if 'val_loss' in hist.columns: # plot only in validation mode SET
        plt.figure() # cmp validation set's acc Vs loss
        plt.title("[1]:Validation Set in loop= " + mString)
        plt.xlabel('Epoch')
        plt.ylabel('Validation Accuracy&Loss')
        plt.plot(hist['epoch'], hist['val_accuracy'], label='ValidAcc')  #A4
        plt.plot(hist['epoch'], hist['val_loss'], label = 'ValidLoss')
        plt.legend()
    else: print("Warning: Not validation data available for ploting")       
    
    plt.show(); plt.close(fig='all') #Display, close all figure.

def plotPrecisionNOthers(history, mString): # plot accuracy Vs validation loss convergency trend 
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    
    plt.figure() # Create a new invisible figure
    plt.title( "[0]:TrainSet in loop= " + mString)
    plt.xlabel('Epoch') #prepare x axis info
    plt.ylabel('Train Preci&loss') #prepare y axis info
    # plt.ylim([0,1.1]) # set y-axis largest limit, acc <=1, 1.1 ok bot not loss
    plt.plot(hist['epoch'], hist['precision'], label='TrainPreci') #plot(x,y with a label)
    plt.plot(hist['epoch'], hist['loss'],label = 'TrainLoss')
    plt.legend() #Place the x-y legends on the axes. Invisible unitl plt.show()

    if 'val_loss' in hist.columns: # plot only in validation mode SET
        plt.figure() # cmp validation set's acc Vs loss
        plt.title("[1]:Validation Set in loop= " + mString)
        plt.xlabel('Epoch')
        plt.ylabel('Validation Preci&Loss')
        plt.plot(hist['epoch'], hist['val_precision'], label='ValidPreci')  #A4
        plt.plot(hist['epoch'], hist['val_loss'], label = 'ValidLoss')
        plt.legend()
    else: print("Warning: Not validation data available for ploting")       
    
    plt.show(); plt.close(fig='all') #Display, close all figure.

def loadDataset(fileString):
    """
    Load default dataset from an Excel CSV, with invalid Nan checks
    :param fileString: is the Excel CSV file
    :return: Pandas dataframe with all data
    """
    dataset=pd.read_csv(fileString,index_col=0)
    if dataset.isna().values.any():
        print("Nan !!! in "+fileString+ "!!!") # Data values' NaN existance healthly checks    
    else: pass #print("Checked No Nan found")
    return dataset

def validateDataFormat(dataframe, filename): #filename of the dataframe read from
    # column size is exactly 5 only.
    if dataframe.shape[1] !=5: sys.exit(filename+" file format error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def loadAsChopImages(fileNamePath, priceVolLength, start, stop): # I/P daily price-vol lenght fixed (9:30a-4:08p) but output CHOPPED
    """
    Load price-vol Excel as a chopped Images in according to input variables
    :param fileNamePath: is the Excel CSV file
    :param priceVolLength: is number of minutes(prices) of input Dataframe in full(9:30a-4:08p) prices available from stock exchange
    :param start: is time(minute index) starting to slice out the prices.
    :param stop: is time ending to slice out the prices. [start,stop] are inclusive for both end points
    :return: Pandas dataframe with all data
    """
    dataset=loadDataset(fileNamePath); validateDataFormat(dataset, fileNamePath)
    return priceVolToChopImages(dataset, priceVolLength, start, stop) # 9mar2020

# =============================================================================
#  Dataframe input equivalent version of loadAsChopImages() above
# =============================================================================
def priceVolToChopImages(priceVolTuplesDataFrame, priceVolLength, start, stop): # I/P daily price-vol lenght fixed (9:30a-4:08p) but output CHOPPED
    priceVol= np.array( priceVolTuplesDataFrame[ [LABEL_PRICE, LABEL_VOL] ].values, dtype="float32" ) # turn to np array, price-max pair. ! .to_numpy() DO'nt work
    priceVol= padTwoSidesConstant(priceVol, CONST_PAD_SIZE, BEFORE_C, AFTER_C)
    priceVol= priceVol.reshape( int(priceVol.shape[0]/priceVolLength), priceVolLength, TOTALCOL )
    return priceVol[:, start:stop, :] # 9mar2020

def padTwoSidesConstant(npArray, CONST_PAD_SIZE, BEFORE_C, AFTER_C): #padding to make price-volume look like images for CNN1D
    npArray=np.pad(npArray, (CONST_PAD_SIZE, CONST_PAD_SIZE), 'constant', constant_values=(BEFORE_C, AFTER_C)) #A3, Top-Bottom and Left-Right,e.g CC=> 0CC0
    npArray=npArray[CONST_PAD_SIZE:(npArray.shape[0]-CONST_PAD_SIZE), :] #remove top-bottom PADDED zero/constant rows
    return npArray
 
def plotConfuMatrix(labels, predictions, string): #CONFUSION Matrix  
    if labels.ndim >1: labels=np.argmax(labels, axis=-1) # convert back matrix to vector for confusion_matrix()
    if predictions.ndim >1: predictions=np.argmax(predictions, axis=-1) #1-D array already, in fact not necessary. Design for change only!!
    
    #  cm=confusion_matrix(labels, predictions, labels=np.unique(labels), normalize=None) #A3, normalize=None or all
    cm=confusion_matrix(labels, predictions, labels=[0,1], normalize=None) #KNOWN two classed ONLY
    plt.figure(figsize=(5,5))
    sns.heatmap(cm, annot=True, fmt="d")
    plt.title(string+" [Confusion matrix]")
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label') 
    
    print("\nCM Matrix from ",string, "dataset -" )
# =============================================================================
# Cij is number of observations known in group i and predicted in group j.
# count of true negatives=C00, false negatives=C10, true positives=C11 and false positives=C01:
# =============================================================================
    if np.size(cm,1)>1: #A2, some case axis1 size=1 instead of 2 when 0/0
        print('Known NonProfitable, Detected NonProfitable (True Negatives): ', cm[0][0])
        print('Known NonProfitable, Detected Profitable (False Positives): ', cm[0][1]) #some case axis1 size=1 instead of 2 when 0/0
        print('Known Profitable, Detected NonProfitable (False Negatives): ', cm[1][0])
        print('Known Profitable, Detected Profitable (True Positives): ', cm[1][1])
        print('CORRECT profitable Predictions: ', cm[1][1], " from dataset total size: ", np.sum(cm[1])+np.sum(cm[0]) )
        if cm[0][1] !=0: print("TP/FP=",cm[1][1]/cm[0][1], end=" ")
        elif  cm[1][1]+cm[0][1] !=0: print(" Precision=",cm[1][1]/(cm[1][1]+cm[0][1]), end=" " )
        elif cm[1][1]+cm[1][0] !=0: print(" Recall=",cm[1][1]/(cm[1][1]+cm[1][0]), " !!!!!!!!!!!!!")
        else: print("All three divided by zeros, error") 
    else: print("Error as axis1 size=1 only and skip printings.")
       
    return cm    

def printLabelClassesInfo(string, npLabel):
    if npLabel.ndim >1: npLabel=np.argmax(npLabel, axis=-1) # convert 1-hot encoded label matrix to vector for confusion_matrix()

    class0, class1 = np.bincount(npLabel, minlength=2) #e.g class0=class encode by 0, NON_PROFITABLE
    total = class0 + class1
    print(string+' sample size:\n    Total: {}\n    Profitable: {} ({:.2f}% of total)\n'.format(
    total, class1, 100 * class1 / total))

def initAll():
    mpl.rcParams['figure.figsize'] = (12, 10); colors = plt.rcParams['axes.prop_cycle'].by_key()['color'] #init MatplotLibs
    results=pd.DataFrame(); printSysConfig() #init dummy dataframe. print TF,Py,GPU version
    path=getCwdPath()
    return colors, results, path

def getCwdPath():
    # path=os.getcwd(); path=path+"\\"
    #  if in Linux use : path=os.getcwd()+'/'
    if LINUX:
        path=os.getcwd()+'/'
    else:
        path=os.getcwd()+"\\" #for Win10

    return path

def joinIntoCwPath(filepath):
    destination= os.path.normpath( os.path.join(os.getcwd(),filepath) )
    return destination

def loadNpStrucArrAsDict(fileString): #load numpy structural array, convert to simple Python dictation immediately.
    """
    Load from saved dictionary in numpy .npy file which stored the dictionary as structual array
    :param fileString: filename.npy
    :return: the save dictionary
    """
    parameters=np.load(fileString, allow_pickle=True).item() #; parameters=classNcount.item() #A13 for pickle=True
    return parameters

def transactionFee(price_V, qty, mode=STK_MODE): # column operation, 25dec2020
    """
    Calculate transaction fee base on asset type, stock or warrant.
    :param price_V: price Vector Or price Scalar
    :param qty: quantity Vector Or quantity Scalar
    :param  mode: for stock or warrant commission calcualtion. 
    :return: the total charge including
        1) HKSE CCASS commission, 2) Broker Commission,
        3)SFC Charge, 4)HKSE Charge, 5)Stamp Duty,
        6) HKSE System Charge
    """
    minimun =(
            BROKER_MIN if (mode ==STK_MODE) else # min fee, stock mode
            BROKER_MIN_WAR if (mode ==WAR_MODE) else # min fee, warrant mode
            
            BROKER_MIN # default value if cannot match to any MODE
             )
    
    duty =(
            STAMP_DUTY if (mode ==STK_MODE) else
            STAMP_DUTY_WAR if (mode ==WAR_MODE) else
            
            STAMP_DUTY # default value if cannot match to any MODE
          )

    totalPrices = price_V*qty # one lot-size total price
    ccassComit = totalPrices*CCASS_COMIT  #HKSEx ccass commission, CCASS_COMIT=0.00002
    commission = totalPrices*BROKER_COMIT  # ib broker commission, BROKER_COMIT=0.001
    commission = [minimun if x< minimun else x for x in commission] # IB broker min charge, 25dec2020
    ccassComit[ccassComit<CCASS_MIN] = CCASS_MIN  # HKSEx, CCASS_MIN=2
    ccassComit[ccassComit>CCASS_MAX] = CCASS_MAX # HKSEx, CCASS_MAX=100
    Charge=commission +ccassComit +totalPrices*SFC_CHARGE +totalPrices*HKSE_CHARGE +totalPrices*duty +HKSE_SYS_CHARGE #25dec2020
    return Charge


# SUPPORT vector/scalar as inputs. Calculate the commission breakeven number-of-lot. 
def decideBuyLotSize(prices, lotQtyS, mode=BROKER_BEQ, asset=STK_MODE): #6feb2021. SUPPORT both vector or scalar inputs, H 11jun2020. default ONLY use broker commission for the calculation, 15Apr2020
    """
    Calculate breakeven lot size based on the mode (mode=1 broker comission ONLY ,mode=2 by broker & CCASS)
    :param prices: price Vector Or price Scalar
    :param lotQtyS: one lot-size Vector Or one lot-size Scalar
    :param mode: Default is 1=calculate BreakEven Qty by broker comission ONLY / 2=by broker & CCASS
    :return: breakeven number-of-lot
    """
    # minCommision = BROKER_MIN #default stock mode
    # if asset==WAR_MODE: minCommision = BROKER_MIN_WAR #6feb2021
    minCommision =( #6feb2021
            BROKER_MIN if (asset ==STK_MODE) else # min free, stock mode
            BROKER_MIN_WAR if (asset ==WAR_MODE) else # min free, warrant mode
            
            BROKER_MIN # default value if cannot match to any MODE
             )

    minCCASS = CCASS_MIN
    totalPrices = prices*lotQtyS # one lot-size total price
    ccassComit = totalPrices*CCASS_COMIT  #HKSEx ccass commission, CCASS_COMIT=0.00002
    commission = totalPrices*BROKER_COMIT  # ib broker commission, BROKER_COMIT=0.001
 
    ccassLot = np.ceil(minCCASS/ccassComit)
    commissionLot = np.ceil(minCommision/commission)

    numOfLot = commissionLot    
    if mode==BROKER_CCASS_BEQ: # pick the max lots among ccass and commssion
        numOfLot=np.maximum(commissionLot, ccassLot); print("Using broker & CCASS commissions for breakeven lot size calculation.")
    else: pass #print("Using ONLY broker commission for breakeven lot size calculation.")
    return np.ceil(numOfLot) #11Jun 2020

def calTotalFees(asset=STK_MODE):
    brokerCommision =(
        BROKER_MIN if (asset ==STK_MODE) else # stock mode
        BROKER_MIN_WAR if (asset ==WAR_MODE) else # warrant mode
        
        BROKER_MIN # default value if cannot match to any MODE
         )
    
    return brokerCommision+CCASS_COMIT

def brkEvenLotSize(prices, lotQtyS, mode, contracts): #auto handle STK/WAR 22mar2021
    """
    Calculate breakeven lot size based on the mode (mode=1 broker comission ONLY ,mode=2 by broker & CCASS)
    :param prices: price Vector Or price Scalar
    :param lotQtyS: one lot-size Vector Or one lot-size Scalar
    :param mode: Default is 1=calculate BreakEven Qty by broker comission ONLY / 2=by broker & CCASS
    :param contracts: asset contracts which has secuirty type information, secType 
    :return: breakeven number-of-lot
    """
    assert len(prices) == len(contracts) == len(lotQtyS), 'Sizes mismatch!'

    minComs=[]
    for c in contracts: #build a min commission vector
        minComs.append(ASSET_MIN_COM[c.secType]) #'STK' = Stock (or ETF), 'WAR' = Warrant (ib_synce sourceCode)

    totalPrices = prices*lotQtyS # one lot-size total price
    ccassComits = totalPrices*CCASS_COMIT  #HKSEx ccass commission, CCASS_COMIT=0.00002
    commissions = totalPrices*BROKER_COMIT  # ib broker commission, BROKER_COMIT=0.001

    # minCCASS = CCASS_MIN    
    ccassLots = np.ceil(CCASS_MIN/ccassComits) #ceiling of input, element-wise.
    # tmp=minComs/commissions #auto element-wise as both are np array.
    commissionLots = np.ceil( minComs/commissions ) #true division, auto element-wise as both are np array.
    # commissionLot = np.ceil(minCommision/commission)

    numOfLot = commissionLots #use values from broker min commission FIRST
    if mode==BROKER_CCASS_BEQ: # pick the max lots among ccass and commssion
        numOfLot=np.maximum(commissionLots, ccassLots); print("Using broker & CCASS commissions for breakeven lot size calculation.")
    else: pass #print("Using ONLY broker commission for breakeven lot size calculation.")
    return numOfLot #22mar2021
    

def amTradingAmountCalculation(csvDf,codeDate): #Calculate all the stocks' morning trading dollar amount(DA): Sum of normalized-price*maxPrice *normalized-volumn*maxVolumn.
    sliceTimeEnd=getDetaConfig()[1]
    # 4Jun2020,  Dave output DENORMALIZED prices&volums by multipy their Max Values already
    vol=csvDf[LABEL_VOL][csvDf[STOCK_CODEDATE]==codeDate].iloc[0:sliceTimeEnd]
    price=csvDf[LABEL_PRICE][csvDf[STOCK_CODEDATE]==codeDate].iloc[0:sliceTimeEnd] 
    amTradingDollarAmount=np.dot(vol, price) # np.dot()=np.multiply(vol, price).sum()
    return amTradingDollarAmount

def dropNonHkdSec(inDataFrame): # drop all Non HKD SEHK securities.
    """
    Drop all stocks/ assets which are not traded in HKD (e.g. RMB & USD)
    :param inDataFrame: input dataframe
    :return: modified dataframe
    """
    for start, stop in [(80000,89999), (9000,9199), (9800,9849), (9200,9399), (9500,9599)]: #https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Stock-Code-Allocation-Plan/scap.pdf
        indexNames = inDataFrame[ (inDataFrame['Code'] >= start) & (inDataFrame['Code'] <= stop) ].index #RMB
        inDataFrame.drop(indexNames , inplace=True)
    print('Dropped all Non-HKD SEHK securities.')
    return inDataFrame
    
def fitSaveStyleFrame(rawDataFrame, fitTuple, sortKey, fileName): #need: import xlsxwriter; from styleframe import StyleFrame
    """
    Format a dataframe and save into a formated Excel file
    :param rawDataFrame: dataframe to be formatted
    :param fitTuple: list column names to be width fitted
    :param sortKey: sort the Excel table base on this column name
    :param fileName: the Excel filename to save as
    :return: None
    """
    temp=rawDataFrame.copy(deep=True) #Make Sure a copy before reset index
    temp.reset_index(inplace=True) #A10,fix StyleFrame bug 16jun2020:'numpy.ndarray' object has no attribute 'style'
    if sortKey !=None: temp=temp.sort_values(by=[sortKey],ascending=False) #Sort the DAs from high to low. Only top few stocks will buy
    # temp=temp.sort_values(by=[sortKey],ascending=False) #Sort the DAs from high to low. Only top few stocks will buy

    styledFrame=StyleFrame(temp) #to styled DataFrame
    excelWrite = StyleFrame.ExcelWriter(fileName) # Use ExcelWrite write into disk
    styledFrame.to_excel( excelWrite, best_fit=fitTuple ) #A3, formatting
    excelWrite.save() # actual save to disk

def checkTestMaxRoi(testMaxRoi, scaleUp): #check and then modify scaleUp-factor during black-swan period
    """
    Base on weekly ROI, return on investment, to adjust scaleUp factor for buy lotsize as part of risk management
    :param testMaxRoi: weekly ROI
    :param scaleUp: weak break-even lotsizes scaling up factor
    :return: adjusted scaling factor
    """
    if testMaxRoi <=0.0001: #0=>0.001,30aug2020. (0 better than 1! as limited budget limit lost,14jun2020H). -ve/~zero ROI during gap-ratio parameters searching 2-days
        # scaleUp=max(np.floor( scaleUp/S_FACTOR ), 1) # if testMaxRoi=-ve, /S_FACTOR which is default numOfLot size without scaleUp. min=1,30aug2020
        scaleUp=1 # if testMaxRoi=-ve, no scaleUp. 18dec2020
        message='Market is unpredictable, trade with care! '+"{:.2%}".format(testMaxRoi)
    elif 0 < testMaxRoi <= 0.02: #2% bi-daily, 1% per day
        message='Market is not very predictable but looking fine. '+"{:.2%}".format(testMaxRoi)
    else: message='Market looks very predictable, trade with confidence. '+"{:.2%}".format(testMaxRoi)
        
    return scaleUp, message

def setTargetRunDateTime(startHour, startMin, exchange):
    """
    Set next day to run the auto day trade function. Skip Sat, Sun, holidays etc...
    :param startHour: Target hour to start
    :param startMin: Targt min to start
    :param exchange: Stock Exchange Symbol
    :return: The targeted date (if time passed, it will be next available trade day of the Exchange
    """
    now=datetime.now(); print("Now is:", now.strftime('%Y-%b-%d %H:%M'), "(HK Time only!)") #A12,get&print current time
    waitUntilStart=now.replace(hour=startHour, minute=startMin, second=0, microsecond=0) #A4, replace to target runtime
    if waitUntilStart > now:
        print("Run when", waitUntilStart.strftime('%Y-%b-%d %H:%M'), "(HK Time) at ", exchange, ". Go sleep now.....\n") #format: '2020-Jun-16':%Y-%b-%d'
    else:
        print("Invalid: The target run-time passed !!!")
        waitUntilStart += timedelta(days=1) # increment one day to run
        #while waitUntilStart.weekday() >4: #A13. check > Fri(4).
        while not checkIsTradeDay(waitUntilStart, exchange=exchange, halfDay=False): # yyyy-mm-dd, e.g. 2020-07-02. Cut half-day trade days
            waitUntilStart += timedelta(days=1) # inc 1day if not a valid tradeday, Sat&Sun are non-trade days by default

        print("Incremented to", waitUntilStart.strftime('%Y-%b-%d %H:%M'), "(assume HKT). Go sleep now...")
        emailAdmin('Next trade day is coming(HKT):'+ waitUntilStart.strftime('%A')+'. '+ waitUntilStart.strftime('%Y-%b-%d'),
                   'From:'+sys.argv[0])
    return waitUntilStart

def checkIsTradeDay(dateTimeBeChecked, exchange='SEHK', halfDay=True): # yyyymmdd=e.g. '2020-07-02'. Ret True if a valid trade-day
    """
    Check whether the input data is the corresponding exchange's valid trading date
    :param dateTimeBeChecked: datetime object for checking is valid trade day or not.
    :param exchange: exchange's symbol
    :param halfDay: True to keep half day trade days as valid trading days
    :return: True if a valid trade day, else return False
    """
    if exchange=='SEHK': # HK Exchange
        url='https://www.hkex.com.hk/-/media/HKEX-Market/Mutual-Market/Stock-Connect/Reference-Materials/Trading-Hour,-Trading-and-Settlement-Calendar/'
        currentTradingCalendar=str(dateTimeBeChecked.year)+'-Calendar_csv_e.csv' #get current year 'yyyy', fix bug 30dec2020
  
        try:
            tradingCalendar=pd.read_csv(currentTradingCalendar) # check latest ver exist in current directory or not
            print('Using local-disk SEHK trading calendar file in current directory:'+currentTradingCalendar)
        except BaseException as e:
            print(e); print("Error in getting latest trade day calendar:", currentTradingCalendar,
                  'from current working directory. Downloading from:', exchange,' ......')
            try:
                # fullPath=os.path.normpath( os.path.join(url, currentTradingCalendar) ) CAN'T use normpath, 30dec2020
                # tradingCalendar= pd.read_csv(fullPath+currentTradingCalendar,skiprows=2)              
                tradingCalendar= pd.read_csv(url+currentTradingCalendar,skiprows=2) #skip the first 2 title rows
                tradingCalendar.to_csv(currentTradingCalendar,index=False) #save without index into current working directory
            except BaseException as e:
                print(e);  msg=f"Error in downdload {currentTradingCalendar} or saving the file, program terminated !!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                print(msg)
                emailAdmin(msg, '  From:'+sys.argv[0])
                sys.exit(msg) # terminate the program
                
    elif exchange=='LSE' or 'NYSE': # London or other exchange in future
        sys.exit(f"Not support this, {exchange}, market yet.") # terminate the program with the error msg.
     
# =============================================================================
#     tradingCalendar=tradingCalendar[tradingCalendar["Hong Kong"]!="Holiday"]["Date"] #exlcude holiday, not include blank and half day
    tradingCalendar.drop(tradingCalendar[tradingCalendar['Hong Kong']=="Holiday"].index, inplace = True) #exlcude holiday
    if not halfDay: # further cut morning only trade day
        tradingCalendar.drop(tradingCalendar[tradingCalendar['Hong Kong']=="Half Day"].index, inplace = True) #exclude half-day if halfDay=False,25dec2020
    tradingCalendar=tradingCalendar["Date"] 
# =============================================================================

    yyyymmdd=dateTimeBeChecked.strftime('%Y-%m-%d')
    return not (tradingCalendar[tradingCalendar==yyyymmdd].empty) # True if a valid trade day

def profitDf2IntCode(profitDf): # get stockcode as a list of integers
    """
    Extract stock/ asset code from the input dataframe
    :param profitDf: the dataframe
    :return: list of integers which are the stock/ asset codes
    """
    if len(profitDf) >0: #have something
        codeDateDf=pd.DataFrame(columns=[STOCK_CODEDATE]); codeDateDf[STOCK_CODEDATE]=profitDf.index
        codeDateDf[['Code', 'Date']]=codeDateDf[STOCK_CODEDATE].str.split('_', expand=True)# split to 2 column, Col0:stock-code, Col1:lotsize
        codeIntList=[int(i) for i in codeDateDf['Code'].to_list()] #gen profitable-stock codes int list.
    else: codeIntList=None
    
    return codeIntList

def stockVsOthersAdjPriceIncII(todayPickDf, columns=[BUY_PRICE, STOP_PRICE, SELL_PRICE]): #The input Df MUST has the column C_SEHK (分類), SELL/STOP/BUY_PRICE
    """
    Base on the asset's type(Stock-ETF-REIT), adjust it's price to match SEHK rules
    :param todayPickDf: Deta's standard dataframe
            columns: list of df col to be processed,e.g. ['buy price', 'example']
    :return: adjusted todayPickDf dataframe
    """
    tmp =todayPickDf.copy(deep=True) #deepCopy to avoid warning, 23feb2021
    groupedDf=tmp.groupby(tmp.分類) #C_SEHK
    ## Handle stock, ETF and Reit
    print('Handling Stock-ETF-REIT ticker price diff inc issues.')
    try:
        todayStock=groupedDf.get_group(C_STOCK) #A17,following args must have ',' after first arguments. Use .loc fix warningsettingWithCopyWarning.
        for c in columns:
            todayStock.loc[:, c]=todayStock.loc[:, c].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)

    except KeyError:
        print('No '+C_STOCK+' class security'); todayStock=pd.DataFrame() # avoid concat error
        
    try:
        todayETF=groupedDf.get_group(C_ETF) # ETF, Stock or REIT    
        for c in columns:
            todayStock.loc[:, c]=todayStock.loc[:, c].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
    except KeyError:
        print('No '+C_ETF+' class security'); todayETF=pd.DataFrame() # avoid concat error

    try:
        todayReit=groupedDf.get_group(C_REIT)   
        for c in columns:
            todayStock.loc[:, c]=todayStock.loc[:, c].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
    except KeyError:
        print('No '+C_REIT+' class security'); todayReit=pd.DataFrame() # avoid concat error

    try:
        todayWar=groupedDf.get_group(C_WAR)   
        for c in columns:
            todayStock.loc[:, c]=todayStock.loc[:, c].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
    except KeyError:
        print('No '+C_WAR+' class security'); todayReit=pd.DataFrame() # avoid concat error

    return pd.concat([todayStock, todayReit, todayETF, todayWar]) #A13, default:axis=0 => vertical concat


# ### For bracket orders' limit-buy/sell, stop-sell ONLY.
# def stockVsOthersAdjPriceInc(todayPickDf): #The input Df MUST has the column C_SEHK (分類), SELL/STOP/BUY_PRICE
#     """
#     Base on the asset's type(Stock-ETF-REIT), adjust it's price to match SEHK rules
#     :param todayPickDf: Deta's standard dataframe
#     :return: adjusted todayPickDf dataframe
#     """
#     tmp =todayPickDf.copy(deep=True) #deepCopy to avoid warning, 23feb2021
#     groupedDf=tmp.groupby(tmp.分類) #C_SEHK
#     ## Handle stock, ETF and Reit
#     print('Handling Stock-ETF-REIT ticker price diff inc issues.')
#     try:
#         todayStock=groupedDf.get_group(C_STOCK) #A17,following args must have ',' after first arguments. Use .loc fix warningsettingWithCopyWarning.
#         todayStock.loc[:, BUY_PRICE]=todayStock.loc[:, BUY_PRICE].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
#         todayStock.loc[:, STOP_PRICE]=todayStock.loc[:, STOP_PRICE].apply(sehkTickRoundPrice, args=('sell',)) #Not Fn(), Fn ONLY
#         todayStock.loc[:, SELL_PRICE]=todayStock.loc[:, SELL_PRICE].apply(sehkTickRoundPrice, args=('sell',)) # A13
#     except KeyError:
#         print('No '+C_STOCK+' class security'); todayStock=pd.DataFrame() # avoid concat error
        
#     try:
#         todayETF=groupedDf.get_group(C_ETF) # ETF, Stock or REIT    
#         todayETF.loc[:, BUY_PRICE]=todayETF.loc[:, BUY_PRICE].apply(sehkETFtickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
#         todayETF.loc[:, STOP_PRICE]=todayETF.loc[:, STOP_PRICE].apply(sehkETFtickRoundPrice, args=('sell',)) #Not Fn(), Fn ONLY
#         todayETF.loc[:, SELL_PRICE]=todayETF.loc[:, SELL_PRICE].apply(sehkETFtickRoundPrice, args=('sell',)) # A13
#     except KeyError:
#         print('No '+C_ETF+' class security'); todayETF=pd.DataFrame() # avoid concat error

#     try:
#         todayReit=groupedDf.get_group(C_REIT)   
#         todayReit.loc[:, BUY_PRICE]=todayReit.loc[:, BUY_PRICE].apply(sehkTickRoundPrice, args=('buy',)) #tick adjust&round,18jul2020. Instead round(x,2)
#         todayReit.loc[:, STOP_PRICE]=todayReit.loc[:, STOP_PRICE].apply(sehkTickRoundPrice, args=('sell',)) #Not Fn(), Fn ONLY
#         todayReit.loc[:, SELL_PRICE]=todayReit.loc[:, SELL_PRICE].apply(sehkTickRoundPrice, args=('sell',)) # A13
#     except KeyError:
#         print('No '+C_REIT+' class security'); todayReit=pd.DataFrame() # avoid concat error

#     return pd.concat([todayStock, todayReit, todayETF]) #A13, default:axis=0 => vertical concat


#ses.reqMarketRule(session.reqContractDetails(contracts[0])[0].marketRuleIds)
def getSehkTickSize(price: float): # for STK- REIT- warrant
    """
    Get stock(same for REIT&Warrant) price increment tick-size based on SEHK rule
    :param price: the asset market price
    :return: size of the price increment
    Ref: Price Range            Tick Size
    From 0.01 to 0.25	        0.001
    Over 0.25 to 0.50	        0.005
    Over 0.50 to 10.00	        0.010
     Over 10.00 to 20.00	    0.020
     Over 20.00 to 100.00	    0.050
     Over 100.00 to 200.00	    0.100
    Over 200.00 to 500.00	    0.200
    Over 500.00 to 1,000.00	    0.500
    Over 1,000.00 to 2,000.00	1.000
    Over 2,000.00 to 5,000.00	2.000
    Over 5,000.00 to 9,995.00	5.000 """
    
    if 10.0 <= price <200: #1st check for most common price ranges
        if 10.0 <= price <20: #use chained comparsion,17aug2020
            size=0.02 #2 cmp & 1 memory moves,24jul2020
        elif 20.0 <= price <100:
            size=0.05 #4 cmp & 1 memory moves,24jul2020
        elif 100.0 <= price <200:
            size=0.1 #6 cmp & 1 memory moves,24jul2020             
 
    elif price <10 or price >=200:  # 2nd check for less common Groups
        # GROUP 2
        if 0.50 <= price <10.00: #check less two-most uncommon
            size=0.010
        elif 200.00 <= price <500.00: 
            size=0.200
        elif 0.25 <= price <0.50:  #check two UNcommon following
            size=0.005  
        elif 500.00 <= price <1000.00:
            size=0.500
        elif 0.01 <= price <0.25: 
            size=SMALLEST_SEHK_STK #0.001  
        elif 1000.0 <= price <2000.00: # following 3, do not happen normally
            size=1.000          
        elif 2000.0 <= price <5000.0: 
            size=2.000
        elif 5000.0 <= price <9995.00:
            size=5.000
        elif price >= 9995.00: # worst case
            size=5.000
        elif price < 0.01: # worst case
            msg=f'Asset price <HKD0.01, warning! Set ticker-size={SMALLEST_SEHK_STK} to avoid hault the whole program!'
            print(msg); emailAdmin(msg, '  From:'+sys.argv[0])
            size=SMALLEST_SEHK_STK
            
            
    return size

def getSehkETFtickSize(price: float):# for ETF only
    """
    Get ETF price increment tick-size based on SEHK rule
    :param price: the ETF asset market price
    :return: size of the price increment

    Ref:lowEdge=0.0, increment=0.001
        lowEdge=1.0, increment=0.002
        lowEdge=5.0, increment=0.005
        lowEdge=10.0, increment=0.01
        lowEdge=20.0, increment=0.02
        lowEdge=100.0, increment=0.05
        lowEdge=200.0, increment=0.1
        lowEdge=500.0, increment=0.2
        lowEdge=1000.0, increment=0.5
        lowEdge=2000.0, increment=1.0  """
    
    size=SMALLEST_SEHK_ETF #0.001, worst if price very close to zero
    if SMALLEST_SEHK_ETF <= price <1.0:
        size=SMALLEST_SEHK_ETF #0.001
    elif 1.0 <= price <5.0: 
        size=0.002
    elif 0.5 <= price <10.0:
        size=0.005  
    elif 10.00 <= price <20.00:
        size=0.01
    elif 20.0 <= price <100.0: 
        size=0.02  
    elif 100.00 <= price <200.00:
        size=0.05          
    elif 200.0 <= price <500.0: 
        size=0.1
    elif 500.0 <= price <1000.00:
        size=0.2
    elif 1000.0 <= price <2000.00:
        size=0.5    
    elif price >=2000.0:
        size=1.0          
    elif price < SMALLEST_SEHK_ETF:
        msg='ETF asset price very small, warning! Set ticker-size=0.0000001 to avoid hault the whole program!'
        print(msg); emailAdmin(msg, '  From:'+sys.argv[0])
        size=0.0000001
    
    return size
""" COULD USE following syntax:
size = ('foo' if (x > 1) else
      'bar' if (x > 2) else
      'baz' if (x > 3) else
      'qux' if (x > 4) else
      'quux'
     )
"""

def incDecSehk(price, mode='INC', count=1):
    mode=mode.upper() #force to upper for compare
    assert mode in ['INC', 'DEC'], 'Invalid mode'
    
    for count in list(range(count)): #default do 1 time with count=1
        if mode=='INC':
            price +=getSehkTickSize(price)
        elif mode=='DEC':
            price -=getSehkTickSize(price)
    
    return price

def incDecSehkETF(price, mode='INC', count=1):
    mode=mode.upper() #force to upper for compare
    assert mode in ['INC', 'DEC'], 'Invalid mode'
    
    for count in list(range(count)): #default do 1 time with count=1        
        if mode=='INC':
            price +=getSehkETFtickSize(price)
        elif mode=='DEC':
            price -=getSehkETFtickSize(price)
    
    return price

def getDelayFrozenPrice(contracts, ses):
    """
    Get 15-20mins delayed price from IB. https://interactivebrokers.github.io/tws-api/market_data_type.html
    :param contracts: contract of the stock/asset
    :param ses: IB connect session handler
    :return: list of the prices
    Ref: https://interactivebrokers.github.io/tws-api/tick_types.html
    """
    ses.reqMarketDataType(4)  # 4=delay-frozen, no subscrition required. 1-live,2-frozen,3-delay,4-delayFrozen, https://interactivebrokers.github.io/tws-api/market_data_type.html
    tickers=[] # ib_insync ticker objects
    for contract in contracts:
        tickers.append(ses.reqMktData(contract, snapshot=True).marketPrice() ) # .marketPrice() ret: bid-ask => mid-point => close prices
    return tickers

def priceTrunc(size, price, action: str):
    """
    Truncate and adjust the price to fit the price increment tick price
    :param size: tick size for that price range
    :param price: the price
    :param action: BUY or SELL action
    :return: the adjusted price
    """
    action=action.upper() #force to upper for compare
    assert action=='BUY' or action=='SELL', 'Trade action not buy nor sell, error!'
    # compensate = 2 * size if action=='BUY' else -2*size # buy a bit higher for easy limitBuy price < X. sell a bit lower for easy limitSell price > X
    compensate = size if action=='BUY' else -size # buy a bit higher for easy limitBuy price < X. sell a bit lower for easy limitSell price > X
        
    if size<1: # int(X.y), cut y to X.0
        adjPrice=int(price)+((price-int(price))//size)*size +compensate    
    else: adjPrice=(price//size)*size +compensate # add back compensate, should be a bug. 2Dec2020
    
    assert adjPrice >0 , 'Error: priceInc adjusted ticker price is -ve' #check only non-negative price is returned
    return adjPrice

def sehkTickRoundPrice(price: float, action: str): #for STK- REIT- warrant
    """
    Adjust the asset input price to fit it's price increment size
    :param price: the price
    :param action: BUY or SELL
    :return: the adjusted price
    """
    size=getSehkTickSize(price) #size is price step size, e.g.0.01, 0.1, 0.5 etc.
    return priceTrunc(size, price, action)

def sehkETFtickRoundPrice(price: float, action: str): # for ETF only
    """
    Adjust the ETF price to fit it's price increment size
    :param price: the price
    :param action: BUY or SELL
    :return: the adjusted price
    """
    size=getSehkETFtickSize(price) #size is price step size, ETF: 0.01, 0.05, 0.2 etc.
    return priceTrunc(size, price, action)

def sehkOPTtickRoundPrice(price: float, action: str): # for Option only
    """
    Adjust the option price to fit it's price increment size
    :param price: the price
    :param action: BUY or SELL
    :return: the adjusted price
    """
    size=0.01 #e.g. https://contract.ibkr.info/v3.10/index.php?action=Details&site=GEN&conid=381417997
    return priceTrunc(size, price, action)

# def roundAssetPrice(price:float, contract, action: str, ses):
#     """
#     Slower than sehkETFtickRoundPrice() and sehkOPTtickRoundPrice() but
#       independent of exchanges and follow exchanges rule when the rule changes
#     Adjust the asset input price to fit it's price increment size

#     :param price: the price
#     :param contract: contract for trade
#     :param action: BUY or SELL
#     :param ses: IB connected session's handler
#     :return: the adjusted price

#     HK e.g.: Price Range            Tick Size
#         From 0.01 to 0.25	        0.001
#         Over 0.25 to 0.50	        0.005
#         Over 0.50 to 10.00	        0.010
        
#     IB's list format: 
#             priceIncrements[ [lowEdge=0.0, increment=0.001],
#                              [lowEdge=1.0, increment=0.002],
#                              [lowEdge=5.0, increment=0.005] ]
#     """
#     priceIncrements=ses.reqMarketRule(ses.reqContractDetails(contract.marketRuleIds) )
    
#     size=priceIncrements[0].lowEdge # init as lowest tick-size for just-in-case "=<" the lowest lowEdge
#     for inc in priceIncrements:
#         if price > inc.lowEdge:
#             size=inc.increment # replace if > the lowEdge
          
#     return priceTrunc(size, price, action)

class Gateway(object):
    """  Call 'ibgateway.exe', need manual login. Set IB gateway with auto restart instead login to avoid closed EVERYDAY,17sep2020
    dt.Gateway(ver='978').run(), dt.Gateway().stop()
    """
    def __init__(self, ver='978', directoryPath: str = 'C:\\Jts\\ibgateway\\'):  # A7, self meanings
        self.exePath = os.path.normpath(os.path.join(directoryPath, ver))
        self.subProcess=0
        print('ibgateway.exe MUST in the folder:', self.exePath)

    def run(self):
        destination = os.path.normpath(os.path.join(self.exePath, 'ibgateway.exe'))
        print('Connecting gateWay directly .....')
        # os.system(destination)
        self.subProcess = spro.Popen([destination])
        print('RECONFIGED new paper account settings, if the account is new?')
        input('Press any key FEW times, after login Gateway successfully, until see the Python running.')

    def stop(self):
        self.subProcess.terminate()
        print('Terminated the ibgateway.exe file')

def connectIB(pNB=7496): #Ibridge said xx96 SAME for both live&paper account in IB-gateway&TWS,Jun2020. IBC used 7462!!
    """
    Connect to IB server with retries
    :param pNB: default as 7496 which must same at the API setting in TWS/Gateway
    :return: the connected session handler
    """
    # if AUTO_BY_IBC: IbcGateway().run()

    maxTry=2050 # 2050 times (>>15mins) that should longer than paperMode maintainence period, remotely 26jan2021.
    for attempts in range(maxTry): #creat [0,30]
        try:
            session=ibs.IB(); session.connect(port=pNB, timeout=3) #creat IB object session & connect to IB server
        except Exception as e:
            print(e)
            if attempts%25==0: emailAdmin(f'Login IB failed:{attempts} times, maybe ibgateway problem. Check EC2 or else!!', '  From:'+sys.argv[0])
            continue # continue the loop to next attempt.
        break # break the loop immediately.

    if session.isConnected():
    # if attempts < maxTry:
        print("!!! Connected to IB server is:", session.isConnected(), ' at:', attempts+1, ' trys' )
        
    else:
        print("!!!!!!!!! Login IB fail more than 2050 times!!!!!!!!!!!!!!")
        emailAdmin("Bad error when Login IB !!, check EC2 ASAP, will terminate the programe immediately !!", '  From:'+sys.argv[0])
        emailAdmin("Bad error when Login IB !!, check EC2 ASAP, will terminate the programe immediately !!", '  From:'+sys.argv[0])
        emailAdmin("Bad error when Login IB !!, check EC2 ASAP, will terminate the programe immediately !!", '  From:'+sys.argv[0])        
        sys.exit('Terminating the program !') # terminate the program with the error msg, 25jan2020

    print('Max subAccounts per account:', session.MaxSyncedSubAccounts, '. All accounts are:', session.managedAccounts())
    return session

def disconnectIB(ses):
    ses.disconnect()
    # if AUTO_BY_IBC: IbcGateway().stop()

def errHandlerIB(reqId, errorCode, errorString, contract):
    """
    Usage: ses.errorEvent += errHandlerIB 
        # operator overload. Add connect method's function, in event kit Not insync.
    Parameters:  IB in_synce evenEvent's parameter
    """
    print(f" ErrorEvent Id:Code:Msg- {reqId}: {errorCode}: {errorString}: {contract}")  

### ALL following functions' input-VARIABLES are vectors(list) and handled by vector operators, list.
    ### Create&Qualify stock contract
def creatQliTradeContracts(assets: list, ses, exchanges: str='SEHK', currency: str='HKD', secType='STK'): #what exchange's assets to buy
    """
    https://interactivebrokers.github.io/tws-api/basic_contracts.html#warrant  ,7jan2022
    Creat the trades' contracts and auto qualify the contract
    :param assets: list of assets. STK is symbol
            WAR is list of tuple (warrant code name,
                                  underlying stock symbol,
                                  lastTradeDateOrContractMonth, eg = "20190621",
                                  strike, e.g. = 7.5,
                                  right, e.g. = "C"
                                  multiplier, e.g. = "100"  # 1/(conversion ratio, 換股比率)
                                  )

    :param ses: connected IB server session handler
    :param exchanges: Stock exhange's symbol
    :param currency: prices' currency
    :param secType: type of the security
    :return: the contracts for placeOrder() order placing to IB

    Ref: 'STK': Stock,'OPT': Option,'FUT': Future,'CONTFUT': ContFuture,'CASH': Forex,'IND': Index,
            'CFD': CFD, 'BOND': Bond, 'CMDTY': Commodity, 'FOP': FuturesOption, 'FUND': MutualFund,
            'WAR': Warrant, 'IOPT': Warrant, 'BAG': Bag, 'NEWS': Contract """

    # WAR_CODE_NAME, UNDERLY_SYM, LAST_T_YDM, STRIKE, RIGHT, MULTIP=0,1,2,3,4,5 # warrant full definition, '_' is the useless underlying stock symbol
    
    if secType=='STK': #stock
        contracts=[ibs.Stock(s, exchanges, currency) for s in assets] # specify a trading contract. '1'=CK Hutchison Holdings Ltd
    elif secType=='WAR': #warrant
        assert len(assets[0]) == 6, 'Invalid size of warrant asset attributes.' # 3 random checks by assert, 2jan2022
        assert isinstance(assets[0][LAST_T_YDM], str), 'Wrong data format of last trade day/month.'
        assert isinstance(assets[-1][MULTIP], float) or isinstance(assets[-1][MULTIP], int), 'Must float or int!'
        contracts=[ibs.Warrant( #https://interactivebrokers.github.io/tws-api/basic_contracts.html#warrant  ,2jan2022. 
                                symbol = UNDERLY_SYM,
                                localSymbol=s[WAR_CODE_NAME], #HKEx's unique warrant symbol code
                                lastTradeDateOrContractMonth =s[LAST_T_YDM], # YYYYMM DD
                                strike =s[STRIKE], #7.5,
                                right  =s[RIGHT], #"C",
                                multiplier =s[MULTIP], # 1/(conversion ratio, 換股比率)
                                exchange=exchanges, currency=currency,
                                # tradingClass=s[NAME], 
                                ) for s in assets] # localSym MUST be defined for WAR, debug17aug2020      
    #     contracts=[ibs.Warrant(localSymbol=s, exchange=exchanges, currency=currency) for s in assets] # localSym MUST be defined for WAR, debug17aug2020
    else: sys.exit('Not yet support this security type yet !!!')

            #### qualifyContracts() Create conId. check & auto fill-in missing datas etc..            
    map(lambda c: ses.qualifyContracts(c), contracts) #qualify In-Place modify contract&return is NOT the contracts,23jul2020
    return contracts


def creatBracketOrders(quantities: list, lBuyP: list, lSellP:list, stopSellP:list, ses): #how bracket oder look like
    """
    Creat bracket orders
    :param quantities: list of trading quantity
    :param lBuyP: list of limit buy price
    :param lSellP: list of limit sell price
    :param stopSellP: list of stop sell price (mdd, Max Drawn Down)
    :param ses: IB server connected session handler
    :return: list of bracket order list (a bracket has 3 orders as a sublist)
    """
    assert all( length==len(quantities) for length in [len(lBuyP), len(lSellP),len(stopSellP)] ), 'Input valuables(q,bP,sP,StopP) size misMatchs!'
    
    bOrders=list( # Each stocks has 3 orders. Buy, Sell, Sell
    map(lambda q,bP,sP,tP:ses.bracketOrder(action='BUY', quantity=q, limitPrice=bP, takeProfitPrice=sP, stopLossPrice=tP),
                        quantities,lBuyP,lSellP,stopSellP
        )
                  ) #A4,5
    return bOrders

def placeBracketOrders(contracts: list, bOrders: list, investments:list,
                      invLimit, ses):  # each stock has a specific contract, say lot-size, currency, exchange etc..
    """ Place Bracket Orders, will skip too big investment in a single stock,
        others stocks will be placed as much as possible in margin mode
        Parameters: contracts= contractList
        bOrders = Blank Orders List for targeting orders to be placed.
        investments=investment amount of each buyLimit order in bOrders
        invLimit= today starting investment fund accumulated up to now.
        ses=IB server connection handler 
        Returns: bTrades=Trade List. bOrdersNew, investmentsNew=updated Orders & investment-amounts List from placed order, 
        Ref: IB confirmed deduct account money ONCE after order PLACED. 13aug2020  """
    bTrades=[]; bOrdersNew=[]; investmentsNew=[] #; invested=0
    stockIx=list( range(len(contracts)) )
    for s in stockIx: # PlaceOrders: interate through stocks index in stockIx
        sym=contracts[s].localSymbol
# =============================================================================        
        # if investments[s] < invLimit: # skip,if investment > the day's starting invest limit for just a single stock 20aug2020
        if investments[s] < sys.float_info.max: # == Buy what ever can buy by margin set by IB        
            print('... ...... Ignore todayInvestLimt, 13jan2021, stop by IB margin limit instead !!!!!') #13jan2021
# =============================================================================
            temp=list( map(lambda o:ses.placeOrder(contracts[s], bOrders[s][o]), #place as much bOrders as possible, will cancel at main())
                    [BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX]) ) # interate 3 blanket order types wrt fixed index 0,1,2
            bTrades.append(temp)
            bOrdersNew.append(bOrders[s]); investmentsNew.append(investments[s])  #valid order&investment index CHANGED here.
            # invested +=investments[s]
            ses.sleep(IB_DELAY*3) #3trades/bracket-order, Max 50msg/s

        else: print(f'ONLY this Asset:{sym} is already over {invLimit}, skipped.')
    
    assert len(bTrades)==len(bOrdersNew), 'No of trades&order are not match!' #double check new bOrders is right.
    print(f'No of bracket orders JUST placed:{len(bOrdersNew)}') # 3 orders per bracket
    return bTrades, bOrdersNew, investmentsNew # placed trades and updated orders lists


def placeMktOrders(contracts: list, mOrders: list, invLimit, ses):  # each stock has a specific contract, say lot-size, currency, exchange etc..
    """ Place Market Orders
        others stocks will be placed as much as possible in margin mode
        Parameters: contracts= contractList
        mOrders = Orders List for targeting orders to be placed.
        ses=IB server connection handler 
        Returns: mTrades=Trade List.
        Ref: IB confirmed deduct account money ONCE after order PLACED. 13aug2020  """
    
    mTrades=[]; mOrdersNew=[]
    for contract, order in zip(contracts, mOrders): #use loop instead map for debug
        temp = ses.placeOrder(contract, order)
        if temp: # if placed order success
            mTrades.append(temp)
            mOrdersNew.append(order)
        else: print('placeOrder() fail, should be over budget already.')
        ses.sleep(IB_DELAY)
    
    assert len(mTrades)==len(mOrdersNew), 'No of trades&order are not match!' #double check new bOrders is right.
    print(f'No of Market orders JUST placed:{len(mOrdersNew)}')
    return mTrades, mOrdersNew # placed trades and updated orders lists


def unsoldOrdCancelNplaceMktOrd(bTrades: list, ses):
    """
    Cancel all stocks bought but did'nt sell and still onhand. Replace them by market-sell-orders
    :param bTrades: list of bracket trade list
    :param ses: IB server connection handler
    :return: Market Order Trades to sell all position, cancelled trades
    Ref: ib_insynce (order.py)
        DoneStates: ClassVar = {'ApiCancelled', 'Cancelled', 'Filled'}
        ActiveStates: ClassVar = {'ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted'} """

    print("Check&Cancelling LimitBuy/Sell/Stop Orders states, won't cancel partial-selling orders.")
    SYM=0; IX=1; ST=2 # indexing for SYMbol, running IndeX & STate.    
    boughtNone=[[],[],[]]  #4classes: Did'nt buy yet, Bought-but-unsold, Bought&Sell SoMe, Bought&Sold All.
    boughtOnly=[[],[],[]]; boughtSoldSm=[[],[],[]]; boughtSoldAll=[[],[],[]]
    boughtNoneOcnL=[] #3cancels. OcnL=OrderCancel. !Will not cancel sell some only, let it try to continue sell
    boughtOnlyOcnL=[]; boughtSoldAllOcnL=[]

    stockIx=list(range(len(bTrades)))
    for s in stockIx: # interate through stocks index in stockIx
        cSymbol=bTrades[s][BLIMIT_BUY_IX].contract.localSymbol
        if bTrades[s][BLIMIT_BUY_IX].filled()>0: #bought some. filled()=NoOfShare filled
            if bTrades[s][BLIMIT_SELL_IX].filled() == 0.0: # Not sold. order.totalQuantity - filled()
                boughtOnlyOcnL.append(cancelBracketOrdTree(bTrades[s], BLIMIT_SELL_IX, ses))
                boughtOnly[SYM].append(cSymbol)  #  Bought but not all sold yet
                boughtOnly[IX].append(s); boughtOnly[ST].append('BuyNotSell')
            elif bTrades[s][BLIMIT_SELL_IX].remaining() >0.0: #  Bought but not all sold yet
                ### CAN'nt cancel which would creat incomplete lotize ### 22aug2020#bought, sell some, not sold all
                boughtSoldSm[SYM].append(cSymbol)  
                boughtSoldSm[IX].append(s); boughtSoldSm[ST].append('**Buy &SoldSome**')
            else: # Remaining=0, Bought& ALL sold successfully
                boughtSoldAll[SYM].append(cSymbol)
                boughtSoldAll[IX].append(s); boughtSoldAll[ST].append('Buy &SoldALL')
        else: #Did'nt buy anythings yet, did'nt cancel
            # boughtOnlyOcnL.append(cancelBracketOrdTree(bTrades[s], BLIMIT_BUY_IX, ses)) #OcnL=OrderCancel
            boughtNoneOcnL.append(cancelBracketOrdTree(bTrades[s], BLIMIT_BUY_IX, ses)) #OcnL=OrderCancel, debug:6jan2021
            boughtNone[SYM].append(cSymbol)
            boughtNone[IX].append(s); boughtNone[ST].append('BuyNone Today')

    # Integrate the lists
    symbols=boughtNone[SYM] +boughtOnly[SYM] + boughtSoldSm[SYM]+ boughtSoldAll[SYM]
    indexes=boughtNone[IX] +boughtOnly[IX] + boughtSoldSm[IX]+ boughtSoldAll[IX]
    states=boughtNone[ST] +boughtOnly[ST] +boughtSoldSm[ST]+ boughtSoldAll[ST]

    d={'Symbol':symbols, 'Index':indexes, 'State':states}; cMode='Urgent' #use back 'Urgent' from 'Normal' ,23dec2020
    dict2DfEmailAdm(d, f". Will force-close stocks by '{cMode}' mode market-order.",
                    "Stocks' holding states before replaced by Market sell-orders, except partially sold stocks. From:"+sys.argv[0])
    msg='Replace holding orders by market orders:' #close all unsold in boughtOnly&boughtSoldSm
    mTrades=closePositions(cMode, msg, ses) #close sells at marketPrice with normal urgency only, ret [] or trade List

    boughtNoneOcnL = flatBtradesToTrades(boughtNoneOcnL) # make work with printTradeStatus()
    boughtOnlyOcnL = flatBtradesToTrades(boughtOnlyOcnL); boughtSoldAllOcnL = flatBtradesToTrades(boughtSoldAllOcnL)

    return mTrades, boughtNoneOcnL +boughtOnlyOcnL +boughtSoldAllOcnL #mTrades=[],if did'nt close anything. DO'nt if selling some

def unsoldAttachOrdCancelNplaceMktOrd(threeTradesList: list, ses):
    """ ASSUMED entry market orders are DONE and bought the assets ALREADY, until bracket order may not
    Count and email. Then replace them by urgent market-sell-orders
    :param threeTradesList: list of entry, take-profit & stop-loss trades
    :param ses: IB server connection handler
    :return: Market Order Trades to sell all position, cancelled trades if any
    Ref: ib_insynce (order.py)
        DoneStates: ClassVar = {'ApiCancelled', 'Cancelled', 'Filled'}
        ActiveStates: ClassVar = {'ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted'} """

    print("Check&Cancelling takeProfit&StpLoss Orders, won't cancel partial-selling orders.")
    SYM=0; IX=1; ST=2 # indexing for SYMbol, running IndeX & STate.    
    # boughtNone=[[],[],[]]  
    #3classes: Bought-but-unsold, Bought&Sell SoMe, Bought&Sold All.
    boughtOnly=[[],[],[]]; boughtSoldSm=[[],[],[]]; boughtSoldAll=[[],[],[]]
    # boughtNoneOcnL=[] 
    #3cancels. OcnL=OrderCancel. !Will not cancel sell some only, let it try to continue sell
    boughtOnlyOcnL=[]; boughtSoldAllOcnL=[]

    NO_TAKE=False; NO_STP=False
    stockIx=list(range(len(threeTradesList)))
    for s in stockIx: # interate through stocks index in stockIx
        cSymbol=threeTradesList[s][ENTRY].contract.localSymbol # .localSymbol do'nt exist for HK warrant
        # if threeTradesList[s][ENTRY].filled()>0: #bought some. filled()=NoOfShare filled
        ### CHECK take profit orders
        if threeTradesList[s][TAKE].filled() == 0.0: # Not sold. order.totalQuantity - filled()
            # boughtOnlyOcnL.append(cancelBracketOrdTree(threeTradesList[s], TAKE, ses))
            NO_TAKE=True
            boughtOnly[SYM].append(cSymbol)  #  Bought but not all sold yet
            boughtOnly[IX].append(s); tmp='No Take Profit' #boughtOnly[ST].append('BuyNotTake')
        elif threeTradesList[s][TAKE].remaining() >0.0: #  Bought but not all sold yet
            ### CAN'nt cancel which would creat incomplete lotize ### 22aug2020#bought, sell some, not sold all
            boughtSoldSm[SYM].append(cSymbol)  
            boughtSoldSm[IX].append(s); tmp='**TakeSome**' #boughtSoldSm[ST].append('**Buy &TakeSome**')
        else: # Remaining=0, Bought& ALL sold successfully
            boughtSoldAll[SYM].append(cSymbol)
            boughtSoldAll[IX].append(s); tmp='TakeALL' #boughtSoldAll[ST].append('Buy &TakeALL')   
                  
        ### CHECK stop loss orders
        if threeTradesList[s][STOP].filled() == 0.0: # Not sold. order.totalQuantity - filled()
            # boughtOnlyOcnL.append(cancelBracketOrdTree(threeTradesList[s], TAKE, ses))
            NO_STP=True
            boughtOnly[SYM].append(cSymbol)  #  Bought but not all sold yet
            boughtOnly[IX].append(s); tmp +=' No Stop Loss'                
        elif threeTradesList[s][STOP].remaining() >0.0: #  Bought but not all sold yet
            ### CAN'nt cancel which would creat incomplete lotize ### 22aug2020#bought, sell some, not sold all
            boughtSoldSm[SYM].append(cSymbol)  
            boughtSoldSm[IX].append(s); tmp +='**StopSome**' #boughtSoldSm[ST].append('**Buy &TakeSome**')                
        else: # Remaining=0, Bought& ALL sold successfully
            boughtSoldAll[SYM].append(cSymbol)
            boughtSoldAll[IX].append(s); tmp +='StopALL' #boughtSoldAll[ST].append('Buy &StpALL')
 
        boughtOnly[ST].append(tmp)
        if NO_TAKE & NO_STP: boughtOnlyOcnL.append(cancelBracketOrdTree(threeTradesList[s], TAKE, ses))

    # Integrate the lists
    symbols=boughtOnly[SYM] + boughtSoldSm[SYM]+ boughtSoldAll[SYM] # +boughtNone[SYM]
    indexes=boughtOnly[IX] + boughtSoldSm[IX]+ boughtSoldAll[IX] # +boughtNone[IX]
    states=boughtOnly[ST] +boughtSoldSm[ST]+ boughtSoldAll[ST]  # +oughtNone[ST]

    d={'Symbol':symbols, 'Index':indexes, 'State':states}; cMode='Urgent' #use back 'Urgent' from 'Normal' ,23dec2020
    dict2DfEmailAdm(d, f". Will force-close assets by '{cMode}' mode market-order.",
                    "assets' holding states before replaced by Market sell-orders, except partially sold stocks. From:"+sys.argv[0])
    msg='Replace holding orders by market orders:' #close all unsold in boughtOnly&boughtSoldSm
    mTrades=closePositions(cMode, msg, ses) #close sells at marketPrice with normal urgency only, ret [] or trade List

    # boughtNoneOcnL = flatBtradesToTrades(boughtNoneOcnL) # make work with printTradeStatus()
    boughtOnlyOcnL = flatBtradesToTrades(boughtOnlyOcnL); boughtSoldAllOcnL = flatBtradesToTrades(boughtSoldAllOcnL)

    return mTrades, boughtOnlyOcnL +boughtSoldAllOcnL #+boughtNoneOcnL #mTrades=[],if did'nt close anything. DO'nt if selling some

def flatBtradesToTrades(bTrades: list):
    """
    Flatten a list of bracket trades. e.g. [[a,b,c], [d,e,f]]=>[a,b,c,d,e,f]
    :param bTrades: list of list
    :return: flattened list
    """
    flatList = []
    # flatList = [item for elem in bTrades for item in elem] #https://thispointer.com/python-convert-list-of-lists-or-nested-list-to-flat-list/
    for elem in bTrades:
        for item in elem:
            flatList.append(item)

    return flatList

def cancelBracketOrdTree(bTrade: list, orderType: int, ses): #BUY_IX=0 is top of the tree
    """ Cancel a bracket order in a ncessary sequence
    :param bTrade: The bracket order's trade object defined by ib_insynce
    :param orderType: either one of BLIMIT_BUY_IX ,BLIMIT_SELL_IX ,BSTOP_SELL_IX
    :param ses: the session connecting to IB's server
    :return flattened cancelled trades
    Reference https://interactivebrokers.github.io/tws-api/order_limitations.html
    """
    assert orderType in [BLIMIT_BUY_IX ,BLIMIT_SELL_IX ,BSTOP_SELL_IX], 'Invalid bracket order types, >2!!'
    orderList =( #debug socket send error,27aug2020,  Refer to API Guidelines's PPT, ~p.9
        [BLIMIT_BUY_IX]                     if (orderType ==BLIMIT_BUY_IX) else #Nothing bought, cancel BUY TWS auto cancel LIMIT&STOP SELLs as nothing for sells.
        [BLIMIT_SELL_IX, BLIMIT_BUY_IX]    if (orderType ==BLIMIT_SELL_IX) else #Cancel LIMIT SELL, TWS auto cancel BSTOP but BUY remain,28aug2020
        [BSTOP_SELL_IX, BLIMIT_BUY_IX] # Cancel STOP, TWS auto cancel SELL only. Need to cancel BUY if it is still active
                )

    oCnl=[]
    for oType in orderList:
        aS = bTrade[oType].isActive()  # avoid repeat cancels.
        if aS:
            tmp=ses.cancelOrder(bTrade[oType].order); ses.sleep(IB_DELAY) # slow down, debug socket.send() error. A19. 50msg/second =0.02sec each msg. 28aug2020
            oCnl.append(tmp)

    return oCnl  # ret as individual flattened cancelled trades

def printBracketTradesStatus(bTrades: list, logFileHandler, mode='BOTH'): #stock's placed Bracket order trade results
    """
    Print out trades status from a list of bracket-order trades.
         If mode=='BOTH' print to file and CONSOLE_M True, else print to console only
    :param bTrades: list of bracket trades
    :return: None
    """
    for bTrade in bTrades:
        if CONSOLE_M or mode=='BOTH':
            list(map(lambda o: print("Asset'{}':Status Filled Remaining-".format(bTrade[o].contract.localSymbol),
                                     bTrade[o].orderStatus.status, bTrade[o].filled(),
                                     bTrade[o].remaining(), '>' + LK_UP[o]),
                     [BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX]
                )   ) #MUST list() map-Obj to print on screen,24jul&1sep 2020. MUST must must
            print(f'Total No of bracket trades printed:{len(bTrades)}')
            
        # elif mode=='BOTH': # to file even CONSOLE_M True, else print to console only
        list(map(lambda o: print("Asset'{}':Status Filled Remaining-".format(bTrade[o].contract.localSymbol),
                                 bTrade[o].orderStatus.status, bTrade[o].filled(),
                                 bTrade[o].remaining(), '>' + LK_UP[o], file=logFileHandler),
                 [BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX]
            )   )
        print(f'Total No of bracket trades printed:{len(bTrades)}', file=logFileHandler)

def printListOfGrpTrades(listOfGroupedTrades, logFileHandler, mode='BOTH'):
    """
    Print from a list of grouped trades and the no. of trades in each group can be different.
    Parameters
    ----------
    listOfGroupedTrades : List of list, [ [a,b,c], [a,b,c], [a,b], [a,....]  .... ]
    logFileHandler : log file handler
    mode : Printing mode, default is print to 'BOTH' console & logfile.

    Returns: None
    """
    for trades in listOfGroupedTrades:
        ix=list(range(len(trades)))
        for i in ix:
            # if trades[i].isActive():  
            t=trades[i]
            print("Asset'{}'-trade({}). :Status Filled Remaining-".format(t.contract.localSymbol, i),
                      t.orderStatus.status, t.filled(), t.remaining(), file=logFileHandler)
            if CONSOLE_M or mode=='BOTH':
                print("Asset'{}'-trade({}). :Status Filled Remaining-".format(t.contract.localSymbol, i),
                      t.orderStatus.status, t.filled(), t.remaining() )

    print(f'Total No of grouped trades printed:{len(listOfGroupedTrades)}', file=logFileHandler)
    if CONSOLE_M or mode=='BOTH': print(f'Total No of grouped trades printed:{len(listOfGroupedTrades)}')

def printTradeStatus(trades: list, logFileHandler, mode='BOTH'):
    """
    Print out a trade status from a list of simple trade
    :param trades: list of trades
    :return: None
    """
    for trade in trades:
        # if trade is not None: #Check None, debug 14aug2020
        if CONSOLE_M or mode=='BOTH': print("Asset'{}':Status Filled Remaining-".format(trade.contract.localSymbol), trade.orderStatus.status,
                  trade.filled(), trade.remaining() )
        
        # elif mode=='BOTH': # to file even CONSOLE_M True, else print to console only
        print("Asset'{}':Status Filled Remaining-".format(trade.contract.localSymbol), trade.orderStatus.status,
              trade.filled(), trade.remaining(), file=logFileHandler )

    print(f'No of Trades printed:{len(trades)}. \n')


def printAccountKeyValues(ses):
    """
    print out account's key values
    :param ses: connected IB server session handler
    :return: None
    """
    print("\nAccount's Key Values from accountValues()")
    x=ses.accountValues(account='')
    for i in x:
        if i.tag=='FullAvailableFunds' and i.currency=='HKD':
            print(f'FullAvailableFunds, {i.value}', end=":'"); print(i.currency)
            # FullAvailableFunds=i.value
        if i.tag=='BuyingPower': print(f'BuyingPower, {i.value}', end=":'"); print(i.currency)
        if i.tag=='CashBalance': print(f'CashBalance, {i.value}', end=":'"); print(i.currency)
        if i.tag=='ExcessLiquidity': print(f'!!! ExcessLiquidity, {i.value}', end="!!!:'"); print(i.currency)
        if i.tag=='RealizedPnL' and i.currency=='HKD':
            print(f'RealizedPnL, {i.value}', end=":'"); print(i.currency)
            realiszedPnL=i.value
        if i.tag=='UnrealizedPnL' and i.currency=='HKD':
            print(f'UnrealizedPnL, {i.value}', end=":'"); print(i.currency)
            UnrealiszedPnL=i.value
        if i.tag=='MaintMarginReq': print(f'MaintMarginReq, {i.value}', end=":'"); print(i.currency)
        if i.tag=='NetLiquidationByCurrency': print(f'NetLiquidationByCurrency, {i.value}', end=":'"); print(i.currency)

    return float(realiszedPnL), float(UnrealiszedPnL) #make sure are floats


##### loopOrdStatusUntil() AND loopBracketOrdStatusUntil MUST Sync !!!, 30jul2020
def loopBracketOrdStatusUntil(bTrades: list, status='PreSubmitted', oType: int=BLIMIT_BUY_IX, count=100): #loop until all orders reach a preDefined status
    """
    Check Bracket Orders Status Until the target 'status' reached befoe return to calling function.
    :param bTrades: rade List. Each element in the list has a sublist with three orders, BLIMIT_BUY/BLIMIT_SELL/BSTOP_SELL
    :param status: Targeting order status at least to be reached.
    :param oType: One of the Blank order's type, index of BLIMIT_BUY/BLIMIT_SELL/BSTOP_SELL
    :return: False if over maximun trials, else True
    """
    opState=True # assume ok, no error
    maxTry=count; noOfStocks=len(bTrades); statuses=[None]*noOfStocks  #len(bTrades) = len(stocks)
    activeStage={None:0, 'PendingSubmit':2, 'PreSubmitted':3, 'Submitted':4, 'Filled':5, 'CancelInact':6}
    
    if noOfStocks !=0: # skip if input trades is empty
        allSubmitted=all(activeStage[x] >=activeStage[status] for x in statuses) #=True if all True    
        timeLimit=0; stockIx=list( range(noOfStocks) ) #ApiPending, PendingSubmit, PreSubmitted, Submitted, Filled
        while not allSubmitted and timeLimit< maxTry: #2min(40x3=120s) break the loop
            for s in stockIx:
                if bTrades[s][oType]: # do, there is something instead empty
                    # symbol=bTrades[s][oType].contract.localSymbol # default:BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX
                    symbol=bTrades[s][oType].contract.localSymbol # default:BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX                     
                    ibs.IB.sleep(1.3) #sleep 1.3s before check again. 1.3x60=78s Timeout
                    statuses[s]=bTrades[s][oType].orderStatus.status
                    if statuses[s] in {'Cancelled', 'Inactive', 'PendingCancel',
                                      'ApiCancelled'}: statuses[s]='CancelInact' #debug treat cancelled/./ as done,5aug2020
                    timeLimit +=1; print('Asset:',symbol,' Order status:', statuses[s])
            allSubmitted=all(activeStage[x] >=activeStage[status] for x in statuses) # True,when all LimitBuys Submitted
            print('                                   1====================1\n')
        print("\nVerified all LimitBuy-orders at least 'PreSubmitted/Submitted' or 'Filled', great! ")
        if timeLimit >= maxTry:
            print('There is Timeout Error, looped:', timeLimit); opState=False
    else: print('Input trades list is empty, skiped checkings.'); opState=False
    
    print(f'No of Trades from placed orders:{noOfStocks}')
    return opState
                # loopOrdStatusUntil() AND loopBracketOrdStatusUntil MUST Sync !!!, 30jul2020 #
def loopOrdStatusUntil(trades: list, status='PreSubmitted', count=100): #loop until all orders reach a preDefined status 
    """ Check simple Orders(non-bracket) Status Until the target 'status' reached befoe return to calling function.
        Parameters: trades=Trade List
        status=Targeting order status at least to be reached.
        return: False if over maximun trials, else True """
    opState=True # assume ok, no error
    maxTry=count; noOfStocks=len(trades); statuses=[None]*noOfStocks  #len(trades) = len(stocks)
    activeStage={None:0, 'PendingSubmit':2, 'PreSubmitted':3, 'Submitted':4, 'Filled':5, 'CancelInact':6}
    
    if noOfStocks !=0: # skip if input trades is empty
        allSubmitted=all(activeStage[x] >=activeStage[status] for x in statuses) #=True if all True      
        timeLimit=0; stockIx=list( range(noOfStocks) ) #ApiPending, PendingSubmit, PreSubmitted, Submitted, Filled
        while not allSubmitted and timeLimit< maxTry: #2min(40x3=120s) break the loop
            for s in stockIx:
                if trades[s]: # do, there is somethng instead empty
                    symbol=trades[s].contract.localSymbol # default:BLIMIT_BUY_IX, BLIMIT_SELL_IX, BSTOP_SELL_IX
                    ibs.IB.sleep(1.3) #sleep 1.3s before check again. 1.3x60=78s Timeout
                    statuses[s]=trades[s].orderStatus.status
                    if statuses[s] in {'Cancelled', 'Inactive', 'PendingCancel',
                                      'ApiCancelled'}: statuses[s]='CancelInact' #debug treat cancelled/./ as done,5aug2020
                    timeLimit +=1; print('Asset:',symbol,' Order status:', statuses[s])
            allSubmitted=all(activeStage[x] >=activeStage[status] for x in statuses) # True,when all LimitBuys Submitted
            print('                                   2====================2\n')
        print("\nVerified Orders in input List at least 'PreSubmitted/Submitted' or 'Filled', great! ")
        if timeLimit >= maxTry:
            print('\rThere is Timeout Error, looped:', timeLimit); opState=False
    else: print('Input trades list is empty, skiped checkings'); opState=False
    
    print(f'No of Trades from placed orders:{noOfStocks}')
    return opState
##### loopOrdStatusUntil() AND loopBracketOrdStatusUntil MUST Sync !!!, 30jul2020


def closePositions(mode:str, msg: str, ses): #mode='Patient', 'Urgent', 'Normal'
    """
    Close all positions (stock held) from the session
    :param mode: sell order's urgency mode
    :param msg: Message to be printed
    :param ses: IB server connection handler
    :return: None
    """

    closedTrades=[]; closeSym=[[],[]]; SYM=0; POS=1 #symbol,position
    positions = ses.positions()  # A list[] of positions, according to IB
    for position in positions:
        contract = position.contract
        if position.position > 0: # Number of active Long positions
            action = 'Sell' # sell hold stocks
        else: sys.exit('Error: Abnormal Negative Position Hold.') # terminate the program with the error msg.

        q = position.position
        order = ibs.MarketOrder(action=action, totalQuantity=q, algoStrategy='Adaptive', #Patient, Urgent, Normal
                algoParams=[ibs.TagValue('adaptivePriority', mode)], tif="DAY") #A16, Not Good-Til-Canceled. 'Adaptive' only support DAY!,31jul2020
        trade = ses.placeOrder(contract, order); ses.sleep(IB_DELAY) # slow down, A19. 50msg/second =0.02sec each msg. 28aug2020
        closedTrades.append(trade)
        closeSym[SYM].append(contract.localSymbol); closeSym[POS].append(q)
        print(msg+f" {action} {'{:.0f}'.format(q)} STK:{contract.localSymbol} {mode}") # f' string, A15
        assert trade in ses.trades(), 'trade not listed in ib.trades' #A17,assert True, do nothing.

    d = {'Symbol': closeSym[SYM], 'Position': closeSym[POS]}
    dict2DfEmailAdm(d, f". Closed the stocks by '{mode}' sell mode.", 'Closed ALL stocks positions held. From:'+sys.argv[0])

    return closedTrades
### ALL above functions' input-VARIABLES are vectors(list) and handled by vector operators.

def strongeBeep(beepCnt: int, silent=False):
    """
    Beep the computer to alert the user
    :param beepCnt: No of beeps
    :return: None
    """
    if not  silent:
        winsound.Beep(1650, 950) # .Beep(1650Hz, (XXXXms)) #e.g 1000ms=1second
        while beepCnt >=0:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS); beepCnt -=1

    return


def mSureNoStockHolded(ses):  # double check and close all outstanding stocks hold.
    """
    Make sure no stock position hold in the session and close them not matter what reason of the holdings
    :param ses: IB server connection handler
    :return: stockSymExch=stock code-symbol and exchange list.
             positions= total number of shares hold in all stocks
    """
# ==========# disable to avoid chopped stocks, 5nov2020 ======================
#     # opOrders = ses.openOrders()  # 1st CANCEL all openTrades from previous market orders placed, avoid short-sell
#     # for ord in opOrders:
#     #     ses.cancelOrder(ord);
#     #     ses.sleep(IB_DELAY / 4)  # delay not critical, few orders reminds at this point.
# =============================================================================

    stockSymExch =[]; holdStocks =[]
    total = 0; positions=ses.positions()
    for position in positions:
        holdStocks.append(position.position)
        stockSymExch.append([position.contract.localSymbol, position.contract.exchange])
        print('Asset from today/past:', position.contract.localSymbol)
        total += position.position

    print('Walked through and close all stocks positions.')
    if total != 0:
        print('!!! Warning !!!. Some stocks STILL on-hand???')
        
        msg = 'Close positions by urgent market orders again:' # No need , 23dec2020
        closePositions('Urgent', msg, ses) # No need if unsold stock replaced by Urgent MktOrder instead of Normal order, 23dec2020
        emailAdmin('!!! Warning !!!. Some stocks STILL on-hand???', '  From:'+sys.argv[0])
        
    else:
        print('****** Great, sold all on hand stocks today ******')


    return stockSymExch, holdStocks

def openFileEmailAdm(pathFileName, mode='at'):
    """
        Open file for append 'a' and text 't' mode, email Admin if error
    :param pathFileName: Full path with file name
    :return: the opened file's handler
    """
    try:
        # do'nt use "with" which will close the file after the with: code-block. https://stackoverflow.com/a/28825445/10356838
        logFileHandler=open(pathFileName, mode) #full path with filename
    except Exception as e:
        print(e); emailAdmin(f"File Open Error, System Stopped. Error:{e}", '  From:'+sys.argv[0]) # running Python code's name.

    return logFileHandler # Non-closed file handler
    
def initChromeDriver(defaultDnLoadPath=os.getcwd()):
    """
    Chromedriver.exe update is handled by ChromeDriverManager(),
    with size 800x600 and download path is current working directory instead of win10 download directly
    with ChromeDriverManager it is not necessary to prevent chrome auto-update at EC2, sometime is impossible
    as google is too smart in working around my old method.
    Parameters
    ----------
    path : string. Default is getCwdPath() +'chromedriver.exe'.
    Returns
    -------
    driver : handler for the opened browser and 
            downlaode right version in:       
            C:\\Users\\Administrator\\.wdm\\drivers\\chromedriver\\win32\\8x.0.4324.xx\\chromedriver.exe
    Ref: auto-updates: https://github.com/yeongbin-jo/python-chromedriver-autoinstaller
    """
# ========***** ===========IMPORTANT=============================****** ========
# Must prevent chromedriver.exe auto-update at EC2 or your running PC.
# "C:\Program Files (x86)\Google\Update\GoogleUpdate.exe" to "GoogleUpdate-org.exe", EC2 Done again 1Mar21
# =============================================================================
    # chromedriver = path  
    options = Options()
    options.add_experimental_option("prefs",
        { "download.prompt_for_download": False,
          "download.default_directory": defaultDnLoadPath, #save into current directory instead win10 download
          "safebrowsing.enabled":"false"
        })
    options.add_argument("--start-maximized")

    # driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    driver.set_window_size (800, 600) # reset window size
    return driver

"""
def randomWalk(): # model for randomWalk behaviour
    random=0 # dummy stub
    return random

def shortTerm(): # short-term model
    return # dummy stub

def longTerm(): # long-term model
    return # dummy stub

def stockScans(): # scan sectors of stocks
    return # dummy stub

def faultToleranceCheck(): # for fault tolerance multi program-servers, datafeed sources, broker traders consideration
    return # dummy stub
    
def buyDecisionQualifier(): # qualify a buy decision from unexpected bad news etc....
    return
"""

""" Reference A:
1) URLerror.code/reason: https://docs.python.org/3/library/urllib.error.html
2) https://numpy.org/doc/1.18/reference/generated/numpy.ma.size.html
3) np.unique()): https://stackoverflow.com/questions/52931158/confusion-matrix-return-single-matrix
4) Keras model.predict() & predict_class(): https://keras.io/models/model/
5) creat Boolean array: http://www.math.buffalo.edu/~badzioch/MTH337/PT/PT-boolean_numpy_arrays/PT-boolean_numpy_arrays.html
6) email:  #https://yagmail.readthedocs.io/en/latest/api.html#e-mail-contents   
7) self & class variables: https://medium.com/quick-code/understanding-self-in-python-a3704319e5f0
8) call methods within class: https://www.geeksforgeeks.org/python-call-function-from-another-function/
9) super().xx :https://www.geeksforgeeks.org/python-call-parent-class-method/
10)  https://github.com/DeepSpace2/StyleFrame/issues/61
11) gDown url issue: https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
12) datatime format: https://strftime.org/
13) Mon(0)-Sun(6): https://pythontic.com/datetime/date/weekday
14) https://www.geeksforgeeks.org/downloading-files-web-using-python/
15) f'' string formating: https://www.geeksforgeeks.org/formatted-string-literals-f-strings-python/
16) Force order types: https://www.interactivebrokers.com.hk/en/software/tws/usersguidebook/ordertypes/time_in_force_for_orders.htm
17) Assert True: https://www.tutorialspoint.com/python3/assertions_in_python.htm
18) if elif else:  https://www.programiz.com/python-programming/if-elif-else
19) sleep(mSecond): https://www.mytecbits.com/internet/python/sleep-for-milliseconds#:~:text=In%20order%20to%20use%20this,(0.06)%20and%20so%20on.
20) IB max message/second: https://interactivebrokers.github.io/tws-api/order_limitations.html
    Related artical: https://ibkr.info/article/1765
    ib_insynce discussion: https://groups.io/g/insync/topic/max_rate_of_messages/6390099?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,6390099 
21) Slice array by tuple: https://stackoverflow.com/questions/34729331/slice-array-by-tuples
"""

