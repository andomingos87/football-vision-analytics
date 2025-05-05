from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
import cv2
import numpy as np
import uuid
from datetime import datetime
import time

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov'}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        flash('Nenhum arquivo enviado')
        return redirect(request.url)
    
    file = request.files['video']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Criar nome de arquivo único
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        upload_path = os.path.join('app/static/uploads', filename)
        file.save(upload_path)
        
        # Redirecionar para a página de processamento
        return redirect(url_for('main.process_video', filename=filename))
    
    flash('Formato de arquivo não permitido. Use MP4 ou MOV.')
    return redirect(request.url)

@main.route('/process/<filename>')
def process_video(filename):
    return render_template('processing.html', filename=filename)

@main.route('/analyze/<filename>', methods=['POST'])
def analyze_video(filename):
    # Caminho para o vídeo
    video_path = os.path.join('app/static/uploads', filename)
    
    # Criar diretório para resultados se não existir
    results_dir = os.path.join('app/static/results', os.path.splitext(filename)[0])
    os.makedirs(results_dir, exist_ok=True)
    
    # Importar o processador de vídeo
    from .processor import process_football_video
    
    # Iniciar processamento
    # Na versão final, isso seria feito em uma thread separada ou com Celery
    result = process_football_video(video_path, results_dir)
    
    return jsonify(result)

@main.route('/results/<result_id>')
def show_results(result_id):
    return render_template('results.html', result_id=result_id)

# Função removida e substituída pelo módulo processor.py
