# -*- coding: utf-8 -*-
""" STOCK, use IB paid data service to get order placing price.

autoDayTrade03 is a backward version from 02 of not use Warrant, but only use stock.
    Moreover, price is from IB paid data service instead by estimation

yagmail.SMTP("detaDayTrade01@gmail.com"): 1st use in a NEW computer. Please login by browser at the computer
     and confirm google with password the computer IS secure first!!

- NEVER use time.sleep in ib_insync related functions, use ibs.IB.sleep(seconds) 
- IB will cut the connection if a code madly repeat to send same cancel order,
  if the order was cancelled without the order ID already. !!!!
- 50 messages per second implying a maximum of 50 orders per second being sent to the TWS.
  IB allows up to 15 active orders per contract per side per account.

Dependencies:
    - Right version of chromedriver.exe (auto detect version NOW, 2jaN2022)
    - timeIndex.xlsx	# time index table (not necessary from detalibs.py ver17.2 3jan2022)
	- classfi.hdf5 from classfi.py, predict.hdf5 from predict.py
	- detalibs.py
    - Two PDFs files for email. 2-FAQ.pdf, 3-Disclaimer.pdf
    - need a subFolder called ../prd-outputs
    - SEHK trading calendar file. yyyy/2021-Calendar_csv_e.csv

ver0.0 9dec2021 - fallback to stock only version. Search 'dec2021'
ver1.0 13dec2021 - first completed version that can use IB paid data service. Search 'dec2021'
                    used dt.getSymbol() to get stock/warrant symbol for displaying & email.
ver1.1 21dec2021 - use IB paid data service to get order placing price and today monring prices.
ver1.2 3jan2022 - used different percents for warrant and stock to takeProfit/stopLoss sells.
ver1.3 4jan2022 - increase buy QTYs when few or only 1 stock picked to make it closer the budget available
                    Double by: tmpQtys=tmpQtys*2 #increase the QTYs
ver1.3.1 7jan2022 - add delays in the loop of launching coRoutine to reduce potential re-entrance problem,
                        when picked many stocks with many coRoutines created.

"""
import sys; import detalibs as dt #; import yagmail
import numpy as np #; import math; import datetime; import re # re.split("[_.]", strings)[1] #multi delimiters
import pandas as pd; from copy import deepcopy
from datetime import datetime, timedelta#, timezone#; import time
import os.path, time

### Be the last import statement with the util.startloop() is better but not MUST.
import ib_insync as ibs; ibs.util.startLoop() # Need in Spyder but not in DOS command-line mode

YAHOO, IB_DATA, IB_COMIS_EST=0,1,2
DATA_SRC=YAHOO # YAHOO/IB_DATA
PRICE_SRC=IB_COMIS_EST #IB_DATA/IB_COMIS_EST, COMIS is estimate from commission

oneMilRatio=8.333 #1M/0.12M, 0.12M=120k
LOT_SIZE_UP=dt.getDetaConfig()[10]*oneMilRatio/4 # 7jan2022, further scaleUp for large budget.
assert LOT_SIZE_UP >= 1, 'LOT_SIZE_UP cannot < 1'

PAPER_MODE=True; REMIND_G=True
    #### NEVER USE DOS mode #####
# EC2_DOS=False # NEVER USE DOS mode, ib_insync realtime events not stable in DOS,30dec2020
NO_SPK=True #Will not beep the computer's speaker

LEVERAGE=1 # leverage by margin, 1 not leverage, max is ~2
TEST1_0=True # True=ignore startTime/email. False / True
TEST1_1=False  # use PickedStock Excel file, do'nt download=True
TEST1_2=False  # use a fixed date for Sat/Sun debugings=True
TEST1_3=False; FIX_F='DateSet_(2022-01-13).csv' # use the fixed file below

F_UNITS = 1000 # total no of units for NAV calculation. e.g. 120,000/120 =1000
DA_EXCEED_AMT=dt.getDetaConfig()[8] # # is 0.2M 3jan2022. 1e6=$1M. 
EMAIL_FILE='1-TodayStockPick.xlsx'; attachFiles=[EMAIL_FILE, '2-FAQ.pdf', '3-Disclaimer.pdf'] #attach order base on alpabatic order of the files
# START_HOUR=11; START_MINUTE=57 #12:00, 21dec2021, real-time download & more time for IB download
START_HOUR=12; START_MINUTE=18 #17 # hr:min(24hrs) download morning price at lunch break, A5

SEHK_CLOSE_HR=15; PRE_CLOSE_MIN=50 #3:50p, 10min early than realClose for urgent sell stocks OUT.
SEHK_CLOSE_MIN=68 # it is 4:08pm, 60+8min
SEHK_LUNCH_END_HR=13 #24hrFormat. 1pm, 59min, 59s
PLACE_ORD_M=0 #Added 2s default. WAR used 2 #wait for a while after the assets behind have prices first, 22feb2021
DIS_TIME=3.8 # stop x seconds for human viewings
WAIT_ACK=29 #45s not work, 30s work.

#### General (picked stocks) email distribution list
if TEST1_0: BCC_EMAILS =['hoson@live.hk']
else: BCC_EMAILS =['hosanglam4-c@my.cityu.edu.hk', 'twgli@connect.hku.hk', 'pongcyuen@gmail.com', 's97474665@gmail.com', #picked stocks distribution list
                   
                   # 'research@efusioninv.com', 'eewmtsan@cityu.edu.hk',
                   
                   # 'ngjessicayy@gmail.com', 'maggieyu0808@ymail.com', 'swaniwu@gmail.com', #CU EMBA
                   # 'lo_jack23@hotmail.com', 'steven.yfseafood@gmail.com','jessielee_329@yahoo.com.hk',
                   
                   ] #Multi gmailNames in one hot.
