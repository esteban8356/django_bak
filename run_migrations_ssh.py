"""
Script para ejecutar migraciones Django directamente en el servidor Dokploy.
Sube el proyecto via SFTP y ejecuta las migraciones dentro de Docker.
"""
import paramiko
import os
import sys

SSH_HOST = '187.77.195.31'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASSWORD = 'Est316728356m.'

# Credenciales de la base de datos (desde Dokploy)
DB_HOST = 'tendencias-tendencias-jzj6qa'
DB_PORT = '5432'
DB_NAME = 'admin'
DB_USER = 'admin'
DB_PASSWORD = 'QBOaGvnuBZgC9gK50Hqi'
DOCKER_NETWORK = 'dokploy-network'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = '/tmp/django_migrate'


def ssh_exec(ssh, cmd, show=True):
    """Ejecuta comando SSH y retorna output."""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if show and out:
        print(out)
    if show and err:
        print(f"  stderr: {err}")
    return out, err


def upload_project(ssh, sftp):
    """Sube los archivos necesarios del proyecto Django al servidor."""
    print("[2/5] Subiendo proyecto al servidor...")
    
    # Crear directorio remoto
    ssh_exec(ssh, f'rm -rf {REMOTE_DIR} && mkdir -p {REMOTE_DIR}', show=False)
    
    # Archivos y carpetas a subir
    def upload_recursive(local_path, remote_path):
        for item in os.listdir(local_path):
            local_item = os.path.join(local_path, item)
            remote_item = f"{remote_path}/{item}"
            
            # Saltar archivos innecesarios
            if item in ('__pycache__', '.git', 'db.sqlite3', 'run_migrations_ssh.py', 
                        '.env', 'node_modules', '.venv', 'venv'):
                continue
            
            if os.path.isfile(local_item):
                try:
                    sftp.put(local_item, remote_item)
                except Exception as e:
                    print(f"  Skip: {item} ({e})")
            elif os.path.isdir(local_item):
                try:
                    sftp.mkdir(remote_item)
                except:
                    pass
                upload_recursive(local_item, remote_item)
    
    upload_recursive(PROJECT_DIR, REMOTE_DIR)
    print("  [OK] Proyecto subido")


def main():
    print("=" * 60)
    print("  MIGRACIONES DJANGO EN SERVIDOR DOKPLOY")
    print("=" * 60)
    
    # 1. Conectar SSH
    print("\n[1/5] Conectando SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD)
    sftp = ssh.open_sftp()
    print("  [OK] Conectado")
    
    # 2. Subir proyecto
    upload_project(ssh, sftp)
    
    # 3. Verificar conectividad con PostgreSQL
    print(f"\n[3/5] Verificando conexion a PostgreSQL ({DB_HOST})...")
    
    # Verificar que la red dokploy-network existe
    out, _ = ssh_exec(ssh, f'docker network ls --filter name={DOCKER_NETWORK} --format "{{{{.Name}}}}"', show=False)
    if DOCKER_NETWORK in out:
        print(f"  [OK] Red '{DOCKER_NETWORK}' encontrada")
    else:
        print(f"  [ERROR] Red '{DOCKER_NETWORK}' no encontrada!")
        print(f"  Redes disponibles:")
        ssh_exec(ssh, 'docker network ls --format "  - {{.Name}}"')
        ssh.close()
        return
    
    # Verificar conectividad a PostgreSQL usando un contenedor temporal
    test_cmd = (
        f'docker run --rm --network {DOCKER_NETWORK} '
        f'postgres:16 psql "postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" '
        f'-c "SELECT 1 as test" 2>&1'
    )
    out, err = ssh_exec(ssh, test_cmd, show=False)
    if 'test' in out or '1' in out:
        print(f"  [OK] PostgreSQL responde correctamente")
    else:
        print(f"  [WARN] Test de conexion: {out[:200]}")
        print(f"  Continuando de todas formas...")
    
    # 4. Crear .env y ejecutar migraciones dentro de Docker
    print(f"\n[4/5] Ejecutando migraciones dentro de Docker...")
    
    # Crear .env en el servidor
    env_content = f"""DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASSWORD={DB_PASSWORD}
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}
"""
    ssh_exec(ssh, f'cat > {REMOTE_DIR}/.env << ENVEOF\n{env_content}\nENVEOF', show=False)
    
    # Crear Dockerfile temporal
    dockerfile = """FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir django djangorestframework django-cors-headers djangorestframework-simplejwt python-dotenv psycopg2-binary
COPY . /app/
"""
    ssh_exec(ssh, f'cat > {REMOTE_DIR}/Dockerfile.migrate << DEOF\n{dockerfile}\nDEOF', show=False)
    
    # Construir imagen temporal
    print("  Construyendo imagen temporal (esto puede tardar ~30s)...")
    out, err = ssh_exec(ssh, f'cd {REMOTE_DIR} && docker build -f Dockerfile.migrate -t django-migrate-temp . 2>&1 | tail -5')
    
    # Comando base de docker run
    docker_run = (
        f'docker run --rm '
        f'--network {DOCKER_NETWORK} '
        f'-e DB_HOST={DB_HOST} '
        f'-e DB_PORT={DB_PORT} '
        f'-e DB_NAME={DB_NAME} '
        f'-e DB_USER={DB_USER} '
        f'-e DB_PASSWORD={DB_PASSWORD} '
        f'-e DJANGO_SUPERUSER_PASSWORD=admin '
        f'-v {REMOTE_DIR}:/app '
        f'-w /app '
        f'django-migrate-temp'
    )
    
    # Ejecutar makemigrations
    print("\n  Ejecutando makemigrations...")
    out, err = ssh_exec(ssh, f'{docker_run} python manage.py makemigrations 2>&1')
    
    # Ejecutar migrate
    print("\n  Ejecutando migrate...")
    out, err = ssh_exec(ssh, f'{docker_run} python manage.py migrate 2>&1')
    
    migrate_ok = 'OperationalError' not in (out + err) and 'Error' not in err
    
    if not migrate_ok:
        print("  [ERROR] Fallo migrate!")
        # Cleanup
        ssh_exec(ssh, f'docker rmi django-migrate-temp 2>/dev/null; rm -rf {REMOTE_DIR}', show=False)
        ssh.close()
        return
    
    # 5. Crear superusuario
    print("\n[5/5] Creando superusuario admin/admin...")
    out, err = ssh_exec(ssh, 
        f'{docker_run} python manage.py createsuperuser --noinput --username admin --email admin@admin.com 2>&1')
    
    # Cleanup
    print("\nLimpiando archivos temporales...")
    ssh_exec(ssh, f'docker rmi django-migrate-temp 2>/dev/null; rm -rf {REMOTE_DIR}', show=False)
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 60)
    print("  COMPLETADO!")
    print("  - Migraciones aplicadas en PostgreSQL")
    print("  - Superusuario: admin / admin")
    print("=" * 60)


if __name__ == '__main__':
    main()
