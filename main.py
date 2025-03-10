# main.py
from data_handler import collect_and_process
from lda_model import train_lda_with_embeddings
from visualizer import plot_topic_trends, visualize_lda

def main():
    user_hashtag = input("Enter a hashtag (without #): ").strip()
    print(f"Starting pipeline for #{user_hashtag}...")
    
    processed_file, df = collect_and_process(user_hashtag, max_tweets=1000)
    if processed_file is None:
        print("No data collected. Exiting.")
        return
    
    num_topics = int(input("Enter the number of topics (default is 5): ") or 5)
    lda_model, corpus, dictionary, df = train_lda_with_embeddings(df, num_topics)
    if lda_model:
        topics_file = processed_file.replace(".csv", "_with_topics.csv")
        df.to_csv(topics_file, index=False)
        print(f"✅ Data with topics saved to {topics_file}")
        
        plot_topic_trends(df, lda_model, user_hashtag)  # Pass lda_model here
        visualize_lda(lda_model, corpus, dictionary, user_hashtag)
    else:
        print("Topic modeling failed. Exiting.")

if __name__ == "__main__":
    main()