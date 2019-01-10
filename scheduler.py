import schedule
import time
import trader
import analyzer
import tweeter
import db.db as db
import api.oanda_api as oanda_api

trader = trader.Trader()

def trader_loop():
    trader.loop()

def analyzer_loop():
    analyzer.loop()

def tweeter_loop():
    tweeter.post_trade_tweets()

def activate():
    #最初にfxタグのスケジュールをクリアする
    schedule.clear('fx')
    if oanda_api.is_market_open():
        #fxタグのスケジュールを登録
        schedule.every(10).seconds.do(analyzer_loop).tag('fx')
        schedule.every(10).seconds.do(trader_loop).tag('fx')
        schedule.every(60).seconds.do(tweeter_loop).tag('fx')

def deactivate():
    trader.exit()
    schedule.clear('fx')

def delete_old_log():
    db.delete_old_log()

def update_long_price_data():
    analyzer.update_long_price_data()

def pl_tweet():
    tweeter.post_pl_tweet()

#このファイル最初の実行時にactivateを実行
activate()

#日〜木23:00UTC(月〜金08:00JST)にactivateを実行
schedule.every().sunday.at('23:00').do(activate)
schedule.every().monday.at('23:00').do(activate)
schedule.every().tuesday.at('23:00').do(activate)
schedule.every().wednesday.at('23:00').do(activate)
schedule.every().thursday.at('23:00').do(activate)

#金曜20:00UTC(土曜05:00JST)にdeactivateを実行
schedule.every().friday.at('20:00').do(deactivate)

#情報更新とか
schedule.every().day.at('22:00').do(update_long_price_data)
schedule.every().friday.at('20:00').do(delete_old_log)
schedule.every().saturday.at('00:00').do(pl_tweet)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        db.write_log('exception', str(e))
        continue
