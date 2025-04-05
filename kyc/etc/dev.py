from .base import *
import os

DEBUG = True
ENV = os.getenv("ENV", "dev").lower()
USE_DOCKER_DB = os.getenv("USE_DOCKER_DB", "false").lower() == "true"

# Choose correct DB credentials based on ENV
if ENV == "test":
    db_config = {
        "NAME": os.getenv("TEST_DB_NAME", "kyc_test_db"),
        "USER": os.getenv("TEST_DB_USER", "kyc_test"),
        "PASSWORD": os.getenv("TEST_DB_PASSWORD", "password"),
        "PORT": os.getenv("TEST_DB_PORT", "5432"),
    }
else:  # default to dev
    db_config = {
        "NAME": os.getenv("DB_NAME", "kyc_db"),
        "USER": os.getenv("DB_USER", "kyc_dev"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }

# Host logic
db_config["HOST"] = os.getenv("DB_HOST", "db" if USE_DOCKER_DB else "localhost")

# Final DATABASES dict
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        **db_config,
    }
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'kyc.src.accounts',
    'kyc.src.questionnaires',
    'kyc.src.responses',
]

# Optional debug print
print(f"[settings] ENV: {ENV} | DB: {db_config['NAME']} | Host: {db_config['HOST']} | Port: {db_config['PORT']}")


# Print out the loaded values
print("Loaded dev.py Database Configuration:")
for key, value in DATABASES['default'].items():
    print(f"{key}: {value}")


CACHEOPS = {
    "accounts.account": {"ops": "all", "timeout": 60 * 15},
    "questionnaires.questionnaire": {"ops": ("fetch",), "timeout": 60 * 30}
}



# def ensure_postgres_container():
#     try:
#         container_name = "postgres"
#
#         # Check if the container exists (running or stopped)
#         result = subprocess.run(
#             ["docker", "ps", "-a", "-q", "-f", f"name={container_name}"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#
#         if result.returncode != 0:
#             print(f"Error checking container status: {result.stderr}")
#             return
#
#         container_id = result.stdout.strip()
#
#         if container_id:
#             # Container exists, check if it's running
#             result = subprocess.run(
#                 ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )
#
#             if result.returncode != 0:
#                 print(f"Error inspecting container: {result.stderr}")
#                 return
#
#             is_running = result.stdout.strip().lower() == "true"
#
#             if not is_running:
#                 # Container exists but is stopped, start it
#                 print(f"Starting existing PostgreSQL container '{container_name}'...")
#                 subprocess.run(
#                     ["docker", "start", container_name],
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE,
#                     text=True
#                 )
#             else:
#                 print(f"PostgreSQL container '{container_name}' is running.")
#         else:
#             # Container does not exist, create and start it
#             print(f"Creating and starting PostgreSQL container '{container_name}'...")
#             subprocess.run(
#                 [
#                     "docker", "run", "-d",
#                     "--name", container_name,
#                     "-e", f"POSTGRES_USER={config('DB_USER')}",
#                     "-e", f"POSTGRES_PASSWORD={config('DB_PASSWORD')}",
#                     "-e", f"POSTGRES_DB={config('DB_NAME')}",
#                     "-p", f"{config('DB_PORT')}:5432",
#                     "postgres:15"
#                 ],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )
#     except Exception as e:
#         print(f"Error while managing PostgreSQL container: {e}")
#
# # Run the container check when starting the dev environment
# ensure_postgres_container()
