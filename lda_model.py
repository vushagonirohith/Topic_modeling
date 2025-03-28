import pandas as pd
import numpy as np
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize

def train_lda_with_embeddings(df, num_topics=5, embedding_size=100):
    tokenized_docs = [word_tokenize(tweet.lower()) for tweet in df['Processed_Tweet'].dropna()]
    if not tokenized_docs:
        print("No valid documents found for topic modeling.")
        return None, None, None, df
    
    # Train Word2Vec model for embeddings
    word2vec_model = Word2Vec(
        sentences=tokenized_docs,
        vector_size=embedding_size,
        window=5,
        min_count=1,
        workers=4,
        sg=1
    )
    
    # Create dictionary and BoW corpus (LDA still needs this)
    dictionary = corpora.Dictionary(tokenized_docs)
    corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
    
    # Train LDA model
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=10
    )
    
    print("\nDiscovered Topics:")
    for idx, topic in lda_model.print_topics(-1):
        print(f"Topic {idx + 1}: {topic}")
    
    df['Dominant_Topic'] = [max(lda_model[corpus[i]], key=lambda x: x[1])[0] if corpus[i] else -1 
                           for i in range(len(corpus))]
    
    return lda_model, corpus, dictionary, df

if __name__ == "__main__":
    input_file = input("Enter the processed CSV file (e.g., AI_tweets_processed.csv): ").strip()
    df = pd.read_csv(input_file)
    num_topics = int(input("Enter the number of topics (default is 5): ") or 5)
    lda_model, corpus, dictionary, df = train_lda_with_embeddings(df, num_topics)
    if lda_model:
        output_file = input_file.replace(".csv", "_with_topics.csv")
        df.to_csv(output_file, index=False)
        print(f"✅ Data with topics saved to {output_file}")