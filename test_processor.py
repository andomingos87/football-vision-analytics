import os
import sys
from app.analyzer import FootballAnalyzer

def download_sample_video():
    """
    Baixa um vídeo de exemplo para testes se não existir
    
    Returns:
        str: Caminho para o vídeo de exemplo
    """
    import requests
    from tqdm import tqdm
    
    # Diretório para salvar o vídeo
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Caminho para o vídeo
    video_path = os.path.join(data_dir, 'sample_football.mp4')
    
    # Se o vídeo já existe, retornar o caminho
    if os.path.exists(video_path):
        print(f"Vídeo de exemplo já existe em: {video_path}")
        return video_path
    
    # URL para um vídeo de exemplo de futebol (curto, para testes)
    # Este é um exemplo de URL, pode ser substituído por outro vídeo de futebol
    url = "https://github.com/opencv/opencv_extra/raw/master/testdata/cv/tracking/david/data/david.webm"
    
    print(f"Baixando vídeo de exemplo de: {url}")
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(video_path, 'wb') as f, tqdm(
            desc="Baixando vídeo",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
        
        print(f"Vídeo baixado com sucesso para: {video_path}")
        return video_path
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None

def test_video_processing():
    """
    Testa o processamento de vídeo com um vídeo de exemplo
    """
    # Baixar vídeo de exemplo
    video_path = download_sample_video()
    if not video_path:
        print("Não foi possível baixar o vídeo de exemplo.")
        return
    
    # Diretório para resultados
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"Processando vídeo: {video_path}")
    print(f"Resultados serão salvos em: {results_dir}")
    
    # Inicializar o analisador
    analyzer = FootballAnalyzer()
    
    # Processar o vídeo (limitando a 100 frames para teste rápido)
    result = analyzer.process_video(video_path, results_dir, max_frames=100)
    
    print("\nResultados do processamento:")
    print(f"Frames processados: {result['frames_processed']}")
    print(f"Duração do processamento: {result['duration']:.2f} segundos")
    print(f"Posse de bola: Time 1 = {result['metrics']['ball_possession']['team1']}%, Time 2 = {result['metrics']['ball_possession']['team2']}%")
    print(f"Passes: Time 1 = {result['metrics']['passes']['team1']}, Time 2 = {result['metrics']['passes']['team2']}")
    print(f"Chutes: Time 1 = {result['metrics']['shots']['team1']}, Time 2 = {result['metrics']['shots']['team2']}")
    print(f"Gols: Time 1 = {result['metrics']['goals']['team1']}, Time 2 = {result['metrics']['goals']['team2']}")
    print(f"Vídeo de saída: {result['output_video']}")
    print(f"Frames-chave: {len(result['charts'])}")
    
    print("\nTeste concluído com sucesso!")

if __name__ == "__main__":
    test_video_processing()
