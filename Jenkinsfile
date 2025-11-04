pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_PORT = "5000"
        SONAR_HOST_URL = "http://localhost:9000"
        SONAR_AUTH_TOKEN = credentials('sonarqube-token')
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                git branch: 'main', url: 'https://github.com/mcollado-dev/miapp-flask.git'
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Ejecutando tests con cobertura...'
                sh '''
                    # Crear entorno virtual
                    python3 -m venv venv
                    . venv/bin/activate

                    # Instalar dependencias necesarias
                    pip install --no-cache-dir -r requirements.txt
                    pip install pytest pytest-cov

                    # Ejecutar tests y generar el reporte coverage.xml
                    pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml:coverage.xml --cov-report=term

                    # Mostrar si el archivo se generó correctamente
                    ls -l coverage.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis SonarQube...'
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        . venv/bin/activate
                        sonar-scanner \
                            -Dsonar.projectKey=miapp-flask \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3 \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=${SONAR_AUTH_TOKEN} \
                            -Dsonar.coverageReportPaths=coverage.xml
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate...'
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Construyendo imagen Docker...'
                sh '''
                    docker build -t miapp-flask .
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo 'Desplegando aplicación Flask...'
                sh '''
                    docker stop miapp-flask-container || true
                    docker rm miapp-flask-container || true
                    docker run -d -p ${APP_PORT}:80 --name miapp-flask-container miapp-flask
                '''
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo 'Verificando despliegue...'
                sh '''
                    sleep 5
                    curl -f http://localhost:${APP_PORT} || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs para más detalles.'
        }
    }
}
