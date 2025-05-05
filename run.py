import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Criar diretórios necessários se não existirem
    os.makedirs('app/static/uploads', exist_ok=True)
    os.makedirs('app/static/results', exist_ok=True)
    
    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
