pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_NAME        = 'miapp-flask'
        DEPLOY_USER     = 'manuelcollado'
        DEPLOY_HOST     = '192.168.56.106'
        APP_PORT        = '8081'      // Puerto del host
        CONTAINER_PORT  = '80'        // Puerto interno del contenedor
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
                echo 'Construyendo imagen Docker de Flask...'
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

        stage('Verify Deployment') {
            steps {
                echo 'Verificando que la app responde...'
                sh """
                ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                    sleep 5
                    STATUS=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${APP_PORT})
                    if [ "\$STATUS" -eq 200 ]; then
                        echo "App Flask corriendo correctamente"
                    else
                        echo "Error: App Flask no responde (HTTP \$STATUS)"
                        exit 1
                    fi
                '
                """
            }
        }
    }

    post {
        success {
            echo 'Despliegue completado correctamente.'
        }
        failure {
            echo 'Falló el despliegue. Revisa los logs.'
        }
    }
}
