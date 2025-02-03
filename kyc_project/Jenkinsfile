pipeline {
    agent {
        docker {
            image "${params.JENKINS_AGENT_IMAGE}" // Jenkins agent runs in this image
        }
    }

    parameters {
        string(name: 'JENKINS_AGENT_IMAGE', defaultValue: 'jenkins', description: 'Jenkins agent image tag')
    }

    environment {
        DATABASE_URL = credentials('DATABASE_URL_SECRET') // Jenkins credentials
        DOCKER_HUB_CREDS = credentials('DOCKER_HUB_CREDS')  // Docker Hub credentials
    }

    stages {
        stage('Load Environment Variables') {
            steps {
                script {
                    // Load environment variables from .env file
                    withEnv(readFile('.env').split('\n')) {
                        echo "Environment variables loaded successfully."
                    }
                }
            }
        }

        stage('Checkout Code') {
            steps {
                git "${env.GITHUB}" // Clone the repository
            }
        }

        stage('Pull and Build if needed') {
            when {
                changeset "Dockerfile,${env.DOCKER_COMPOSE_FILE}"  // Trigger only if these files change
            }
            steps {
                script {
                    // Validate docker-compose.yml
                    sh 'docker-compose config'

                    // Pull images in parallel
                    def images = ["${env.DOCKER_HUB_USERNAME_REPOSITORY_NAME}:${env.DOCKER_IMAGE_DB}"] // Place more images in list separated with coma
                    parallel images.collectEntries { image ->
                        ["Pull ${image}": {
                            retry(3) {
                                sh "docker pull ${image} || true"
                            }
                        }]
                    }

                    // Build with cache and pull updated base images, add --cache-from IMAGE for image
                    sh """
                        docker-compose build --pull --cache-from ${env.DOCKER_HUB_USERNAME_REPOSITORY_NAME}:${env.DOCKER_IMAGE_DB}
                    """

                    // Log build success
                    echo 'Docker images built successfully.'
                }
            }
        }

        stage('Start Services') {
            steps {
                sh 'docker-compose up -d'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker-compose -f ${env.DOCKER_COMPOSE_FILE} exec tests python manage.py test' // Run tests in the tests container
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    docker-compose -f ${env.DOCKER_COMPOSE_FILE} down -v  // Stop and remove containers, networks, and volumes
                    docker image prune -f --filter "until=24h"  // Remove unused images older than 24 hours
                    docker volume prune -f  // Remove unused volumes
                '''
            }
        }

        post {
            always {
                echo 'Pipeline completed. Performing cleanup...'
                // Additional cleanup steps if needed
            }
            success {
                echo 'Pipeline succeeded!'
            }
            failure {
                echo 'Pipeline failed!'
                // Add notifications (e.g., email, Slack) here
            }
        }
    }
}


// stage('Unit Tests') {
//     steps {
//         sh 'docker-compose -f docker-compose.unit.yml up --abort-on-container-exit'
//     }
// }
//
// stage('Integration Tests') {
//     steps {
//         sh 'docker-compose -f docker-compose.integration.yml up --abort-on-container-exit'
//     }
// }
// stage('Cleanup') {
//     steps {
//         sh 'docker-compose -f docker-compose.unit.yml down'
//         sh 'docker-compose -f docker-compose.integration.yml down'
//     }
// }


//     stage('Push Image') {
//         steps {
//             script {
//                 // Log in to Docker Hub
//                 sh """
//                     echo ${DOCKER_HUB_CREDS_PSW} | docker login -u ${DOCKER_HUB_CREDS_USR} --password-stdin
//                 """
//
//                 // Push the Docker image
//                 sh "docker push ${env.DOCKER_IMAGE}"
//             }
//         }
//     }