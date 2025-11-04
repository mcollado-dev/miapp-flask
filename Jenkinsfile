pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_PORT = "5000"
        SONAR_HOST_URL = "http://192.168.56.104:9000"
        DEPLOY_HOST = "192.168.56.106"
        SSH_USER = "manuelcollado"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                checkout scm
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Ejecutando tests con cobertura...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --no-cache-dir -r requirements.txt
                    pip install pytest pytest-cov coverage

                    # Ejecutar tests
                    pytest --maxfail=1 --disable-warnings --cov=. --cov-report=term

                    # Generar coverage compatible Sonar (version 1)
                    coverage xml -o coverage.xml
                    ls -l coverage.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis SonarQube...'
                withSonarQubeEnv('SonarQube-Local') {
                    script {
                        def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                        sh """
                            . venv/bin/activate
                            ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=miapp-flask \
                                -Dsonar.sources=. \
                                -Dsonar.python.version=3 \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.login=${SONAR_AUTH_TOKEN} \
                                -Dsonar.coverageReportPaths=coverage.xml \
                                -Dsonar.exclusions=venv/**,tests/**
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Construyendo imagen Docker local...'
                sh '''
                    docker build -t miapp-flask .
                '''
            }
        }

        stage('Deploy Flask App en remoto') {
            steps {
                echo "Desplegando contenedor Flask en ${DEPLOY_HOST}..."
                sh '''
                    docker save miapp-flask | bzip2 | ssh -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} 'bunzip2 | docker load'

                    ssh -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} "
                        docker stop miapp-flask-container || true
                        docker rm miapp-flask-container || true
                        docker run -d -p ${APP_PORT}:80 --name miapp-flask-container miapp-flask
                    "
                '''
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo "Verificando despliegue remoto en ${DEPLOY_HOST}..."
                sh '''
                    sleep 5
                    ssh -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} "curl -f http://localhost:${APP_PORT} || exit 1"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente: análisis SonarQube + despliegue remoto exitoso.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs para más detalles.'
        }
    }
}
