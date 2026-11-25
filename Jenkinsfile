pipeline {
    agent any
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install') {
            steps {
                bat '''
                    python -m venv .venv
                    if errorlevel 1 exit /b 1
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pytest --junitxml=report.xml'
            }
        }
    }
    post {
        always {
            junit 'report.xml'
        }
    }
}
