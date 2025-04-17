#!/bin/bash

# Script de implantação para Football Vision Analytics
# Este script configura o ambiente e implanta a aplicação

echo "Iniciando implantação do Football Vision Analytics..."

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script deve ser executado como root (use sudo)"
  exit 1
fi

# Diretório base da aplicação
APP_DIR="/home/ubuntu/football-vision-analytics"
VENV_DIR="$APP_DIR/venv"
DEPLOY_DIR="$APP_DIR/deployment"

echo "Atualizando pacotes do sistema..."
apt-get update
apt-get upgrade -y

echo "Instalando dependências do sistema..."
apt-get install -y python3-pip python3-venv nginx

# Configurar Nginx
echo "Configurando Nginx..."
cp $DEPLOY_DIR/nginx.conf /etc/nginx/sites-available/football-vision
ln -sf /etc/nginx/sites-available/football-vision /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Configurar serviço systemd
echo "Configurando serviço systemd..."
cp $DEPLOY_DIR/football-vision.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable football-vision
systemctl start football-vision

echo "Verificando status do serviço..."
systemctl status football-vision

echo "Implantação concluída!"
echo "A aplicação está disponível em: http://localhost"
echo "Para acessar de outros dispositivos, use o IP do servidor"

# Instruções finais
echo ""
echo "Instruções de uso:"
echo "1. Acesse a aplicação através do navegador"
echo "2. Faça upload de um vídeo de futebol (MP4 ou MOV)"
echo "3. Aguarde o processamento"
echo "4. Visualize os resultados da análise"
echo ""
echo "Para mais informações, consulte a documentação em $APP_DIR/docs"
