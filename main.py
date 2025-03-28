# main.py
from flask import Flask, request, jsonify, send_file, render_template
from data_handler import collect_and_process
from lda_model import train_lda_with_embeddings
from visualizer import plot_topic_trends, visualize_lda
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Render the template with Jinja2

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    hashtag = data.get('hashtag', '').strip()
    num_topics = int(data.get('num_topics', 5))
    
    print(f"Starting pipeline for #{hashtag}...")
    processed_file, df = collect_and_process(hashtag, max_tweets=1000)
    if processed_file is None:
        return jsonify({"error": "No data collected."}), 400
    
    lda_model, corpus, dictionary, df = train_lda_with_embeddings(df, num_topics)
    if not lda_model:
        return jsonify({"error": "Topic modeling failed."}), 500
    
    topics_file = processed_file.replace(".csv", "_with_topics.csv")
    df.to_csv(topics_file, index=False)
    
    # Generate visualizations
    plot_topic_trends(df, lda_model, hashtag)
    visualize_lda(lda_model, corpus, dictionary, hashtag)
    
    return jsonify({
        "message": "Processing complete!",
        "topics_file": topics_file,
        "trends_image": f"{hashtag}_topic_trends.png",
        "lda_html": f"{hashtag}_lda_visualization.html"
    })

@app.route('/results/<filename>')
def serve_file(filename):
    return send_file(filename)  # Serve generated files directly from the root directory

if __name__ == "__main__":
    app.run(debug=True, port=5000)