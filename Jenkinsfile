pipeline {
    agent { label 'debian-agent' }

    environment {
        // Carpeta donde se creará el entorno virtual de Python
        VENV_DIR = "${WORKSPACE}/venv"
    }

    stages {

        // === 1. DESCARGA DEL CÓDIGO DESDE EL REPOSITORIO ===
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        // === 2. EJECUCIÓN DE TESTS UNITARIOS Y GENERACIÓN DE COBERTURA ===
        stage('Run Unit Tests') {
            steps {
                sh """
                    # Crear entorno virtual
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate

                    # Instalar dependencias del proyecto
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Instalar librerías para testing y cobertura
                    pip install pytest pytest-cov coverage

                    # Ejecutar los tests y generar el reporte de cobertura en XML
                    pytest --maxfail=1 --disable-warnings \
                           --cov=. --cov-report=xml:coverage.xml \
                           --cov-report=term
                """
            }
        }

        // === 3. ANÁLISIS DE CÓDIGO CON SONARQUBE ===
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube-Local') {
                    script {
                        def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

                        sh """
                            # Añadimos SonarScanner al PATH y activamos el entorno virtual
                            export PATH=${scannerHome}/bin:\$PATH
                            . ${VENV_DIR}/bin/activate

                            # Ejecutamos el análisis de SonarQube con parámetros del proyecto
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

        // === 4. VALIDACIÓN DE LA CALIDAD DEL CÓDIGO ===
        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    // Espera a que SonarQube procese el análisis
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // === 5. CONSTRUCCIÓN DE LA IMAGEN DOCKER ===
        stage('Build Docker Image') {
            steps {
                // Se fuerza a no usar caché para evitar residuos
                sh 'docker build --no-cache -t miapp-flask:latest .'
            }
        }

        // === 6. DESPLIEGUE REMOTO EN LA VM ===
        stage('Deploy Flask App en remoto') {
            steps {
                sh """
                    # Exportar la imagen Docker local, comprimirla y enviarla por SSH
                    docker save miapp-flask:latest | bzip2 | ssh manuelcollado@192.168.56.106 'bunzip2 | docker load'

                    # En el servidor remoto: detener y eliminar contenedor antiguo si existe,
                    # y levantar uno nuevo con el puerto 8081 mapeado al 80 del contenedor
                    ssh manuelcollado@192.168.56.106 '
                        docker stop miapp-flask || true
                        docker rm miapp-flask || true
                        docker run -d --name miapp-flask -p 8081:80 miapp-flask:latest
                    '
                """
            }
        }

        // === 7. VERIFICAR QUE LA APP ESTÉ ARRIBA ===
        stage('Verificar Despliegue') {
            steps {
                sh """
                    echo 'Esperando 10 segundos para que el contenedor se inicie...'
                    sleep 10

                    # Se realizan hasta 90 intentos (≈3 minutos)
                    # para comprobar si la app responde en el puerto 8081
                    for i in {1..90}; do
                        if curl -fs http://192.168.56.106:8081 > /dev/null; then
                            echo 'La aplicación está en línea.'
                            exit 0
                        fi
                        echo "Intento \$i: la app aún no responde, esperando..."
                        sleep 2
                    done

                    echo 'La app no respondió en el tiempo esperado' >&2
                    exit 1
                """
            }
        }
    }

    // === RESULTADO FINAL DEL PIPELINE ===
    post {
        success {
            echo 'Pipeline completado correctamente.'
        }
        failure {
            echo 'Falló el pipeline. Revisa los logs.'
        }
    }
}

