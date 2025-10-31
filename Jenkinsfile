pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://192.168.56.106:9000'
        SONAR_AUTH_TOKEN = credentials('sonar-token')  // Token guardado en Jenkins
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Construyendo imagen Docker...'
                sh "docker build -t miapp-flask:latest ."
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo 'Desplegando app en host remoto...'
                sh """
                    docker save miapp-flask:latest | bzip2 | \\
                    ssh manuelcollado@192.168.56.106 \\
                    "bunzip2 | docker load; \
                     docker rm -f miapp-flask || true; \
                     docker run -d -p 8081:80 --name miapp-flask miapp-flask:latest"
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo 'Comprobando que Flask responde...'
                sh """
                    ssh manuelcollado@192.168.56.106 \\
                    "MAX_TRIES=15; COUNT=0; \
                     until curl -s -o /dev/null -w '%{http_code}' http://localhost:8081 | grep 200 > /dev/null; do \
                        sleep 2; COUNT=\$((COUNT+1)); \
                        if [ \$COUNT -ge \$MAX_TRIES ]; then echo 'Flask no responde'; exit 1; fi; \
                     done; \
                     echo 'App Flask corriendo correctamente'"
                """
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis SonarQube...'
                withSonarQubeEnv('SonarQube-Local') {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=miapp-flask \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_AUTH_TOKEN}
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate de SonarQube...'
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente: app desplegada y análisis SonarQube OK.'
        }
        failure {
            echo 'Pipeline falló, revisa los logs.'
        }
    }
}
