import cv2
import numpy as np
import os

class PlayerDetector:
    """
    Classe para detecção de jogadores em vídeos de futebol usando OpenCV
    """
    
    def __init__(self):
        # Parâmetros para detecção de jogadores
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, 
            varThreshold=16, 
            detectShadows=False
        )
        
        # Parâmetros para filtragem de contornos
        self.min_contour_area = 500  # Área mínima para considerar um contorno como jogador
        self.max_contour_area = 10000  # Área máxima para evitar detecções muito grandes
        
        # Kernel para operações morfológicas
        self.kernel = np.ones((5, 5), np.uint8)
    
    def detect_players(self, frame):
        """
        Detecta jogadores em um frame usando subtração de fundo e análise de contornos
        
        Args:
            frame: Frame do vídeo (imagem BGR)
            
        Returns:
            list: Lista de retângulos (x, y, w, h) representando os jogadores detectados
        """
        # Aplicar desfoque para reduzir ruído
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # Aplicar subtração de fundo
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Aplicar operações morfológicas para melhorar a máscara
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área
        player_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_contour_area < area < self.max_contour_area:
                x, y, w, h = cv2.boundingRect(contour)
                # Verificar proporção altura/largura para filtrar objetos não-humanos
                if 1.5 < h/w < 4.0:  # Proporção típica de uma pessoa em pé
                    player_boxes.append((x, y, w, h))
        
        return player_boxes
    
    def draw_players(self, frame, player_boxes, team_colors=None):
        """
        Desenha retângulos ao redor dos jogadores detectados
        
        Args:
            frame: Frame do vídeo
            player_boxes: Lista de retângulos (x, y, w, h)
            team_colors: Dicionário com cores para cada time (opcional)
            
        Returns:
            frame: Frame com as marcações
        """
        for i, (x, y, w, h) in enumerate(player_boxes):
            # Cor padrão (verde)
            color = (0, 255, 0)
            
            # Se as cores dos times forem fornecidas, tentar classificar o jogador
            if team_colors is not None:
                # Extrair região do jogador
                player_roi = frame[y:y+h, x:x+w]
                
                # Classificar o jogador com base na cor predominante
                team_id = self._classify_player_team(player_roi, team_colors)
                
                # Definir cor com base no time
                if team_id == 1:
                    color = (255, 0, 0)  # Time 1 (azul)
                elif team_id == 2:
                    color = (0, 0, 255)  # Time 2 (vermelho)
            
            # Desenhar retângulo
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Adicionar ID do jogador
            cv2.putText(frame, f"Player {i+1}", (x, y-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def _classify_player_team(self, player_roi, team_colors):
        """
        Classifica um jogador em um dos times com base na cor predominante
        
        Args:
            player_roi: Região da imagem contendo o jogador
            team_colors: Dicionário com cores para cada time
            
        Returns:
            int: ID do time (1 ou 2) ou 0 se não for possível classificar
        """
        # Verificar se a ROI é válida
        if player_roi.size == 0:
            return 0
        
        # Converter para HSV para melhor análise de cores
        hsv_roi = cv2.cvtColor(player_roi, cv2.COLOR_BGR2HSV)
        
        # Calcular histograma de cores
        hist_h = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv_roi], [1], None, [256], [0, 256])
        
        # Encontrar cor predominante
        h_max_val = np.argmax(hist_h)
        s_max_val = np.argmax(hist_s)
        
        # Comparar com as cores dos times
        team1_h, team1_s, _ = cv2.split(cv2.cvtColor(np.uint8([[team_colors['team1']]]), cv2.COLOR_BGR2HSV))
        team2_h, team2_s, _ = cv2.split(cv2.cvtColor(np.uint8([[team_colors['team2']]]), cv2.COLOR_BGR2HSV))
        
        # Calcular distâncias
        dist_team1 = abs(h_max_val - team1_h[0][0]) + abs(s_max_val - team1_s[0][0])
        dist_team2 = abs(h_max_val - team2_h[0][0]) + abs(s_max_val - team2_s[0][0])
        
        # Classificar com base na menor distância
        if dist_team1 < dist_team2 and dist_team1 < 50:  # Limiar de distância
            return 1
        elif dist_team2 < dist_team1 and dist_team2 < 50:
            return 2
        else:
            return 0  # Não foi possível classificar (pode ser árbitro, goleiro, etc.)

