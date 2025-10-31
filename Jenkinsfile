pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_NAME       = 'miapp-flask'
        DEPLOY_USER    = 'manuelcollado'
        DEPLOY_HOST    = '192.168.56.106'
        APP_PORT       = '8081'
        CONTAINER_PORT = '80'
        SONAR_SERVER   = 'SonarQube-Local'   // Configuración del plugin de Jenkins
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
                echo "Construyendo imagen Docker ${APP_NAME}..."
                sh "docker build -t ${APP_NAME}:latest ."
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo "Desplegando aplicación Flask en ${DEPLOY_HOST}..."
                sh """
                docker save ${APP_NAME}:latest | bzip2 | \
                ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                    bunzip2 | docker load
                    docker rm -f ${APP_NAME} || true
                    docker run -d -p ${APP_PORT}:${CONTAINER_PORT} --name ${APP_NAME} ${APP_NAME}:latest
                '
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo "Verificando que la app responde..."
                sh """
                ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                    MAX_TRIES=15
                    COUNT=0
                    until curl -s -o /dev/null -w "%{http_code}" http://localhost:${APP_PORT} | grep 200 > /dev/null; do
                        sleep 2
                        COUNT=$((COUNT+1))
                        if [ $COUNT -ge $MAX_TRIES ]; then
                            echo "Flask no responde después de 30 segundos"
                            exit 1
                        fi
                    done
                    echo "App Flask corriendo correctamente"
                '
                """
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando SonarQube...'
                withSonarQubeEnv("${SONAR_SERVER}") {
                    sh 'mvn sonar:sonar || echo "Usando plugin de Jenkins para análisis"'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate de SonarQube...'
                waitForQualityGate abortPipeline: true
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente: app desplegada y análisis SonarQube OK.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs en Jenkins.'
        }
    }
}


