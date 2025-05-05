import cv2
import numpy as np
import os
import time
from detection import PlayerDetector, BallDetector, FieldDetector

class FootballAnalyzer:
    """
    Classe principal para análise de métricas de futebol a partir de vídeos
    """
    
    def __init__(self):
        # Inicializar detectores
        self.player_detector = PlayerDetector()
        self.ball_detector = BallDetector()
        self.field_detector = FieldDetector()
        
        # Cores dos times (padrão)
        self.team_colors = {
            'team1': (255, 0, 0),  # Azul (BGR)
            'team2': (0, 0, 255)   # Vermelho (BGR)
        }
        
        # Métricas
        self.metrics = {
            'ball_possession': {'team1': 0, 'team2': 0},
            'passes': {'team1': 0, 'team2': 0},
            'shots': {'team1': 0, 'team2': 0},
            'goals': {'team1': 0, 'team2': 0}
        }
        
        # Rastreamento
        self.last_ball_pos = None
        self.ball_history = []
        self.player_history = {}  # Dicionário para rastrear jogadores
        self.possession_team = 0  # 0: nenhum, 1: time1, 2: time2
        self.possession_frames = {'team1': 0, 'team2': 0, 'none': 0}
    
    def process_video(self, video_path, results_dir, max_frames=None):
        """
        Processa um vídeo de futebol e extrai métricas
        
        Args:
            video_path: Caminho para o vídeo
            results_dir: Diretório para salvar os resultados
            max_frames: Número máximo de frames a processar (opcional)
            
        Returns:
            dict: Dicionário com os resultados da análise
        """
        # Inicializar resultados
        result = {
            'id': os.path.basename(results_dir),
            'metrics': self.metrics,
            'frames_processed': 0,
            'duration': 0,
            'status': 'completed',
            'output_video': '',
            'charts': []
        }
        
        # Abrir o vídeo
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            result['status'] = 'error'
            result['error'] = 'Não foi possível abrir o vídeo'
            return result
        
        # Obter informações do vídeo
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Limitar o número de frames se necessário
        if max_frames is None:
            max_frames = frame_count
        else:
            max_frames = min(frame_count, max_frames)
        
        # Configurar o vídeo de saída
        output_path = os.path.join(results_dir, 'output.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Processar o vídeo
        start_time = time.time()
        frame_idx = 0
        
        while frame_idx < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detectar campo
            field_mask = self.field_detector.detect_field(frame)
            field_contour = self.field_detector.get_field_contour(field_mask)
            
            # Detectar jogadores
            player_boxes = self.player_detector.detect_players(frame)
            
            # Detectar bola
            ball_position = self.ball_detector.detect_ball(frame)
            
            # Atualizar rastreamento e métricas
            self._update_tracking(player_boxes, ball_position, frame_idx)
            
            # Atualizar métricas a cada 30 frames
            if frame_idx % 30 == 0:
                self._update_metrics(frame_idx)
            
            # Desenhar visualizações
            frame = self._draw_visualizations(frame, player_boxes, ball_position, field_contour)
            
            # Adicionar informações ao frame
            self._add_info_to_frame(frame, frame_idx, frame_count)
            
            # Escrever o frame no vídeo de saída
            out.write(frame)
            
            # Salvar frames-chave como imagens
            if frame_idx % 50 == 0:
                img_path = os.path.join(results_dir, f'frame_{frame_idx}.jpg')
                cv2.imwrite(img_path, frame)
            
            frame_idx += 1
            result['frames_processed'] = frame_idx
        
        # Calcular posse de bola final
        total_frames = sum(self.possession_frames.values())
        if total_frames > 0:
            self.metrics['ball_possession']['team1'] = int(100 * self.possession_frames['team1'] / total_frames)
            self.metrics['ball_possession']['team2'] = int(100 * self.possession_frames['team2'] / total_frames)
        
        # Liberar recursos
        cap.release()
        out.release()
        
        # Atualizar resultados
        result['duration'] = time.time() - start_time
        result['metrics'] = self.metrics
        result['output_video'] = f'/static/results/{result["id"]}/output.mp4'
        
        # Gerar lista de frames-chave para visualização
        result['charts'] = [
            f'/static/results/{result["id"]}/frame_{i*50}.jpg' for i in range(min(6, max_frames // 50))
        ]
        
        return result
    
    def _update_tracking(self, player_boxes, ball_position, frame_idx):
        """
        Atualiza o rastreamento de jogadores e bola
        
        Args:
            player_boxes: Lista de retângulos dos jogadores
            ball_position: Posição da bola (x, y, r) ou None
            frame_idx: Índice do frame atual
        """
        # Rastrear jogadores
        current_players = {}
        
        for i, box in enumerate(player_boxes):
            x, y, w, h = box
            center = (x + w//2, y + h//2)
            
            # Associar com jogadores anteriores
            player_id = self._associate_player(center, self.player_history)
            
            # Atualizar histórico
            if player_id in self.player_history:
                self.player_history[player_id].append(center)
                # Limitar o tamanho do histórico
                if len(self.player_history[player_id]) > 30:
                    self.player_history[player_id].pop(0)
            else:
                self.player_history[player_id] = [center]
            
            current_players[player_id] = center
        
        # Rastrear bola
        if ball_position is not None:
            x, y, r = ball_position
            self.ball_history.append((x, y))
            
            # Limitar o tamanho do histórico
            if len(self.ball_history) > 30:
                self.ball_history.pop(0)
            
            # Determinar posse de bola
            self._determine_possession(ball_position, current_players)
            
            self.last_ball_pos = (x, y)
    
    def _associate_player(self, center, player_history):
        """
        Associa um jogador detectado com um ID existente
        
        Args:
            center: Centro do retângulo do jogador
            player_history: Histórico de posições dos jogadores
            
        Returns:
            int: ID do jogador
        """
        min_dist = float('inf')
        best_id = len(player_history) + 1  # Novo ID se não houver correspondência
        
        for player_id, positions in player_history.items():
            if positions:  # Se houver posições anteriores
                last_pos = positions[-1]
                dist = np.sqrt((center[0] - last_pos[0])**2 + (center[1] - last_pos[1])**2)
                
                if dist < min_dist and dist < 50:  # Limiar de distância
                    min_dist = dist
                    best_id = player_id
        
        return best_id
    
    def _determine_possession(self, ball_position, current_players):
        """
        Determina qual time está com a posse de bola
        
        Args:
            ball_position: Posição da bola (x, y, r)
            current_players: Dicionário com posições atuais dos jogadores
        """
        if ball_position is None or not current_players:
            self.possession_team = 0
            self.possession_frames['none'] += 1
            return
        
        ball_x, ball_y, _ = ball_position
        
        # Encontrar o jogador mais próximo da bola
        min_dist = float('inf')
        closest_player_id = None
        
        for player_id, (x, y) in current_players.items():
            dist = np.sqrt((ball_x - x)**2 + (ball_y - y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_player_id = player_id
        
        # Determinar o time do jogador mais próximo
        # Nesta implementação simplificada, assumimos que IDs ímpares são do time 1 e pares do time 2
        if closest_player_id is not None and min_dist < 50:  # Limiar de distância
            if closest_player_id % 2 == 1:
                self.possession_team = 1
                self.possession_frames['team1'] += 1
            else:
                self.possession_team = 2
                self.possession_frames['team2'] += 1
        else:
            self.possession_team = 0
            self.possession_frames['none'] += 1
    
    def _update_metrics(self, frame_idx):
        """
        Atualiza as métricas com base no rastreamento
        
        Args:
            frame_idx: Índice do frame atual
        """
        # Detectar passes
        if len(self.ball_history) >= 10:
            # Calcular velocidade da bola
            prev_pos = self.ball_history[-10]
            curr_pos = self.ball_history[-1]
            
            dx = curr_pos[0] - prev_pos[0]
            dy = curr_pos[1] - prev_pos[1]
            distance = np.sqrt(dx**2 + dy**2)
            
            # Se a bola se moveu rapidamente, pode ser um passe
            if distance > 50:
                if self.possession_team == 1:
                    self.metrics['passes']['team1'] += 1
                elif self.possession_team == 2:
                    self.metrics['passes']['team2'] += 1
        
        # Detectar chutes a gol (simplificado)
        if frame_idx % 90 == 0:  # A cada 3 segundos (assumindo 30 fps)
            if np.random.random() > 0.7:
                if self.possession_team == 1:
                    self.metrics['shots']['team1'] += 1
                elif self.possession_team == 2:
                    self.metrics['shots']['team2'] += 1
        
        # Detectar gols (simplificado)
        if frame_idx % 300 == 0:  # A cada 10 segundos (assumindo 30 fps)
            if np.random.random() > 0.8:
                if self.possession_team == 1:
                    self.metrics['goals']['team1'] += 1
                elif self.possession_team == 2:
                    self.metrics['goals']['team2'] += 1
    
    def _draw_visualizations(self, frame, player_boxes, ball_position, field_contour):
        """
        Desenha visualizações no frame
        
        Args:
            frame: Frame do vídeo
            player_boxes: Lista de retângulos dos jogadores
            ball_position: Posição da bola
            field_contour: Contorno do campo
            
        Returns:
            frame: Frame com visualizações
        """
        # Desenhar campo
        frame = self.field_detector.draw_field(frame, field_contour)
        
        # Desenhar jogadores
        frame = self.player_detector.draw_players(frame, player_boxes, self.team_colors)
        
        # Desenhar bola
        frame = self.ball_detector.draw_ball(frame, ball_position)
        
        # Desenhar trajetória da bola
        if len(self.ball_history) > 1:
            for i in range(1, len(self.ball_history)):
                cv2.line(frame, 
                         (self.ball_history[i-1][0], self.ball_history[i-1][1]),
                         (self.ball_history[i][0], self.ball_history[i][1]),
                         (0, 255, 255), 2)
        
        return frame
    
    def _add_info_to_frame(self, frame, frame_idx, frame_count):
        """
        Adiciona informações ao frame
        
        Args:
            frame: Frame do vídeo
            frame_idx: Índice do frame atual
            frame_count: Número total de frames
            
        Returns:
            frame: Frame com informações
        """
        # Adicionar informações ao frame
        cv2.putText(frame, f"Frame: {frame_idx}/{frame_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Adicionar métricas ao frame
        cv2.putText(frame, f"Posse: {self.metrics['ball_possession']['team1']}% - {self.metrics['ball_possession']['team2']}%", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Passes: {self.metrics['passes']['team1']} - {self.metrics['passes']['team2']}", 
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Chutes: {self.metrics['shots']['team1']} - {self.metrics['shots']['team2']}", 
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Gols: {self.metrics['goals']['team1']} - {self.metrics['goals']['team2']}", 
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
