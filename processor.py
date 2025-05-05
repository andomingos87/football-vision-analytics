from analyzer import FootballAnalyzer

def process_football_video(video_path, results_dir):
    """
    Função principal para processar o vídeo de futebol e extrair métricas
    
    Args:
        video_path: Caminho para o vídeo
        results_dir: Diretório para salvar os resultados
        
    Returns:
        dict: Dicionário com os resultados da análise
    """
    # Inicializar o analisador
    analyzer = FootballAnalyzer()
    
    # Processar o vídeo (limitando a 300 frames para o MVP)
    result = analyzer.process_video(video_path, results_dir, max_frames=300)
    
    return result
