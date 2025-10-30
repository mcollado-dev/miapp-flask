pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_NAME = 'miapp-flask'
        DEPLOY_USER = 'manuelcollado'
        DEPLOY_HOST = '192.168.56.106'
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
                sh """
                    docker build -t ${APP_NAME}:latest .
                """
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo "Desplegando aplicación Flask en ${DEPLOY_HOST}..."
                sh """
                    docker save ${APP_NAME}:latest | bzip2 | \
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} 'bunzip2 | docker load'

                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                        docker rm -f ${APP_NAME} || true
                        docker run -d -p 8081:80 --name ${APP_NAME} ${APP_NAME}:latest
                    '
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo 'Verificando que la app responde...'
                sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} 'curl -I http://localhost:8081 | grep "200 OK"'
                """
            }
        }
    }

    post {
        success {
            echo 'Despliegue de la app Flask completado correctamente.'
        }
        failure {
            echo 'Falló el despliegue. Revisa los logs.'
        }
    }
}
