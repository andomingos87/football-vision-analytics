# Documentação Técnica - Football Vision Analytics

## Visão Geral da Arquitetura

O Football Vision Analytics é uma aplicação web para análise de métricas de futebol usando visão computacional. A arquitetura do sistema é composta pelos seguintes componentes principais:

### 1. Frontend
- Interface web desenvolvida com HTML, CSS (Bootstrap) e JavaScript
- Páginas para upload de vídeo, visualização de processamento e exibição de resultados
- Visualizações interativas usando Chart.js

### 2. Backend
- Servidor web Flask para gerenciamento de requisições HTTP
- Sistema de upload e processamento de vídeos
- API para comunicação entre frontend e módulos de processamento

### 3. Módulos de Processamento de Vídeo
- Detecção de jogadores usando OpenCV
- Detecção de bola e campo
- Rastreamento de objetos e cálculo de métricas
- Geração de vídeo com marcações

### 4. Sistema de Armazenamento
- Armazenamento de vídeos originais
- Armazenamento de resultados processados
- Armazenamento de frames-chave

## Estrutura de Diretórios

```
football-vision-analytics/
├── app/                      # Código principal da aplicação
│   ├── static/               # Arquivos estáticos
│   │   ├── uploads/          # Vídeos enviados pelos usuários
│   │   └── results/          # Resultados processados
│   ├── templates/            # Templates HTML
│   ├── __init__.py           # Inicialização da aplicação Flask
│   ├── routes.py             # Rotas da aplicação
│   ├── detection.py          # Módulos de detecção (jogadores, bola, campo)
│   ├── analyzer.py           # Análise de métricas
│   ├── processor.py          # Processamento de vídeo
│   └── test_processor.py     # Testes do processador
├── data/                     # Dados para testes
├── deployment/               # Arquivos de implantação
│   ├── nginx.conf            # Configuração do Nginx
│   ├── football-vision.service # Configuração do serviço systemd
│   └── deploy.sh             # Script de implantação
├── docs/                     # Documentação
│   ├── manual_usuario.md     # Manual do usuário
│   └── documentacao_tecnica.md # Documentação técnica
├── venv/                     # Ambiente virtual Python
├── requirements.txt          # Dependências Python
├── run.py                    # Script para iniciar a aplicação
└── README.md                 # Informações gerais do projeto
```

## Tecnologias Utilizadas

### Linguagens de Programação
- Python 3.10+: Linguagem principal para backend e processamento de vídeo
- JavaScript: Para interatividade no frontend
- HTML/CSS: Para estrutura e estilo da interface

### Frameworks e Bibliotecas
- Flask: Framework web para Python
- OpenCV: Biblioteca de visão computacional
- NumPy: Processamento numérico
- Chart.js: Visualização de dados
- Bootstrap: Framework CSS para interface responsiva

### Ferramentas de Implantação
- Nginx: Servidor web
- Systemd: Gerenciamento de serviços
- Bash: Scripts de implantação

## Fluxo de Processamento de Vídeo

1. **Upload do Vídeo**
   - O usuário faz upload de um vídeo MP4 ou MOV
   - O vídeo é salvo no diretório `app/static/uploads/`
   - Um ID único é gerado para o processamento

2. **Detecção de Jogadores**
   - A classe `PlayerDetector` processa cada frame do vídeo
   - Utiliza subtração de fundo e análise de contornos para detectar jogadores
   - Filtra contornos por área e proporção para identificar pessoas

3. **Detecção de Bola**
   - A classe `BallDetector` utiliza a transformada de Hough para detectar círculos
   - Filtra os círculos por tamanho para identificar a bola

4. **Detecção de Campo**
   - A classe `FieldDetector` segmenta o campo usando filtros de cor HSV
   - Identifica a área verde do campo para delimitar a área de jogo

5. **Rastreamento e Análise**
   - A classe `FootballAnalyzer` integra as detecções
   - Rastreia jogadores e bola ao longo dos frames
   - Calcula métricas como posse de bola, passes, chutes e gols

6. **Geração de Resultados**
   - Cria um vídeo com marcações visuais
   - Salva frames-chave como imagens
   - Compila estatísticas e métricas
   - Prepara dados para visualização

7. **Apresentação dos Resultados**
   - Exibe o vídeo processado com marcações
   - Mostra gráficos e tabelas com as métricas
   - Apresenta frames-chave de momentos importantes

## Algoritmos Principais

### Detecção de Jogadores
```python
# Pseudocódigo simplificado
def detect_players(frame):
    # Aplicar subtração de fundo
    fg_mask = background_subtractor.apply(frame)
    
    # Aplicar operações morfológicas
    fg_mask = apply_morphology(fg_mask)
    
    # Encontrar contornos
    contours = find_contours(fg_mask)
    
    # Filtrar contornos por área e proporção
    player_boxes = []
    for contour in contours:
        if min_area < area(contour) < max_area:
            x, y, w, h = bounding_rect(contour)
            if 1.5 < h/w < 4.0:  # Proporção humana
                player_boxes.append((x, y, w, h))
    
    return player_boxes
```

### Rastreamento de Jogadores
```python
# Pseudocódigo simplificado
def track_players(current_players, player_history):
    for player_center in current_players:
        # Encontrar jogador mais próximo no histórico
        player_id = find_closest_player(player_center, player_history)
        
        # Atualizar histórico
        player_history[player_id].append(player_center)
    
    return player_history
```

### Determinação de Posse de Bola
```python
# Pseudocódigo simplificado
def determine_possession(ball_position, player_positions):
    if ball_position is None:
        return "none"
    
    # Encontrar jogador mais próximo da bola
    closest_player = find_closest_player(ball_position, player_positions)
    
    # Determinar time do jogador
    if distance(ball_position, closest_player) < threshold:
        return get_team(closest_player)
    else:
        return "none"
```

## Limitações Atuais e Melhorias Futuras

### Limitações
- Detecção baseada em cores pode ser afetada por condições de iluminação
- Rastreamento pode perder jogadores durante oclusões
- Detecção de eventos (passes, chutes) é simplificada no MVP
- Processamento limitado a 300 frames para otimização

### Melhorias Futuras
- Implementar modelos de deep learning (YOLO, SSD) para detecção mais precisa
- Adicionar reconhecimento de números de camisas para identificação de jogadores
- Melhorar algoritmos de rastreamento com filtros de Kalman
- Implementar processamento distribuído para vídeos longos
- Adicionar detecção automática de times por cores de uniforme
- Implementar análise tática e de formações

## Implantação

### Requisitos de Sistema
- Ubuntu 20.04 LTS ou superior
- Python 3.10+
- Nginx
- 4GB RAM mínimo
- 10GB espaço em disco

### Passos para Implantação
1. Clone o repositório
2. Execute o script `deployment/deploy.sh` como root
3. Configure o domínio no arquivo Nginx se necessário
4. Reinicie os serviços

### Monitoramento e Manutenção
- Logs da aplicação: `/var/log/football-vision/`
- Logs do Nginx: `/var/log/nginx/`
- Reiniciar serviço: `systemctl restart football-vision`

## Referências

- OpenCV Documentation: https://docs.opencv.org/
- Flask Documentation: https://flask.palletsprojects.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- Chart.js Documentation: https://www.chartjs.org/docs/

---

© 2025 Football Vision Analytics. Todos os direitos reservados.