class BallDetector:
    """
    Classe para detecção da bola em vídeos de futebol usando OpenCV
    """
    
    def __init__(self):
        # Parâmetros para detecção da bola
        self.min_ball_radius = 5
        self.max_ball_radius = 20
        
        # Parâmetros para detecção de círculos usando Hough
        self.param1 = 50  # Sensibilidade
        self.param2 = 30  # Limiar de acumulação
    
    def detect_ball(self, frame):
        """
        Detecta a bola em um frame usando transformada de Hough para círculos
        
        Args:
            frame: Frame do vídeo (imagem BGR)
            
        Returns:
            tuple: Coordenadas (x, y) e raio da bola, ou None se não for detectada
        """
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar desfoque para reduzir ruído
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detectar círculos usando a transformada de Hough
        circles = cv2.HoughCircles(
            blurred, 
            cv2.HOUGH_GRADIENT, 
            dp=1, 
            minDist=50, 
            param1=self.param1, 
            param2=self.param2, 
            minRadius=self.min_ball_radius, 
            maxRadius=self.max_ball_radius
        )
        
        # Verificar se algum círculo foi detectado
        if circles is not None:
            # Converter para inteiros
            circles = np.uint16(np.around(circles))
            
            # Retornar o primeiro círculo detectado (assumindo que é a bola)
            x, y, r = circles[0, 0]
            return (x, y, r)
        
        return None
    
    def draw_ball(self, frame, ball_position):
        """
        Desenha um círculo ao redor da bola detectada
        
        Args:
            frame: Frame do vídeo
            ball_position: Tupla (x, y, r) com a posição e raio da bola
            
        Returns:
            frame: Frame com a marcação da bola
        """
        if ball_position is not None:
            x, y, r = ball_position
            # Desenhar círculo ao redor da bola
            cv2.circle(frame, (x, y), r, (0, 255, 255), 2)
            # Marcar o centro da bola
            cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
        
        return frame

class FieldDetector:
    """
    Classe para detecção e segmentação do campo de futebol
    """
    
    def __init__(self):
        # Faixa de cor verde para o campo (em HSV)
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([90, 255, 255])
        
        # Kernel para operações morfológicas
        self.kernel = np.ones((5, 5), np.uint8)
    
    def detect_field(self, frame):
        """
        Detecta o campo de futebol usando segmentação por cor
        
        Args:
            frame: Frame do vídeo (imagem BGR)
            
        Returns:
            mask: Máscara binária do campo
        """
        # Converter para HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Criar máscara para a cor verde
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        
        # Aplicar operações morfológicas para melhorar a máscara
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        
        return mask
    
    def get_field_contour(self, field_mask):
        """
        Obtém o contorno do campo a partir da máscara
        
        Args:
            field_mask: Máscara binária do campo
            
        Returns:
            contour: Maior contorno encontrado (campo)
        """
        # Encontrar contornos
        contours, _ = cv2.findContours(field_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Se não houver contornos, retornar None
        if not contours:
            return None
        
        # Retornar o maior contorno (assumindo que é o campo)
        return max(contours, key=cv2.contourArea)
    
    def draw_field(self, frame, field_contour):
        """
        Desenha o contorno do campo no frame
        
        Args:
            frame: Frame do vídeo
            field_contour: Contorno do campo
            
        Returns:
            frame: Frame com o contorno do campo
        """
        if field_contour is not None:
            cv2.drawContours(frame, [field_contour], 0, (0, 255, 0), 2)
        
        return frame
