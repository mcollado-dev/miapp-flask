pipeline {
    agent any  // Ejecuta el pipeline en cualquier agente disponible

    environment {
        // Variable de entorno con las credenciales de SonarQube (token configurado en Jenkins)
        SONARQUBE = credentials('sonarqube-token')

        // Herramienta SonarQube Scanner instalada en Jenkins (configurada en Manage Jenkins > Tools)
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner'
    }

    stages {

        // Etapa 1: Clonar el repositorio desde GitHub
        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                checkout scm
            }
        }

        // Etapa 2: Ejecutar los tests unitarios con cobertura dentro de un entorno virtual
        stage('Run Unit Tests') {
            steps {
                echo 'Ejecutando tests con cobertura (entorno virtual)...'
                sh '''
                    # Crear entorno virtual de Python
                    python3 -m venv venv

                    # Activar el entorno virtual
                    . venv/bin/activate

                    # Actualizar pip e instalar dependencias necesarias
                    pip install --upgrade pip
                    pip install -r requirements.txt pytest pytest-cov

                    # Ejecutar los tests con cobertura de código y generar informe XML
                    pytest --maxfail=1 --disable-warnings -q --cov=. --cov-report=xml
                '''
            }
        }

        // Etapa 3: Ejecutar el análisis estático de código con SonarQube
        stage('SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis de SonarQube...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        # Activar entorno virtual
                        . venv/bin/activate

                        # Ejecutar el escáner de SonarQube
                        # Se excluyen los directorios venv/ y __pycache__ para evitar falsos positivos
                        sonar-scanner \
                          -Dsonar.projectKey=miapp-flask \
                          -Dsonar.projectName="Mi App Flask" \
                          -Dsonar.language=python \
                          -Dsonar.python.version=3 \
                          -Dsonar.sources=. \
                          -Dsonar.exclusions=venv/**,__pycache__/**,**/venv/**,**/__pycache__/** \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.login=$SONARQUBE
                    '''
                }
            }
        }

        // Etapa 4: Esperar el resultado del Quality Gate de SonarQube
        stage('Quality Gate') {
            steps {
                echo 'Esperando resultado del Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // Etapa 5: Construir la imagen Docker de la aplicación Flask
        stage('Build Docker Image') {
            steps {
                echo 'Construyendo imagen Docker...'
                sh '''
                    docker build -t miapp-flask:latest .
                '''
            }
        }

        // Etapa 6: Desplegar la aplicación Flask en un contenedor Docker
        stage('Deploy Flask App') {
            steps {
                echo 'Desplegando aplicación Flask...'
                sh '''
                    # Ejecutar el contenedor en segundo plano, exponiendo el puerto 80
                    docker run -d -p 80:80 --name miapp-flask miapp-flask:latest
                '''
            }
        }

        // Etapa 7: Verificar que la aplicación Flask esté funcionando correctamente
        stage('Verificar Despliegue') {
            steps {
                echo 'Verificando que la aplicación Flask esté corriendo...'
                sh '''
                    # Esperar unos segundos para permitir que el contenedor arranque
                    sleep 5

                    # Hacer una petición HTTP al contenedor y verificar respuesta
                    curl -f http://localhost:80 || (echo "Error: La aplicación no responde" && exit 1)
                '''
            }
        }
    }

    post {
        // Si el pipeline finaliza correctamente
        success {
            echo 'Pipeline ejecutado correctamente.'
        }

        // Si ocurre algún error en cualquier etapa
        failure {
            echo 'Falló el pipeline. Revisa los logs para más detalles.'
        }
    }
}