#### Formal NAV members' email distribution list
MEMBR_EMAILS=['hoson@live.hk', 'tograceli@hotmail.com'] #, 's97474665@gmail.com'] #NAV member emails
emailSubject=". Generation IV: Support stock, Warrant etc., Get price by IB data services !"
emailBody =  """\
                    G-IV Ver 1.2: Real, Live Trading (Validating in paperMode)

    1) The Robot places Market orders for the picked assets (warrant/Stock) start at 1:00:02 pm.
    2) He will place take-profit, stop-loss & time sell order by OCA API afterwards,
    3) and at 3:30 pm sell out all assets on-hand at market prices, without holding overnight!
    
    * Budget set at HKD1M on the first day and put back profits to the trading account every-day until after at least a week.
    * Warrant stamp duty is assumed zero.
    ## All price values are in HKD. All RMB&USD SEHK-traded securities are removed. e.g. 82833/9834...
    ## Please refer to the "Disclaimer" file on the limited responsibility of this robot-email notice.
    ### This new version can support LSE exchange in future. 
                                                                                Dave. Jimons 2021-2022
              """
emailBody += '\n\n\n From machine: '+ sys.argv[0].split("-")[0] # add partial machine related path information

def analysisAllStocks(ses):
    """
     Update SEHK stock list. Download prices and analysis all stocks-ETF-REIT. Email the picked asset table

    Returns: dataframe of assets picked or an empty list to keep next day run
    -------

    """
    allHKExStocks=dt.getHkexStockList() # download stocks/Reit/ETF(no warrants/bond) but getHkexAssetList() have. Then save into AllStockTable.xlsx
    # symbolList, barsList=dt.setupAllSehkAssetBars(allHKExStocks, ses, sample=False) #9jan2022
    stocksInfo=allHKExStocks.iloc[:,0:4]  # updated securtities list from HKEX Get all stock codes with index = StockCode
    classfiNN='classfi.hdf5'; predictNN='predict.hdf5'; print('The classifier is: ',classfiNN, ' and predictor is: ',predictNN, end='\n\n')
    parameters=dt.loadNpStrucArrAsDict(dt.getCwdPath()+'dayTrade01Para.npy') # Load Dict of optimised parameters stored
    DaveFundMgr=dt.Dave(classfiNN, predictNN, 0.8) #0.8=similarly, 3jan2021
    # DaveFundMgr=dt.Dave(classfiNN, predictNN, parameters['similarly']) #valid price-vol lenght=11_59+1, others None
    msg=time.ctime(os.path.getmtime('classfi.hdf5'))
    msg1=time.ctime(os.path.getmtime('predict.hdf5'))
    msg=f'classfi-NN lastest file time:{msg}, which should less than a week from today.'
    msg1=f"predict-NN file time:{msg1}. Dummy NN does'nt cause bug, 22dec2021. \n"
    dt.emailAdmin(msg, msg1+' From:'+sys.argv[0])

    #e.g. startDate = '2020-06-08', endDate = '2020-06-09' END DATE is not included
    today=datetime.today() if not TEST1_2 else datetime(2022, 1, 13, 13, 1, 1, 1)  #13 have, 15 Sat NONE
    if TEST1_3: # use the target fixed file.
        todayStockDf=pd.read_csv(FIX_F, index_col=0) 
    else: #DONWLOAD from internet
        if DATA_SRC==YAHOO:
            todayStockDf=dt.getHKExStocksPrice(allHKExStocks, today.strftime('%Y-%m-%d'), #today date
                                            (today+timedelta(days=1)).strftime('%Y-%m-%d')) #today date +1day
        elif DATA_SRC==IB_DATA:
            dt.ibDnLoadPrices1D(allHKExStocks, today, ses) # 1day version, 21dec2021
            # todayStockDf=dt.converBars2DetaFormat(symbolList, barsList) # 1day version, 9jan2022
        
    # todayStockDf=
    # todayStockDf=dt.getHKExStocksPrice(allHKExStocks, today.strftime('%Y-%m-%d'), #today date
    #                                 (today+timedelta(days=1)).strftime('%Y-%m-%d')) #today date +1day
    todayStockDf.to_csv(dt.getCwdPath()+'prd-outputs\\'+'todayStockRaw.csv') #for debug diff pick ExcelSim, 15sep2020
    tmp=len( todayStockDf['Stock Code&Date'].value_counts() ) #check Yahoo download how may stock today. Should >1500. A21, frequency count.
    dt.emailAdmin(f'Yahoo downloaded:{tmp}, >1.5k?. todayStockRaw.csv &other daily-replaced CSVs save in :.prd-outputs\\ directory.', 'From:'+sys.argv[0])

    ### If not a valid tradeday, all stock volumns are zero. debug19aug2020 ###
    temp=todayStockDf[dt.LABEL_VOL]
    if temp.iloc[dt.PRICE_START:(dt.PRICE_11_59a+1)].values.sum()==0: #debug, [row,0] single col,0 do'nt work
        dt.emailAdmin('ALL stocks ARE zero volumns in morning, maybe Typhoon/Unexpect-Holiday or else non-trade days', ' From:'+sys.argv[0])
        todayStockDf=[] #set to an empty list
        return todayStockDf # !! dirty EARLY return to terminate this function BUT not terminate the Code !!

    csvDf, profitDf=DaveFundMgr.classfiPredictDf(todayStockDf) # All output prices&volumns are denormalised by multipy by their MAXs

    if profitDf is not None:
        #able to get at least one stock > similarity thresold, debug 10sep2021
        profitDf['amTradingAmount']= np.nan #prepare a col for pdDataFrame.loc() access
        profitDf=profitDf.set_index(dt.STOCK_CODEDATE) #reindex - use dt.STOCK_CODEDATE as dataframe index
        for codeDate in profitDf.index:
            profitDf.loc[codeDate,'amTradingAmount']=np.around(dt.amTradingAmountCalculation(csvDf,codeDate) ,decimals=0)

        todayPickDf= profitDf.copy(deep=True) #for warrant mode, 8mar2021
        todayPickDf= profitDf[profitDf['amTradingAmount']> DA_EXCEED_AMT] # need for stk-war mix mode. only pick stocks according to the DA size.
        todayPickDf=todayPickDf.sort_values(by=['amTradingAmount'],ascending=False) #Sort the DAs from high to low. Only top few stocks will buy
    
        codeIntList=dt.profitDf2IntCode(todayPickDf) # get stockcode as a list of integers
        temp=stocksInfo.loc[codeIntList, dt.COM_NAME].to_list(); todayPickDf['Name']=temp #A7,add Eng col to existing DF by list
        temp=stocksInfo.loc[codeIntList, dt.C_SEHK].to_list(); todayPickDf[dt.C_SEHK]=temp # add security classes into Df
        temp=stocksInfo.loc[codeIntList, dt.LOT_SIZE].to_list(); todayPickDf[dt.LOT_SIZE]=temp # add for chopped lotsize adjustment 7sep2020
        todayPickDf['Code']=codeIntList
    # ========== Drop unwanted stuffs ============================
        #todayPickDf.to_csv(dt.getCwdPath()+'prd-outputs\\'+'todayPickDfBeforeDrop.csv')
        rowBeforeDrop=todayPickDf.shape[0]  #[0] number of row, [1] col
        todayPickDf.drop_duplicates(subset ='Code', keep = False, inplace = True) #A10,fix a random bug of repeat stokcs 152,H22jun2020
        # rowsDropped=rowBeforeDrop-todayPickDf.shape[0] #before - after drop
        print('Duplicated rows dropped=', rowBeforeDrop-todayPickDf.shape[0])
    
        todayPickDf=dt.dropNonHkdSec(todayPickDf) # Drop RMB&USD currency securities. A16
    # =============================================================================
        todayPickDf.to_csv(dt.getCwdPath()+'todayPicks.csv') #for email usage
        dt.noticeTraders(f'Stocks Picked before convert to warrants and dayTrade01Para.npy content is: {parameters}. '+sys.argv[0],
                         dt.ADM_EMAILS, ['todayPicks.csv'], '- Stock.')
    #### Convert Stocks to available warrants START, 12feb2021. Disable 12dec2021 
        tmp=len(todayPickDf)
        todayPickDf=dt.stockToWarStkII(todayPickDf) # o/p is 換股比率, multipler = 1/(換股比率) for IB placeOrder
        
        # todayPickDf=dt.stockToWarStk(todayPickDf) # Assume selenium chromedriver in current directory
        if len(todayPickDf) ==0:
            dt.emailAdmin(f'No assets found. As dropped:{tmp} after stockToWarStk(), exist and go next trade-day.', ' From:'+sys.argv[0])
            todayStockDf=[] #set to an empty list
            return todayStockDf # !! dirty EARLY return to terminate this function BUT not terminate the Code !!
        todayPickDf.to_csv(dt.getCwdPath()+'prd-outputs\\'+'afterStockToWar.csv') #for ref only.
      
        if '成交額 (千元)' in todayPickDf.columns: #debug 31mar2021, as sometime do'nt have the col.  col is Indexs that is np arrays. Simply match a string with an array.
            tmp1=todayPickDf.loc[ todayPickDf['成交額 (千元)'] ==0 ].index # debug when 0
            todayPickDf.drop(tmp1, inplace=True) # debug when 0
        if len(todayPickDf) ==0:
            dt.emailAdmin('No assets found. As dropped:{len(tmp1)} too small traded-amount, exist and go next trade-day.', ' From:'+sys.argv[0])
            todayStockDf=[] #set to an empty list
            return todayStockDf # !! dirty EARLY return to terminate this function BUT not terminate the Code !!
    
        todayPickDf.to_csv(dt.getCwdPath()+'prd-outputs\\'+'todayWar-others.csv') #for ref only.
    #### END: Convert Stocks to available warrants, 12feb2021 
    
        #### Re-order the columns for saving to Excel
        if len(todayPickDf) >0:#avoid potential bug, 5mar2021, sometime pick none stock. valid Dataframe, rows X cols >0, at least 1. 
            colNames=['Code','Name', dt.C_SEHK, dt.LOT_SIZE, 'Underlying Sym', #add 11jan2022
                       '換股比率', '購/沽', # will buy rise/drop by 購/沽. Warrant specific. Disable 12dec2021
                       '實際槓桿','價內/價外 (%)', '到期日 (年-月-日)', '行使價', '街貨量 (%)', '最後交易日 (年-月-日)', #Warrant specific. Disable 12dec2021
                      ]
            newColNames=[] #store only available cols and skip do'nt exist warrant specific cols
            for name in colNames: #debug KeyError 18apr2021, work when no warrant was found & no corresponding cols
                if name in todayPickDf: newColNames.append(name) #only use cols available
    
            todayPickDf=todayPickDf[newColNames].copy(deep=True)
            bestFitCols=(dt.STOCK_CODEDATE, 'Name') #, '成交額 (千元)')        
            dt.fitSaveStyleFrame(todayPickDf, bestFitCols, None, EMAIL_FILE) #sortKey==None, will not sort
            msg='Dave'+ ' -reference indexes '+ '{:.1}'.format(DaveFundMgr.simThreshold)+ f" Vs {parameters['similarly']} "+ emailSubject
            dt.noticeTraders(emailBody, BCC_EMAILS, attachFiles, msg) #the body included machine info already.
    
            print(DaveFundMgr.name,
                  "'s  character is Similarity-{0},DayLength-{1}".format(DaveFundMgr.simThreshold,
                  DaveFundMgr.aDayLengthEnd) ) #A2
        else: print('No stock picked today!')
        
    else: todayPickDf=[] #dirty EARLY return. when UNABLE to get at least one stock > similarity thresold, debug 10sep2021
    return todayPickDf # SEARCH "dirty EARLY" RETURN at ~line 108 &154/162/170 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!,19aug2020

