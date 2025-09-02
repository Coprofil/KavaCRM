#!/bin/bash

# Скрипт для налаштування PostgreSQL з pgvector для RAG системи

set -e

DB_NAME="kavacrm"
DB_USER="kavacrm_user"
DB_PASSWORD="your-secure-password"
POSTGRES_VERSION="15"

echo "🐘 Налаштування PostgreSQL з pgvector для KavaCRM"

# Встановлення PostgreSQL
echo "📦 Встановлення PostgreSQL..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Встановлення pgvector
echo "🔧 Встановлення pgvector..."
sudo apt install -y build-essential git postgresql-server-dev-${POSTGRES_VERSION}

# Клонування та компіляція pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Налаштування PostgreSQL
echo "⚙️ Налаштування PostgreSQL..."

# Створення користувача та бази даних
sudo -u postgres psql <<EOF
-- Створення користувача
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Створення бази даних
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Надання прав
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Підключення до бази та створення розширення
\c $DB_NAME
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Надання прав на розширення
GRANT USAGE ON SCHEMA public TO $DB_USER;
GRANT CREATE ON SCHEMA public TO $DB_USER;
EOF

# Налаштування pg_hba.conf для безпеки
echo "🔒 Налаштування безпеки PostgreSQL..."
sudo tee -a /etc/postgresql/${POSTGRES_VERSION}/main/pg_hba.conf > /dev/null <<EOF

# KavaCRM connections
local   $DB_NAME         $DB_USER                                md5
host    $DB_NAME         $DB_USER        127.0.0.1/32            md5
host    $DB_NAME         $DB_USER        ::1/128                 md5
EOF

# Налаштування postgresql.conf для оптимізації
echo "⚡ Оптимізація PostgreSQL..."
sudo sed -i "s/#shared_preload_libraries = ''/shared_preload_libraries = 'vector'/" /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf

# Налаштування пам'яті (для сервера з 4GB RAM)
sudo sed -i "s/#shared_buffers = 128MB/shared_buffers = 1GB/" /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
sudo sed -i "s/#effective_cache_size = 4GB/effective_cache_size = 3GB/" /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
sudo sed -i "s/#work_mem = 4MB/work_mem = 16MB/" /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf

# Перезапуск PostgreSQL
echo "🔄 Перезапуск PostgreSQL..."
sudo systemctl restart postgresql
sudo systemctl enable postgresql

# Перевірка встановлення
echo "✅ Перевірка встановлення..."
sudo -u postgres psql -d $DB_NAME -c "SELECT version();"
sudo -u postgres psql -d $DB_NAME -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Створення тестової таблиці для перевірки pgvector
echo "🧪 Тестування pgvector..."
sudo -u postgres psql -d $DB_NAME <<EOF
-- Створення тестової таблиці
CREATE TABLE test_vectors (
    id SERIAL PRIMARY KEY,
    name TEXT,
    embedding VECTOR(1536)
);

-- Вставка тестових даних
INSERT INTO test_vectors (name, embedding) VALUES 
('test1', '[1,2,3]'::vector),
('test2', '[4,5,6]'::vector);

-- Тест пошуку схожості
SELECT name, embedding <-> '[1,2,3]'::vector AS distance 
FROM test_vectors 
ORDER BY embedding <-> '[1,2,3]'::vector;

-- Видалення тестової таблиці
DROP TABLE test_vectors;
EOF

# Створення скрипта для створення індексів
echo "📝 Створення скрипта для індексів..."
sudo tee /usr/local/bin/create-rag-indexes.sql > /dev/null <<EOF
-- Індекси для RAG системи
-- Використовувати після створення таблиць Django

-- Індекс для швидкого пошуку по типу контенту
CREATE INDEX IF NOT EXISTS idx_document_embeddings_content_type 
ON document_embeddings (content_type);

-- Індекс для пошуку по object_id
CREATE INDEX IF NOT EXISTS idx_document_embeddings_object_id 
ON document_embeddings (object_id);

