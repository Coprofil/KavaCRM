#!/bin/bash

# Скрипт для запуску KavaCRM в продакшн режимі
# Використовуйте цей скрипт замість manage.py runserver

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функції для кольорового виводу
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Перевірка наявності virtual environment
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment активний: $VIRTUAL_ENV"
    else
        print_warning "Virtual environment не активний"
        print_info "Активація venv..."
        source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || {
            print_error "Не вдалося активувати virtual environment"
            exit 1
        }
    fi
}

# Перевірка наявності залежностей
check_dependencies() {
    print_info "Перевірка залежностей..."

    python -c "import django" 2>/dev/null || {
        print_error "Django не встановлений"
        exit 1
    }

    python -c "import kavacrm" 2>/dev/null || {
        print_error "KavaCRM модуль недоступний"
        exit 1
    }

    print_success "Залежності перевірені"
}

# Перевірка налаштувань
check_settings() {
    print_info "Перевірка налаштувань Django..."

    # Перевірка SECRET_KEY
    if grep -q "django-insecure" kavapro/settings.py; then
        print_warning "SECRET_KEY містить 'django-insecure' - змініть для безпеки"
    fi

    # Перевірка DEBUG
    if grep -q "DEBUG = True" kavapro/settings.py; then
        print_warning "DEBUG = True - вимкніть для продакшн"
    fi

    print_success "Налаштування перевірені"
}

# Перевірка бази даних
check_database() {
    print_info "Перевірка з'єднання з базою даних..."

    python manage.py dbshell --command="SELECT 1;" 2>/dev/null || {
        print_error "Не вдалося підключитися до бази даних"
        print_info "Переконайтеся, що PostgreSQL запущений та налаштований"
        exit 1
    }

    print_success "З'єднання з БД успішне"
}

# Перевірка статичних файлів
check_static_files() {
    print_info "Перевірка статичних файлів..."

    if [ ! -d "staticfiles" ]; then
        print_info "Збір статичних файлів..."
        python manage.py collectstatic --noinput --clear
    fi

    if [ -d "staticfiles" ]; then
        files_count=$(find staticfiles -type f | wc -l)
        print_success "Знайдено $files_count статичних файлів"
    else
        print_error "Не вдалося створити статичні файли"
        exit 1
    fi
}

# Перевірка міграцій
check_migrations() {
    print_info "Перевірка міграцій..."

    python manage.py showmigrations | grep -q "\[ \]" && {
        print_warning "Є неприйняті міграції"
        print_info "Застосування міграцій..."
        python manage.py migrate
    }

    print_success "Міграції перевірені"
}

# Створення резервної копії перед запуском
create_backup() {
    print_info "Створення резервної копії..."

    backup_dir="backups/pre_start_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Копіювання БД
    if command -v pg_dump >/dev/null 2>&1; then
        pg_dump -h localhost -U kavacrm_user -d kavacrm > "$backup_dir/database.sql" 2>/dev/null && {
            print_success "Резервна копія БД створена"
        } || {
            print_warning "Не вдалося створити резервну копію БД"
        }
    fi

    # Архівування медіа файлів
    if [ -d "media" ]; then
        tar -czf "$backup_dir/media.tar.gz" media/ 2>/dev/null && {
            print_success "Резервна копія медіа файлів створена"
        }
    fi
}

# Запуск сервера
start_server() {
    print_info "Запуск KavaCRM сервера..."

    # Визначення порту
    PORT=${PORT:-8000}
    HOST=${HOST:-0.0.0.0}

    print_info "Сервер буде доступний на: http://$HOST:$PORT"

    # Запуск з різними опціями залежно від наявності gunicorn
    if command -v gunicorn >/dev/null 2>&1; then
        print_info "Використання Gunicorn для продакшн..."
        exec gunicorn kavapro.wsgi:application \
            --bind "$HOST:$PORT" \
            --workers 3 \
            --timeout 120 \
            --access-logfile logs/gunicorn_access.log \
            --error-logfile logs/gunicorn_error.log \
            --log-level info
    else
        print_warning "Gunicorn не знайдений, використовую Django development server"
        print_warning "Для продакшн рекомендується встановити Gunicorn"
        exec python manage.py runserver "$HOST:$PORT"
    fi
}

# Перевірка наявності директорій
create_directories() {
    print_info "Створення необхідних директорій..."

    mkdir -p logs
    mkdir -p backups
    mkdir -p media
    mkdir -p staticfiles

    print_success "Директорії створені"
}

# Перевірка системних сервісів
check_services() {
    print_info "Перевірка системних сервісів..."

    services=("postgresql" "redis-server" "nginx")

    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            print_success "$service - запущений"
        else
            print_warning "$service - не запущений або недоступний"
        fi
    done
}

# Функція для коректного завершення
cleanup() {
    print_info "Завершення роботи..."
    # Тут можна додати код для коректного завершення
    exit 0
}

# Обробка сигналів
trap cleanup SIGINT SIGTERM

# Основна функція
main() {
    print_info "ЗАПУСК KAVACRM В ПРОДАКШН РЕЖИМІ"
    echo "======================================"

    # Перевірка аргументів
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            --help)
                echo "Використання: $0 [опції]"
                echo ""
                echo "Опції:"
                echo "  --no-backup    Пропустити створення резервної копії"
                echo "  --debug        Режим відлагодження"
                echo "  --help         Показати цю допомогу"
                exit 0
                ;;
            *)
                print_error "Невідомий аргумент: $1"
                echo "Використайте --help для допомоги"
                exit 1
                ;;
        esac
    done

    # Послідовність перевірок
    check_venv
    create_directories
    check_dependencies
    check_settings
    check_services
    check_database
    check_migrations
    check_static_files

    # Створення бекапу (якщо не пропущено)
    if [ "$SKIP_BACKUP" != "true" ]; then
        create_backup
    fi

    # Повідомлення про успішну ініціалізацію
    echo ""
    print_success "ВСІ ПЕРЕВІРКИ ПРОЙДЕНІ!"
    print_success "СИСТЕМА ГОТОВА ДО РОБОТИ"
    echo ""

    # Інформація про систему
    print_info "Інформація про систему:"
    echo "• Python: $(python --version)"
    echo "• Django: $(python -c "import django; print(django.VERSION)")"
    echo "• База даних: $(python manage.py dbshell --command="SELECT version();" 2>/dev/null | head -1 || echo "Недоступна")"

    if [ "$DEBUG_MODE" = "true" ]; then
        print_warning "ЗАПУСК В РЕЖИМІ ВІДЛАГОДЖЕННЯ"
        export DJANGO_DEBUG=True
    fi

    echo ""
    print_info "ЗАПУСК СЕРВЕРА..."
    echo "======================================"

    # Запуск сервера
    start_server
}

# Запуск основної функції
main "$@"