def placeNmonitorOrds(todayPickDf, ses): #caller checked todayPickDf is NOT empty before call this API
    """ todayPickDf is 換股比率, multipler = 1/(換股比率) for IB placeOrder
        Place orders for selected assets and monitor their status at different times.
        This will save all daily report into subdirectory called 'prd-outputs' under current directory.
        Parameters: todayPickDf=select assets dataframe
        cumWeekFund= accumulated funds during a week day-by-day carry forward
        ses=IB server connection handler 
        
        Returns: tomorrowInvestLimit= net-fund earned daily for next day's usage """  
        
    # def pickDf2ContactsQtyPerLot(todayPickDf, ses): #, secType='WAR'): # take out asset without
    #     contracts, todayDf=dt.warNonWarContracts(todayPickDf, ses) #auto detect STK or WAR
    #     qtyPerLotVector=todayDf[dt.LOT_SIZE].to_numpy(dtype='float', copy=True) #get it values, can't int 20dec2021
        
    #     return contracts, qtyPerLotVector, todayDf

    logFullPath=dt.getCwdPath()+'prd-outputs\\'+'logfile'+datetime.now().strftime('%Y-%b-%d')+'.txt' # log file with time stamp
    logFileHandler=dt.openFileEmailAdm(logFullPath) # open writeable file and emailAdm if error

    def errHandler(reqId, errorCode, errorString, contract): # 18dec2020
        # logFileHandler in OUTER scope of this function but not GLOBAL!, be careful !!
        try: print(f" ErrorEvent Id:Code:Msg- {reqId}: {errorCode}: {errorString}: {contract}", file=logFileHandler)
        except: print("Skipped print's exception Error, when no logFileHandler !")   
        return
    ses.errorEvent += errHandler # operator overload. Add connect method's function, in event kit Not insync.

 ### Init time constants for while-loops to check Orders, until 3:30+2 pm
    now=datetime.now(); print("Now is:", now.strftime('%Y-%b-%d %H:%M'), "(HK Time only!)") #A12,get&print current time
    timeCancelNplaceOrds=now.replace(hour=dt.REPLACE_byMKTSELL_HR, minute=dt.REPLACE_byMKTSELL_MIN+2, second=0, microsecond=0) #>=3:30+2 pm. Give 2min for timeCond Order to be executed.
    timeStopTrades=now.replace(hour=SEHK_CLOSE_HR, minute=PRE_CLOSE_MIN, second=0, microsecond=0) #A4, replace to target runtime
    timeLunchEnded=now.replace(hour=SEHK_LUNCH_END_HR, minute=PLACE_ORD_M, second=2, microsecond=0)

    accValues=ibs.util.df(ses.accountValues(account='')) #Starting Account values DF
    todayInvestLimit=float( accValues.query(" tag=='CashBalance' & currency=='HKD' ")['value'] ) #settled cash, T+2. A19
    todayInvestLimit=min(todayInvestLimit, oneMilRatio*dt.getDetaConfig()[9]) #increased to hkd1M, 14dec2021
    print(f"\nToday's Investment Limit is(min(budget, accBalance)):HKD{todayInvestLimit}"); ses.sleep(DIS_TIME)
    buyPower=float( accValues.query(" tag=='BuyingPower' & currency=='HKD' ")['value'] ) #A19
    print(f"Buypower:HKD{buyPower}, enlarged by margin. !!!!!!")
    dt.emailAdmin(f"Connected: HK$, Today buyingPower:{buyPower}, investment limit:{todayInvestLimit}", 'From:'+sys.argv[0]) # running Python code's name.

    if LEVERAGE !=1:
        msg=f'Ignore investLimt picked, leverage it by margin at {LEVERAGE} times.'
        print(msg); dt.emailAdmin(msg, '  From:'+sys.argv[0])
    
    contracts, qtyPerLotVector, todayPickDf=dt.pickDf2ContactsQtyPerLot(todayPickDf, ses) # MAY change the todayPickDf, 9jan2022       
    if PRICE_SRC==IB_DATA: localSymbols, tickers=dt.reqAllMktData(contracts, ses, mode=dt.FROZEN) # 30dec2021, preparing to get real-time data as it take time to fill tickers

    print('Waiting until 1:00:02pm....., looping!')
    if not TEST1_0:
        while datetime.now() < timeLunchEnded: pass #1:00:02pm

    ## Debug 4mar2021, unknow reasons that some warrant do not report commission ##
    if PRICE_SRC==IB_COMIS_EST:
        dfTable=dt.estPricesFrCommission(contracts, qtyPerLotVector, ses, mode=dt.EST) #make SURE over min commission for price estimation 
    elif PRICE_SRC==IB_DATA:
        # prices=dt.reqAllPrices(tickers)
        dfTable=dt.oldFormatPrices(localSymbols, dt.reqAllPrices(tickers)); dt.cancelAllMktData(contracts, ses)  
    # prices=dt.reqAllPrices(tickers); dfTable=dt.oldFormatPrices(localSymbols, prices); dt.cancelAllMktData(contracts, ses)
    # dfTable=dt.estPricesFrCommission(contracts, qtyPerLotVector, ses, mode=dt.EST) #make SURE over min commission for price estimation 
    # dfTable=dt.getRealPrices(contracts, ses) #most stable, up to 6jan2022

    todayPickDf['commiS']=dfTable['commiS'].values #round after DROP. =None of 'commissions'&'estPrices' => np.nan after .values
    todayPickDf['estPrices']=dfTable['estPrices'].values #=None of 'commissions'&'estPrices' => np.nan after .values 

    noPriceDf=todayPickDf.loc[ todayPickDf['estPrices'].isnull()]; tmp1=noPriceDf.index
    placeOrderDf=todayPickDf.drop(tmp1, inplace=False) #drop
    noOfdrops=len(tmp1) #for later usage

    #     # Regenerate contracts if dropped some assets and there are still have some.
    contracts, qtyPerLotVector, placeOrderDf=dt.pickDf2ContactsQtyPerLot(placeOrderDf, ses) # MAY change the contract and Df !!, 9jan2022
    
    placeOrderDf=placeOrderDf.round({'estPrices': 2, 'commiS': 2}) #round after removed Nones, debug18mar2021
    estPrices=placeOrderDf['estPrices'].to_list()
    numOfLot=dt.brkEvenLotSize(estPrices, qtyPerLotVector, dt.BROKER_BEQ, contracts)*int(LOT_SIZE_UP) #MUST INT, increase lots, 22dec2021
    quantities=np.multiply(qtyPerLotVector, numOfLot).flatten() #(1, x)=>(x, 1) shape
    ## save qty info into the df later, ~line257, after placed time-sensitive price orders first
    estValues=np.multiply(estPrices, quantities).flatten() #(1, x)=>(x, 1) shape

                ### Handle situation when very few stocks are picked & can't use the budget even BUY ALL.
    tmpQtys=quantities; tmpValues=estValues # .sum() will be the total investment amount.
    while tmpValues.sum() < todayInvestLimit* LEVERAGE:
        estValues=deepcopy(tmpValues); quantities=deepcopy(tmpQtys) #Update with the smaller QTYs that result in investment amount within budget.
        tmpQtys=tmpQtys * 2 #increase the QTYs
        tmpValues=np.multiply(estPrices, tmpQtys).flatten() #Update estValues for above while-loop test
    dt.emailAdmin('Will increase lotSizes to invest more when picked very few stock only.', 'x2 at least. From:'+sys.argv[0])
                ### Handle situation when very few stocks are picked & can't use the budget even BUY ALL.
        
    mTrades=[]; attachedRoutines=[] # list of profit-Take/Stop-Loss sells instance to be attached   
    assetIx = list(range(len(contracts))) #STK/WAR assets etc.    
    mOrders = [ ibs.MarketOrder(action='BUY', totalQuantity=quantity ) for quantity in quantities ]
    totalInvestAmt=0.0; buyIx=[] #the RecursionError is not really from here! Unknown code-analysis error but fine to run
    for i in assetIx: # establish buy Index for buyIx. for-loop (a)
        amount=estValues[i] #shape must (x, 1)
        totalInvestAmt +=amount
        if totalInvestAmt <= todayInvestLimit* LEVERAGE:
            buyIx.append(i) #SOME order maynot be placed if over budget
        else: totalInvestAmt -=amount; break #adjust for reporting purpose
    noOfPlaceOrd=len(buyIx)

    dt.OcaSell_10a.resetStates(counts=0, recList=[]) #each day reset before use AGAIN.
    dt.emailAdmin('Will use different TakeProfit/StopLoss Percents.', 'Refer to coming email record. From:'+sys.argv[0])
    for i in buyIx: #index of assets to be bought
        if contracts[i].secType=='WAR':
            takeProfit= dt.TAKE_PERCENT # 7%
            stopLoss= dt.STP_LOSS_PERCENT # 7%
        elif contracts[i].secType=='STK': #'STK' = Stock (or ETF), 'WAR' = Warrant (ib_synce sourceCode)
            takeProfit= dt.TAKE_PERCENT-4 # 7% to 3%
            stopLoss= dt.STP_LOSS_PERCENT-4 # 7% to 3%
        else:
            dt.emailAdmin(f'WARNING!. Security type:{contracts[i].secType}, not yet supported. Used default values.', '  From:'+sys.argv[0])
            takeProfit= dt.TAKE_PERCENT # 7%
            stopLoss= dt.STP_LOSS_PERCENT # 7%
            
        coRoutineInstance= dt.OcaSell_10a(ses, contracts[i],
                                       takePercent=takeProfit, #e.g. 7-4=3% for stock
                                       stopPercent=stopLoss, #stop will use '-' minus percent internally
                                       sellTime='15:30' 
                                       )
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        # ======= 2 statements as close as POSSIBLE ===========================
        mktTrade=ses.placeOrder(contracts[i], mOrders[i])
        mktTrade.filledEvent+= coRoutineInstance.fireAttachSells #can't put into API 17feb2021, must in mainLoop     
        # ======= 2 statements as close as POSSIBLE ===========================
        
        coRoutineInstance.refTrade=mktTrade # the entry trade
        attachedRoutines.append(coRoutineInstance ) #keep record
        mTrades.append(mktTrade ) #keep record
        ibs.IB.sleep(dt.IB_DELAY) #delay a bit before launch next coRountine, 7jan2022
        if noOfPlaceOrd >5: ibs.IB.sleep(dt.IB_DELAY*5) #reduce speed if more than 5 orders, 7jan2022
        # if noOfPlaceOrd%49 ==0: ibs.IB.sleep(dt.IB_DELAY*noOfPlaceOrd) #avoid > 50msg/second    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

    #Reminder: NOT in the for-loop above
    mismatch= dt.OcaSell_10a.counts - len(attachedRoutines)   
    placeOrderDf['Opti Buy Qty']=quantities #breakEven qty calculated
    placeOrderDf.to_csv(dt.getCwdPath()+'dfWithEstPrice.csv')
    msg=f'Dropped: {noOfdrops} asssets without commissions info. MismatchOCA:{mismatch}. Order at HKT: '+timeLunchEnded.strftime("%H:%M:%S") + sys.argv[0]
    dt.noticeTraders(msg, dt.ADM_EMAILS, ['dfWithEstPrice.csv'], '- with price(when $10000 commiS) or Est. Prices from commission.')
    
    print('Check market Orders filling situation...')
    if not dt.loopOrdStatusUntil(mTrades, status='Filled', count=1888):#1001 too small, 5jan2022    
        msg='Wait abnormal long to fill all market entry orders, PLEASE CHECK EC2!!,if not No-order-placed today. Try ~1k loop unitl done.'
        dt.emailAdmin(msg, '  From:'+sys.argv[0])
    else:
        print('All placed entry Mkt trades filled.')   
    print(f'Assets picked&trading are {len(mOrders)}, placed-Order are {len(buyIx)}. Difference is {len(mOrders)-len(buyIx)}.')
    
    ### 3:30+2 pm > Time > ~12:30p-1:00p , loop to check take-profit Stop-loss Sell done or not ###
    print('No of Open Trades', len(ses.openTrades()) ) # trigger a request to get an update, 10sep2020, try help bTrades
    SYM=0; AMT=1 # indexing for symbol and running index number.
    keepLoop=True; printedA=False; printedB=True #for control toggleing to reduce screen printings frequencies
    while keepLoop: #use a boolean to control the loop for better documentation
        if datetime.now() > timeCancelNplaceOrds: #>=3:30+2 pm. Give 2min for timeCond Order to be executed.
            attachTradesList= dt.OcaSell_10a.GLOBAL_records #get again, debug 1mar2021
            closeTrades=[]
            for attachTrades in attachTradesList:
                closeTrade =attachTrades[-1]; closeTrades.append(closeTrade) # [-1] is last item of a list
            dt.printListOfGrpTrades(attachTradesList, logFileHandler, mode='BOTH')
            keepLoop=False # exit while loops after passed 3:30+2 pm,18aug2020

        ### <3:30+2 pm
        else:
            attachTradesList= dt.OcaSell_10a.GLOBAL_records #add here as realtime updates, debug 1mar2021
            positions=ses.positions()
            if not ses.waitOnUpdate(timeout=WAIT_ACK): # Wait on any new update to arrive from the network
                print('Wait too long at A, timeout !, now:'+ datetime.now().strftime('%Y-%b-%d %H:%M'), end=' >' ) #waited over 30s

            delta=25 #minutes
            slots=datetime.now().minute%delta
            if  slots==0 and not printedA: # display each %X mins
                print("Placed orders")
                dt.printListOfGrpTrades(attachTradesList, logFileHandler, mode='BOTH')

                print(f'Total qualfied picked today:{len(placeOrderDf)}, placed-Order:{len(buyIx)}')
                print('Order filled', ses.fills()); print('Order filled', ses.fills(), file=logFileHandler)
                printedA=True; printedB=not printedB #toggle to enable printedB for print totalInvestAmt following
                print('=====================================,wait ~10-20mins\n')
            elif slots ==int(delta/2.6) and not printedB: # mid-point from previous delta boundary
                invested = [[], []]
                if len(positions) > 0:  # debug, have something, not empty
                    for position in positions:
                        amount = position.position * position.avgCost
                        # invested[SYM].append(position.contract.localSymbol) # the stock's symbol& $bought.
                        invested[SYM].append(dt.getSymbol(position.contract)) #14dec2021 debug. the stock's symbol& $bought.
                        invested[AMT].append(amount)

                accValues = ibs.util.df(ses.accountValues(account=''))
                mMargin = float(accValues.query(" tag=='FullMaintMarginReq' & currency=='HKD' ")['value'])
                tmp=todayInvestLimit -totalInvestAmt #budgetBalance
                print("Total Invested Amount:'{:.2f}', fr buyPower:'{:.2f}', InvestLMTBal(-ve:OD):'{:.2f}',"
                      " maintainMargin:'{:.2f}' wait ~10mins".format(totalInvestAmt, buyPower, tmp, mMargin) ) #A12, alternate display at the 3rd min after the %X min
                bodyMsg='[Symbol:HKD]'+f"{list(zip(invested[SYM], invested[AMT]))}"+f" 'PnL updates if exist:'{ses.pnl()}"
                print(bodyMsg) #print email body msg to console first.-

                titleMsg="No Of Stock Held(PartOrFull):'{}', InvestedHKD:'{:.2f}', " \
                   "Balance$:'{:.2f}' fr '{:.2f}' ".format(len(positions), totalInvestAmt, tmp, todayInvestLimit)
                dt.emailAdmin(titleMsg, bodyMsg+ '     From:'+sys.argv[0])
                printedB=True; printedA=not printedA #toggle to enable printedA for printListOfGrpTrades()             

                # Reconnect link if broken due to some reason.
            if ses.isConnected() is not True:
                    ses=dt.connectIB(); print('Reconnecting!') # re-connect IB if broken due to any reason,31jul2020
                    dt.emailAdmin("IB connection broken, reconnecting !", ' From:'+sys.argv[0])
        ### <3:30+2 pm
        
    ###  3:50p > Time > 3:30+2 pm , loop to show stock positions until URGENT sell at 3:50pm; if still has stocks onhand ###
            ##### can't right after for-loop (a) above, coRoutines take time to finish. #####
    takeList, stopList=[], []
    idx=range( len(attachedRoutines) ) #for get all take/stopPercents
    takeList=[attachedRoutines[i].takePercent for i in idx ]; stopList=[attachedRoutines[i].stopPercent for i in idx ]
    tmpD={'TakeProfit':takeList, 'StopLoss':stopList} #creat dict to creat dataframe
    tmpD=pd.DataFrame(tmpD); tmpD.to_csv(dt.getCwdPath()+'takeStopPercents.csv')
    msg='TakeProfit%, StopLoss% used today 1-by-1 in order as show in coming logfileXX.txt .'+ sys.argv[0] #body msg
    dt.noticeTraders(msg, dt.ADM_EMAILS, ['takeStopPercents.csv'], 'Take Stop percents record.')
    # print(msg) #; dt.emailAdmin(msg, '  From:'+sys.argv[0])
            ##### can't right after for-loop (a) above #####
            
    keepLoop=True; printedA=False; printedB=False #control to reduce screen printings frequencies
    while keepLoop: #use a boolean to control the loop for better documentation
        if datetime.now() < timeStopTrades: # < 3:50pm, urgent SELL and stop tradings.
            notTimeOut=ses.waitOnUpdate(timeout=WAIT_ACK) #Wait on any new update to arrive from the network
            if not notTimeOut: print('Wait too long at B, timeout !. Now:'+ datetime.now().strftime('%Y-%b-%d %H:%M'), end=' >')
            if len(closeTrades)>0 and not printedA: # do, if there is something instead of empty, a=[]
                print('\nThe 3:30p replace Market-Trade status:') 
                
                print('\nThe 3:30p replace Market-Trade status:', file=logFileHandler)
                dt.printTradeStatus(closeTrades, logFileHandler, mode='BOTH')
                print("Current Positions: ",ses.positions()); print('\n\n====== Waiting 3:50p .    .  . ...')
                printedA=True
                # ibs.IB.sleep(DIS_TIME-1) #xS for human print viewing purpose, -1sec 6aug2020
            elif len(closeTrades) <=0 and not printedB:
                print('No 3:30p replace Market-order from today placed stocks. Waiting 3:50p...')#; break # exit while loops
                printedB=True

            # Reconnect link if broken due to some reason.
            if ses.isConnected() is not True:
                ses=dt.connectIB(); print('Reconnecting!') # re-connect IB if broken due to any reason,31jul2020
                dt.emailAdmin("IB connection broken, reconnecting !", ' From:'+sys.argv[0])

        else: # TIME == 3:50p
            print("After ", timeStopTrades, ", all today's trades DONE!")
            keepLoop=False # exit while loops after passed 3:50pm,18aug2020

    ### >3:50pm, market close within 1min ###
    print('Double checking any assets on-hand!'); print('Double checking any assets on-hand!', file=logFileHandler)
    stockSymExch, holdStocks=dt.mSureNoStockHolded(ses) # Urgently sell all positions again, before mkt close!
    print(list(zip(stockSymExch, holdStocks))) #holdStocks=list of, no-of-shares hold in a stock
    print(f'Wait {SEHK_CLOSE_MIN - PRE_CLOSE_MIN}min until market really closed .....'); ibs.IB.sleep((SEHK_CLOSE_MIN - PRE_CLOSE_MIN)*60) #4:08pm as SEHK CLOSE

    ### Market Closed, Save&report records ###
    realiszedPnL, UnrealiszedPnL=dt.printAccountKeyValues(ses) #All in HKD
    tomorrowInvestLimit=todayInvestLimit+realiszedPnL # accumlated non-settled (T+2) cash/fund for tomorrow
    m1="Today Investment Limit Used:'{:.2f}', BuyingPower:'{:.2f}', LotsizeUp:'{}', ".format(todayInvestLimit, buyPower, LOT_SIZE_UP)
    m2="PnL:'{:.2f}', PnLUnRe:'{:.2f}', InvestLimit for tomorrow:'{}'".format(realiszedPnL, UnrealiszedPnL, tomorrowInvestLimit)
    print(m1+m2); dt.emailAdmin(m1+m2, ' From:'+sys.argv[0])
    
    cwd=dt.getCwdPath()
    now=datetime.now().strftime('%Y-%b-%d'); print("\nToday's records saved in :", cwd+'prd-outputs\\')
    fileName='accountValues'+now+'.csv' #MUST CSV not xlsx, 14aug2020
    tempDf=ibs.util.df(ses.accountValues(account='')) # log today's account Value
    if isinstance(tempDf, pd.DataFrame):tempDf.loc['account']='UXXX835X'; tempDf.to_csv(cwd+'prd-outputs\\'+fileName); print('Saving:', fileName)  #save if not NoneType/empty

    fileName='executedTrades'+now+'.csv' #MUST CSV not xlsx. 28jul2020 Debug: Excel does not support datetimes with timezones
    tempDf=ibs.util.df(ses.executions()) # log today's order executions
    if isinstance(tempDf, pd.DataFrame):tempDf.loc[:, 'acctNumber']='UXXX835X'; tempDf.to_csv(cwd+'prd-outputs\\'+fileName); print('Saving:', fileName)  #save if not NoneType/empty

    fileName='entryMktTradesRec'+now+'.csv' #MUST CSV not xlsx. 28jul2020 Debug: Excel does not support datetimes with timezones
    tempDf=ibs.util.df(mTrades)
    if isinstance(tempDf, pd.DataFrame): tempDf.to_csv(cwd+'prd-outputs\\'+fileName); print('Saving:', fileName) #save if not NoneType empty

    fileName='closeMktTradesRec'+now+'.csv' #MUST CSV not xlsx. 28jul2020 Debug: Excel does not support datetimes with timezones
    tempDf=ibs.util.df(closeTrades)
    if isinstance(tempDf, pd.DataFrame): tempDf.to_csv(cwd+'prd-outputs\\'+fileName); print('Saving:', fileName) #save if not NoneType empty

    fileName='portfolio On-hand summary, on'+now+'.csv'#MUST CSV not xlsx. 28jul2020 Debug: Excel does not support datetimes with timezones
    tempDf=ibs.util.df(ses.portfolio())
    if isinstance(tempDf, pd.DataFrame):
        tempDf.loc[:, 'account']='UXXX835X'; tempDf.to_csv(cwd+'prd-outputs\\'+fileName); print('Saving:', fileName)  #save if not NoneType empty
    else: print('Sold all on hand, no portfolio-Onhand-summary file saved.')

    logFileHandler.close() #make sure file closed file-buffer before email&exist
    dt.noticeTraders('Today log:'+sys.argv[0], dt.ADM_EMAILS, [logFullPath], 'fr .prd-outputs\ .') #email logfile
    return tomorrowInvestLimit

