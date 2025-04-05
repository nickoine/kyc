# 🚀 Running the Application

The root directory for running commands is **`kyc_project`**.

---

## ⚙️ Configuration

All environment configuration files live in the `etc/` directory, including:

- `docker-compose.yml`
- `.env`

You can control the application behavior using two key environment variables:

- `ENV`: Defines the mode (`dev` or `test`)
- `USE_DOCKER_DB`: Toggles between using a Dockerized DB or local DB

---

## 🐳 Development Mode (Running in Docker)

1. Set environment:
   ```bash
   export ENV=dev
   export USE_DOCKER_DB=true
   ```
2. Build Docker images:
   ```bash
   docker-compose build
   ```
3. Start services:
   ```bash
   docker-compose up
   ```

---

## 🧪 Test Mode (Using Docker)

1. Run tests with `pytest` (independent of `ENV`):
   ```bash
   export PYTHONPATH=.
   pytest
   ```

2. Set test environment:
   ```bash
   export ENV=test
   export USE_DOCKER_DB=true
   ```

3. Build and run test containers:
   ```bash
   docker-compose -f docker-compose.test.yml up --build
   ```

4. Run Django tests:
   ```bash
   python manage.py test
   ```
   
5. Reset the Test DB Volume:
   ```bash
   docker-compose -f docker-compose.test.yml down -v
   ```
---

## 🔀 Hybrid Setup (App Local + DB in Docker)

This setup allows local development of the Django app using a DB inside Docker.

1. Start the database container:
   ```bash
   docker start <db_container_name>
   ```

2. Switch to hybrid mode:
   ```bash
   export ENV=dev
   export USE_DOCKER_DB=true
   ```

3. Run the app locally:
   ```bash
   python manage.py runserver
   ```

---

## 💻 Fully Local Setup (No Docker)

To run both Django and PostgreSQL locally:

1. Start PostgreSQL:
   ```bash
   sudo service postgresql start
   ```

2. Allow local connections (edit `pg_hba.conf` to use `trust` or `md5`), then restart:
   ```bash
   sudo service postgresql restart
   ```

3. Set `.env` or shell values:
   ```env
   ENV=dev
   DB_HOST=localhost
   USE_DOCKER_DB=false
   ```

4. Apply migrations and run:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 🔁 Switching Between Docker and Local DB

To toggle DB source easily:

- Docker DB:
  ```bash
  export USE_DOCKER_DB=true
  ```

- Local DB:
  ```bash
  export USE_DOCKER_DB=false
  ```

