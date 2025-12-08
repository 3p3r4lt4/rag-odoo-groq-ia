#!/bin/bash
# Script de control para RAG Odoo Bot
# Uso: ./botctl.sh [start|stop|restart|status|logs|enable|disable]

SERVICE_NAME="rag-odoo-bot.service"
USER="raguser"
PROJECT_DIR="/home/raguser/rag-odoo"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[RAG-Odoo Bot]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

check_venv() {
    if [ ! -f "$PROJECT_DIR/venv/bin/activate" ]; then
        print_error "Entorno virtual no encontrado en $PROJECT_DIR/venv"
        exit 1
    fi
}

check_env() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_error "Archivo .env no encontrado en $PROJECT_DIR"
        exit 1
    fi
}

case "$1" in
    start)
        print_status "Iniciando RAG Odoo Bot..."
        sudo systemctl start $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    stop)
        print_status "Deteniendo RAG Odoo Bot..."
        sudo systemctl stop $SERVICE_NAME
        print_success "Bot detenido"
        ;;
    restart)
        print_status "Reiniciando RAG Odoo Bot..."
        sudo systemctl restart $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    status)
        print_status "Estado del RAG Odoo Bot:"
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    logs)
        print_status "Mostrando logs del bot (últimas 50 líneas):"
        sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
        ;;
    logs-follow)
        print_status "Siguiendo logs en tiempo real (Ctrl+C para salir):"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    logs-all)
        print_status "Mostrando todos los logs:"
        sudo journalctl -u $SERVICE_NAME --no-pager
        ;;
    enable)
        print_status "Habilitando inicio automático..."
        sudo systemctl enable $SERVICE_NAME
        print_success "Servicio habilitado para inicio automático"
        ;;
    disable)
        print_status "Deshabilitando inicio automático..."
        sudo systemctl disable $SERVICE_NAME
        print_success "Servicio deshabilitado"
        ;;
    manual)
        print_status "Ejecutando manualmente en primer plano..."
        check_venv
        check_env
        cd $PROJECT_DIR
        source venv/bin/activate
        python run.py
        ;;
    test)
        print_status "Probando configuración..."
        check_venv
        check_env
        print_success "Entorno virtual: OK"
        print_success "Archivo .env: OK"
        
        # Probar imports de Python
        cd $PROJECT_DIR
        source venv/bin/activate
        python -c "
import sys
sys.path.append('.')
try:
    from config.settings import settings
    print('✅ Configuración: OK')
    from services.odoo_client import OdooClient
    print('✅ Cliente Odoo: OK')
    from handlers.telegram_bot import TelegramBot
    print('✅ Bot Telegram: OK')
    print('\\n🎉 Todas las pruebas pasaron!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
        "
        ;;
    update)
        print_status "Actualizando código desde Git..."
        cd $PROJECT_DIR
        if [ -d ".git" ]; then
            git pull
            print_success "Código actualizado"
            
            # Reiniciar si el servicio está activo
            if systemctl is-active --quiet $SERVICE_NAME; then
                print_status "Reiniciando servicio..."
                sudo systemctl restart $SERVICE_NAME
            fi
        else
            print_warning "No es un repositorio Git"
        fi
        ;;
    backup)
        print_status "Creando backup del proyecto..."
        BACKUP_DIR="/home/raguser/backups"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/rag-odoo-backup-$TIMESTAMP.tar.gz"
        
        mkdir -p $BACKUP_DIR
        cd /home/raguser
        tar -czf $BACKUP_FILE rag-odoo --exclude=venv --exclude=__pycache__ --exclude=*.pyc
        
        print_success "Backup creado: $BACKUP_FILE"
        ls -lh $BACKUP_FILE
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|logs-follow|logs-all|enable|disable|manual|test|update|backup}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start       - Iniciar servicio"
        echo "  stop        - Detener servicio"
        echo "  restart     - Reiniciar servicio"
        echo "  status      - Ver estado del servicio"
        echo "  logs        - Ver últimos logs"
        echo "  logs-follow - Seguir logs en tiempo real"
        echo "  logs-all    - Ver todos los logs"
        echo "  enable      - Habilitar inicio automático"
        echo "  disable     - Deshabilitar inicio automático"
        echo "  manual      - Ejecutar manualmente en terminal"
        echo "  test        - Probar configuración"
        echo "  update      - Actualizar código desde Git"
        echo "  backup      - Crear backup del proyecto"
        exit 1
esac

exit 0