# ##########              Main Program    #################################
# Check valid SEHK trading stock dates and execute the codes continuously.
# #########################################################################
dt.reRegisterEmail().send(subject="Confirm connected to yagmail.") #make sure rigth login data to yagmail.
gateway =dt.Gateway(ver='981')  #6dec2021=> 981, creat gateway instance for run& later's stop
gateway.run()
mg1=f'Global set:, take profit sell= {dt.TAKE_PERCENT}%,  stop loss sell= {dt.STP_LOSS_PERCENT}%.'; print(mg1)

if TEST1_0: # testMode level-0, ignore start time
    input('Did not check startTime!, IBsync?, go anyway or Ctrl-C to interrupt?')
    ses=dt.connectIB() #19dec2021
    ## /Simulate analysisAllStocks()
    if TEST1_1: pickedAssets=pd.read_excel(EMAIL_FILE, index_col=0); print('Used Excel simulate pickedAssets Df.') # deeper testMode level_1
    else: pickedAssets=analysisAllStocks(ses) #19dec2021. analysis all SEHK stocks, email out and return a pickedStock dataframe.
    # ses=dt.connectIB()
    placeNmonitorOrds(pickedAssets, ses) # place bracket orders for picked stocks. ()[9] is BUDGET_SET

else: #non-testMode base on nextStart time
    dt.emailAdmin("System RESTARTED and running. "+mg1, ' From:'+sys.argv[0]) # running Python code's name.
    nextStart = dt.setTargetRunDateTime(START_HOUR, START_MINUTE, 'SEHK'); print(dt.getCwdPath())

    runCount=0 #init for looping. kLoop=True; 
    while True:
        if datetime.now() > nextStart: # >= to >, 22dec2021
            ses=dt.connectIB(); print(datetime.now().strftime('%Y-%b-%d %H:%M')) #19dec2021
            pickedAssets=analysisAllStocks(ses) #19dec2021. analysis all SEHK stocks, email out and return a pickedStock dataframe.
            if len(pickedAssets) >0: #valid Dataframe, rows X cols >0, at least 1
                dt.strongeBeep(2, NO_SPK) # EC2 & EC2's DOS have not speaker, will raise runtime error
                # ses=dt.connectIB(); print(datetime.now().strftime('%Y-%b-%d %H:%M'))
                dt.emailAdmin("Reconnected to gateway now.", 'From:'+sys.argv[0]) # running Python code's name.

                print('assets Position should start at nothing', end=':'); positions = ses.positions()  # A list[] of positions, according to IB
                map(lambda x: print(x.position, end=': '), positions) #just print holding assets' position, IF ANY.

                cumWkFund=placeNmonitorOrds(pickedAssets, ses) #place today-orders, ret fund accumlated
                # if datetime.now().weekday() ==4: kLoop=False #Fri(4), stop Python if done all weekly tasks
                mg1 =f"Today NAV change to HKD{'{:.1f}'.format(cumWkFund/F_UNITS)}. Be patience, our simulated performance is weekly instead of daily. "
                mg2 ='It started HKD1000 from 1-May-2021. No attached file in this email. '+sys.argv[0] #15dec2021
                print(mg1); dt.noticeTraders(mg1+mg2, MEMBR_EMAILS, [], '.') # No file attached

                print('Ctrl-C,interrupt. Wait 6min further after market closed .....'); ibs.IB.sleep(6*60) #locY 
                dt.disconnectIB(ses)
                print('Disconnected from gateway already.')
                dt.emailAdmin("Done and disconnected from gateway now. Auto restart IBGateway every 4:45pm",
                              'From:'+sys.argv[0]+".  Today's records saved in :"+'..\\prd-outputs') # running Python code's name.
                print( f'Account position:{len(ses.positions())}. This should be zero.' )
            else:
                # dt.emailAdmin('No picked stock today!', 'From:'+sys.argv[0]+'. Market changing too fast, typhoon or else..')
                dt.email2List(BCC_EMAILS, 'No picked stock today!', 'From:'+sys.argv[0]+'. Market changing too fast, typhoon or else..') #5jan2022 after CuEmba trails

                
            # next target run date has to skip Sat,Sun,holiday
            nextStart=dt.setTargetRunDateTime(START_HOUR, START_MINUTE, 'SEHK') # get next START_HOUR:START_MINUTE in a day, HK Exchange
            runCount+=1; print('Today is: ', datetime.now().strftime('%A'))
        # Go to nextday's setups if not Friday.
        now=datetime.now()
        if now.weekday() ==4 and now.hour >= 16: # at least 4pm
            break #Fri(4)& >=5pm, stop Python if done all weekly tasks
                  #EC2 will shutdown after 6pm, 8nov2020
        else:
            diffSeconds=(nextStart-now).total_seconds(); diffSeconds=diffSeconds//20 #fallback 1/20 eachLoop. int/floor div. X//2&X//10 too small,12Oct2020
            if diffSeconds <15: diffSeconds=15 #if small than 0.25min(15s), check again in 15s
            print('       Everyday will reset IB-gateway HKT-4:45pm after SEHK closed, but keep running onward.')
            print('Ran:',runCount,'. Sleep ', '{:.2f}'.format(diffSeconds/60), 'mins before check again.')
            ibs.IB.sleep(diffSeconds) #wait at least 15s but can thousand seconds to check again
        # loop the While-Loop, with new cymWkFund-investmentLimit for next trade-day.

    # come here if Friday
    print('Program Ended Normally on Fri, need restart on Mon.')
    dt.emailAdmin("Program Ended on Fri, please RESTART EC2 on Mon.", 'From:'+sys.argv[0]) # running Python code's name.
    if REMIND_G: dt.emailAdmin("Hi Grace. Kindly reminder: did you update/fix necessary stuffs for me?", 'From:'+sys.argv[0])
    dt.disconnectIB(ses); gateway.stop()
