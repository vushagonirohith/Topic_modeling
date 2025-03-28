from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

# Download required NLTK data (run once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def scrape_twitter(hashtag, max_tweets=1000, scroll_pause=3):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    dr = webdriver.Chrome(options=options)
    url = f"https://x.com/i/flow/login?redirect_after_login=%2Fsearch%3Fq%3D%2523{hashtag}%26src%3Dtyped_query%26f%3Dlive"
    dr.get(url)
    
    try:
        WebDriverWait(dr, 15).until(EC.presence_of_element_located((By.XPATH, "//input[@name='text']")))
        username = dr.find_element(By.XPATH, "//input[@name='text']")
        username.send_keys('Vishakha259816')  # Replace with your Twitter username
        dr.find_element(By.XPATH, "//button[2]").click()
        
        WebDriverWait(dr, 15).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
        password = dr.find_element(By.XPATH, "//input[@name='password']")
        password.send_keys('Vishakha@123')  # Replace with your Twitter password
        dr.find_element(By.XPATH, "//button[@data-testid='LoginForm_Login_Button']").click()
        
        WebDriverWait(dr, 30).until(EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))
    except Exception as e:
        print(f"Login failed: {e}")
        dr.quit()
        return None

    tweet_data = set()
    last_height = dr.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_attempts = 5
    
    while len(tweet_data) < max_tweets and scroll_attempts < max_attempts:
        tweets = dr.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        for tweet in tweets:
            try:
                username = tweet.find_element(By.XPATH, ".//span[contains(text(), '@')]").text
                content = tweet.find_element(By.XPATH, ".//div[@lang]").text
                timestamp = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
                tweet_data.add((username, content, timestamp))
                if len(tweet_data) >= max_tweets:
                    break
            except:
                continue
        
        print(f"Collected {len(tweet_data)}/{max_tweets} unique tweets")
        dr.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause + random.uniform(0, 2))
        
        new_height = dr.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            print(f"No new content loaded (Attempt {scroll_attempts}/{max_attempts})")
        else:
            scroll_attempts = 0
            last_height = new_height
    
    dr.quit()
    
    tweet_list = [{"Username": t[0], "Tweet": t[1], "Timestamp": t[2]} for t in tweet_data]
    df = pd.DataFrame(tweet_list)
    raw_file = f"{hashtag}_tweets.csv"
    df.to_csv(raw_file, index=False)
    print(f"✅ Scraping complete! Collected {len(tweet_data)} unique tweets. Saved to {raw_file}")
    return df

def preprocess_for_lda(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"@\w+|#\w+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    tokens = [word for word in tokens if len(word) > 2]
    return " ".join(tokens)

def process_tweets(df, hashtag):
    df['Processed_Tweet'] = df['Tweet'].apply(preprocess_for_lda)
    processed_file = f"{hashtag}_tweets_processed.csv"
    df.to_csv(processed_file, index=False)
    print(f"✅ Preprocessed data saved to {processed_file}")
    print("\nSample of Original vs Preprocessed Tweets:")
    print(df[['Username', 'Tweet', 'Processed_Tweet']].head())
    return processed_file, df

def collect_and_process(hashtag, max_tweets=1000):
    print(f"Starting data collection for #{hashtag}...")
    df = scrape_twitter(hashtag, max_tweets)
    if df is None or df.empty:
        print("No data collected. Exiting.")
        return None, None
    processed_file, df = process_tweets(df, hashtag)
    return processed_file, df

if __name__ == "__main__":
    hashtag = input("Enter a hashtag (without #): ").strip()
    collect_and_process(hashtag)