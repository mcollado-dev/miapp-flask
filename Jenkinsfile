pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_PORT = "5000"
        SONAR_HOST_URL = "http://192.168.56.104:9000"
        SONAR_AUTH_TOKEN = credentials('sonar-token') // token seguro de Jenkins
        DEPLOY_HOST = "192.168.56.106"
        SSH_USER = "manuelcollado"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt
                    pip install pytest pytest-cov coverage
                    pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml:coverage.xml --cov-report=term
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube-Local') {
                    sh '''
                        . venv/bin/activate
                        sonar-scanner \
                            -Dsonar.projectKey=miapp-flask \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3 \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=${SONAR_AUTH_TOKEN} \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.exclusions=venv/**,tests/**
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t miapp-flask .'
            }
        }

        stage('Deploy Flask App en remoto') {
            steps {
                sh '''
                    docker save miapp-flask | bzip2 | ssh ${SSH_USER}@${DEPLOY_HOST} 'bunzip2 | docker load'
                    ssh ${SSH_USER}@${DEPLOY_HOST} "
                        docker stop miapp-flask-container || true
                        docker rm miapp-flask-container || true
                        docker run -d -p ${APP_PORT}:80 --name miapp-flask-container miapp-flask
                    "
                '''
            }
        }

        stage('Verificar Despliegue') {
            steps {
                sh "ssh ${SSH_USER}@${DEPLOY_HOST} 'curl -f http://localhost:${APP_PORT}'"
            }
        }
    }

    post {
        success { echo 'Pipeline completado correctamente.' }
        failure { echo 'Falló el pipeline. Revisa los logs.' }
    }
}
