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
                // Crear y activar entorno virtual
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
                        // Ajusta el nombre exacto de tu SonarScanner en Jenkins Global Tool Config
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
                sh 'docker build -t miapp-flask:latest .'
            }
        }

        stage('Deploy Flask App en remoto') {
            steps {
                sh """
                    ssh manuelcollado@192.168.56.106 '
                        docker stop miapp-flask || true
                        docker rm miapp-flask || true
                        docker run -d --name miapp-flask -p 5000:5000 miapp-flask:latest
                    '
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                sh "curl -f http://remote-server:5000 || exit 1"
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
