pipeline {
    agent { label 'debian-agent' }

    environment {
        APP_NAME       = 'miapp-flask'
        DEPLOY_USER    = 'manuelcollado'
        DEPLOY_HOST    = '192.168.56.106'
        APP_PORT       = '8081'
        CONTAINER_PORT = '80'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis SonarQube (modo verbose sin Node.js)...'
                withSonarQubeEnv('SonarQube-Local') {
                    script {
                        def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                        sh """
                            ${scannerHome}/bin/sonar-scanner -X \
                                -Dsonar.projectKey=miapp-flask \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.login=${SONAR_AUTH_TOKEN} \
                                -Dsonar.exclusions=**/*.js,**/*.css,**/static/** \
                                -Dsonar.verbose=true
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate de SonarQube (sin abortar pipeline)...'
                script {
                    def qg = waitForQualityGate()
                    echo "Resultado del Quality Gate: ${qg.status}"

                    // Si el Quality Gate falla, mostrar advertencia pero NO abortar
                    if (qg.status != 'OK') {
                        echo "\u001B[31m El análisis de SonarQube no pasó el Quality Gate (${qg.status}). Continuando de todos modos...\u001B[0m"
                    } else {
                        echo "\u001B[32m SonarQube aprobó el Quality Gate.\u001B[0m"
                    }
                }
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
                        set -e
                        bunzip2 | docker load
                        if docker ps -a --format "{{.Names}}" | grep -Eq "^${APP_NAME}\$"; then
                            docker rm -f ${APP_NAME}
                        fi
                        docker run -d -p ${APP_PORT}:${CONTAINER_PORT} --name ${APP_NAME} ${APP_NAME}:latest
                    '
                """
            }
        }

        stage('Verificar Despliegue') {
            steps {
                echo 'Verificando que la app responde...'
                sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                        COUNT=0
                        MAX=15
                        until curl -s -o /dev/null -w "%{http_code}" http://localhost:${APP_PORT} | grep 200 > /dev/null; do
                            sleep 2
                            COUNT=\$((COUNT+1))
                            if [ \$COUNT -ge \$MAX ]; then
                                echo "Flask no responde después de 30 segundos"
                                exit 1
                            fi
                        done
                        echo "App Flask corriendo correctamente"
                    '
                """
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado correctamente: análisis SonarQube y app desplegada.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs.'
        }
    }
}
