pipeline {
    agent { label 'debian-agent' }

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov coverage
                    pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml:coverage.xml --cov-report=term
                """
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube-Local') {
                    script {
                        def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                        sh """
                            export PATH=${scannerHome}/bin:\$PATH
                            . ${VENV_DIR}/bin/activate
                            sonar-scanner \
                                -Dsonar.projectKey=miapp-flask \
                                -Dsonar.sources=. \
                                -Dsonar.python.version=3 \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.login=${SONAR_AUTH_TOKEN} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.exclusions=venv/**,tests/**
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build --no-cache -t miapp-flask:latest .'
            }
        }

        stage('Deploy Flask App en remoto') {
            steps {
                sh """
                    docker save miapp-flask:latest | bzip2 | ssh manuelcollado@192.168.56.106 'bunzip2 | docker load'
                    ssh manuelcollado@192.168.56.106 '
                        docker stop miapp-flask || true
                        docker rm miapp-flask || true
                        docker run -d --name miapp-flask -p 8081:80 miapp-flask:latest
                    '
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                sh """
                    for i in {1..30}; do
                        curl -f http://192.168.56.106:8081 && exit 0
                        echo 'Esperando a que la app arranque...'
                        sleep 1
                    done
                    echo 'La app no respondió en el tiempo esperado' >&2
                    exit 1
                """
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs.'
        }
    }
}
