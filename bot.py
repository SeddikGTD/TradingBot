import requests
import pandas as pd
import pandas_ta as ta
import time

# === إعدادات التليجرام ===
TELEGRAM_TOKEN = "8687498302:AAGg0pQEwDYN0btt7sxDq1lL9QjlQLAL3aY"
CHAT_ID = "8687498302"
SYMBOL = "EURUSDT" # تغيير طفيف ليتوافق مع بينانس
TIMEFRAME = "1m"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ في التليجرام: {e}")

def analyze_market():
    try:
        # جلب البيانات مباشرة من Binance API (بدون ccxt)
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={TIMEFRAME}&limit=100"
        response = requests.get(url)
        data = response.json()
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                          'close_time', 'quote_asset_volume', 'number_of_trades', 
                                          'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        
        # حساب المؤشرات
        df['rsi'] = ta.rsi(df['close'], length=14)
        bb = ta.bbands(df['close'], length=20, std=2)
        df = df.join(bb)
        
        last_candle = df.iloc[-2]
        current_price = last_candle['close']
        rsi = last_candle['rsi']
        lower_bb = last_candle['BBL_20_2.0']
        upper_bb = last_candle['BBU_20_2.0']
        
        signal = None
        
        if rsi < 30 and current_price <= lower_bb:
            signal = "UP ⬆️"
        elif rsi > 70 and current_price >= upper_bb:
            signal = "DOWN ⬇️"
            
        return signal, rsi
        
    except Exception as e:
        print(f"خطأ في جلب البيانات: {e}")
        return None, None

def main():
    print("🤖 البوت السحابي الخفيف يعمل الآن... يراقب السوق!")
    send_telegram_message("☁️ *تم تشغيل البوت السحابي الخفيف بنجاح!*\nيراقب زوج _" + SYMBOL + "_")
    
    last_signal_time = 0
    
    while True:
        try:
            current_time = time.time()
            if current_time - last_signal_time >= 60:
                signal, rsi_value = analyze_market()
                
                if signal:
                    message = (
                        f"🚀 *إشارة سحابية (BOT SIGNAL)* 🚀\n\n"
                        f"الاتجاه: *{signal}*\n"
                        f"الزوج: _{SYMBOL}_\n"
                        f"قيمة RSI: {rsi_value:.2f}\n"
                        f"المدة: 1 دقيقة\n\n"
                        f"⏳ اذهب لمنصة Binomo الآن!"
                    )
                    send_telegram_message(message)
                    print(f"تم إرسال إشارة: {signal}")
                    last_signal_time = current_time
                else:
                    print(f"لا فرصة حالياً. RSI: {rsi_value:.2f}")
                    
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("تم إيقاف البوت.")
            break
        except:
            time.sleep(30)

if __name__ == "__main__":
    main()
