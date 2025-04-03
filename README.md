# Running the Application

The root directory for running commands is **kyc_project**. The application can be run either locally or inside a Docker container.

## Configuration

Configuration files are located in the `etc` directory.

## Running Locally

### Development Mode
1. In the `.env` file, set `DB_HOST=localhost`.
2. Set the environment variable:  
   ```sh
   export ENV=dev
   ```
3. Run the application:
   ```sh
   python manage.py runserver
   ```

### Test Mode
1. In the `.env` file, set `DB_HOST=localhost`.
2. Set the environment variable:
   ```sh
   export ENV=test
   ```
3. Run tests using Django's test runner:
   ```sh
   python manage.py test
   ```
4. To run tests with `pytest`, set the `PYTHONPATH` environment variable:
   ```sh
   export PYTHONPATH=.
   pytest
   ```

## Running in Docker

### Development Mode
1. In the `.env` file, set `DB_HOST=db`.
2. Build the Docker images:
   ```sh
   docker-compose build
   ```
3. Start the containers:
   ```sh
   docker-compose up
   ```

### Test Mode
1. In the `.env` file, set `DB_HOST=db`.
2. Build the Docker images for testing:
   ```sh
   docker-compose -f docker-compose.test.yml build
   ```
3. Start the test containers:
   ```sh
   docker-compose -f docker-compose.test.yml up
   ```

