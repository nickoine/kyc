from .base import *
import subprocess
import environ
import os

# Initialize environment variables
env = environ.Env()

# Load .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='dev_db'),
        'USER': config('DB_USER', default='dev'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432),
    }
}

def ensure_postgres_container():
    try:
        container_name = "postgres"

        # Check if the container exists (running or stopped)
        result = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", f"name={container_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"Error checking container status: {result.stderr}")
            return

        container_id = result.stdout.strip()

        if container_id:
            # Container exists, check if it's running
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print(f"Error inspecting container: {result.stderr}")
                return

            is_running = result.stdout.strip().lower() == "true"

            if not is_running:
                # Container exists but is stopped, start it
                print(f"Starting existing PostgreSQL container '{container_name}'...")
                subprocess.run(
                    ["docker", "start", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                print(f"PostgreSQL container '{container_name}' is running.")
        else:
            # Container does not exist, create and start it
            print(f"Creating and starting PostgreSQL container '{container_name}'...")
            subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", container_name,
                    "-e", f"POSTGRES_USER={config('DB_USER')}",
                    "-e", f"POSTGRES_PASSWORD={config('DB_PASSWORD')}",
                    "-e", f"POSTGRES_DB={config('DB_NAME')}",
                    "-p", f"{config('DB_PORT')}:5432",
                    "postgres:15"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
    except Exception as e:
        print(f"Error while managing PostgreSQL container: {e}")

# Run the container check when starting the dev environment
ensure_postgres_container()