##########        Main END    ####################

""" Reference A:
1) re.split(): https://note.nkmk.me/en/python-split-rsplit-splitlines-re/
2) "{0}{1}{2}".format(a,b,c): https://docs.python.org/3/library/string.html#string-formatting
3) StyleFrame API: https://readthedocs.org/projects/styleframe/downloads/pdf/latest/
4) datetime.replace(): https://pythontic.com/datetime/datetime/replace
5) datatime format: https://strftime.org/
6) pause until(): https://github.com/jgillick/python-pause
7) add col to existing DF by list: https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
8) https://github.com/DeepSpace2/StyleFrame/issues/61
9) gDown url issue: https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
10) pd.drop_duplicates():  https://www.geeksforgeeks.org/python-pandas-dataframe-drop_duplicates/
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop_duplicates.html
11) dropna before check empty: https://pandas.pydata.org/pandas-docs/version/0.18.1/generated/pandas.DataFrame.empty.html
12) print(f''): http://zetcode.com/python/fstring/
13) pandas concat() : #https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
14) pandas apply() : https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.apply.html
15) pd.merge() as vLookUp:
    https://www.geeksforgeeks.org/how-to-do-a-vlookup-in-python-using-pandas/
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html
    https://pythonhealthcare.org/2018/04/05/28-using-pandas-to-merge-or-lookup-data/
16) RMB/USD SEHK securities:
    https://www.hkex.com.hk/products/securities/equities?sc_lang=en
    https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Stock-Code-Allocation-Plan/scap.pdf
17) .APPLY(Df, args=(x,)):  https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.apply.html
18) 13 OrderStatus: https://trade-commander.com/tc_forum/viewtopic.php?t=40
                    https://www.interactivebrokers.com/en/software/tws/usersguidebook/realtimeactivitymonitoring/order_status_colors.htm
19) pd.query(): https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/   
20) Max msg/second: https://interactivebrokers.github.io/tws-api/order_limitations.html
    Related artical: https://ibkr.info/article/1765 
     ib_insynce discussion: https://groups.io/g/insync/topic/max_rate_of_messages/6390099?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,6390099   
21) df.value_counts(): https://www.geeksforgeeks.org/python-pandas-index-value_counts/ """