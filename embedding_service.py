#!/usr/bin/env python3

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)

# 모델 로드
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")

@app.route('/embed', methods=['POST'])
def embed():
    try:
        data = request.json
        inputs = data.get('inputs', '')

        if not inputs:
            return jsonify({"error": "No inputs provided"}), 400

        # 임베딩 생성
        embeddings = model.encode([inputs])
        return jsonify(embeddings.tolist())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': 'all-MiniLM-L6-v2'})

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'embedding-service',
        'model': 'all-MiniLM-L6-v2',
        'endpoints': ['/embed', '/health']
    })

if __name__ == '__main__':
    print("Starting embedding service on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)