-- Індекс для векторного пошуку (створюється автоматично pgvector)
-- CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector 
-- ON document_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Композитний індекс для пошуку по типу та об'єкту
CREATE INDEX IF NOT EXISTS idx_document_embeddings_type_object 
ON document_embeddings (content_type, object_id);

-- Індекс для пошуку по даті створення
CREATE INDEX IF NOT EXISTS idx_document_embeddings_created 
ON document_embeddings (created_at);
EOF

# Створення скрипта для моніторингу
echo "📊 Створення скрипта моніторингу..."
sudo tee /usr/local/bin/monitor-postgresql.sh > /dev/null <<EOF
#!/bin/bash

# Моніторинг PostgreSQL для KavaCRM

echo "🐘 PostgreSQL Status for KavaCRM"
echo "================================"

# Статус сервісу
echo "1. Service Status:"
sudo systemctl status postgresql --no-pager -l

echo -e "\n2. Database Size:"
sudo -u postgres psql -d $DB_NAME -c "
SELECT 
    pg_size_pretty(pg_database_size('$DB_NAME')) as database_size,
    (SELECT count(*) FROM document_embeddings) as rag_documents,
    (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables;
"

echo -e "\n3. Active Connections:"
sudo -u postgres psql -d $DB_NAME -c "
SELECT 
    count(*) as active_connections,
    state,
    application_name
FROM pg_stat_activity 
WHERE datname = '$DB_NAME'
GROUP BY state, application_name;
"

echo -e "\n4. Vector Extension Status:"
sudo -u postgres psql -d $DB_NAME -c "
SELECT 
    extname,
    extversion,
    extrelocatable
FROM pg_extension 
WHERE extname = 'vector';
"

echo -e "\n5. Recent RAG Activity:"
sudo -u postgres psql -d $DB_NAME -c "
SELECT 
    content_type,
    count(*) as document_count,
    max(created_at) as last_created
FROM document_embeddings 
GROUP BY content_type
ORDER BY document_count DESC;
"
EOF

sudo chmod +x /usr/local/bin/monitor-postgresql.sh

# Створення backup скрипта
echo "💾 Створення backup скрипта..."
sudo tee /usr/local/bin/backup-postgresql.sh > /dev/null <<EOF
#!/bin/bash

# Backup PostgreSQL для KavaCRM

BACKUP_DIR="/var/backups/postgresql"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="kavacrm_db_\$DATE.sql"

echo "💾 Створення backup PostgreSQL..."

# Створення директорії
sudo mkdir -p \$BACKUP_DIR

# Створення backup
sudo -u postgres pg_dump -h localhost -U $DB_USER -d $DB_NAME > \$BACKUP_DIR/\$BACKUP_FILE

# Стиснення
gzip \$BACKUP_DIR/\$BACKUP_FILE

echo "✅ Backup створено: \$BACKUP_DIR/\$BACKUP_FILE.gz"

# Видалення старих backup (старші 7 днів)
find \$BACKUP_DIR -name "kavacrm_db_*.sql.gz" -mtime +7 -delete

echo "🗑️ Видалено старі backup файли"
EOF

sudo chmod +x /usr/local/bin/backup-postgresql.sh

# Додавання backup до cron
echo "⏰ Налаштування автоматичного backup..."
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup-postgresql.sh") | crontab -

echo "✅ PostgreSQL з pgvector налаштування завершено!"
echo "🐘 База даних: $DB_NAME"
echo "👤 Користувач: $DB_USER"
echo "🔧 Розширення: vector, uuid-ossp"
echo ""
echo "Команди для управління:"
echo "  Моніторинг: sudo /usr/local/bin/monitor-postgresql.sh"
echo "  Backup: sudo /usr/local/bin/backup-postgresql.sh"
echo "  Підключення: psql -h localhost -U $DB_USER -d $DB_NAME"
echo ""
echo "Наступні кроки:"
echo "1. Оновіть налаштування Django для використання PostgreSQL"
echo "2. Запустіть міграції: python manage.py migrate"
echo "3. Ініціалізуйте RAG систему: python manage.py init_rag_system"
