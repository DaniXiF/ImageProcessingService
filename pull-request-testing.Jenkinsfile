pipeline {
    agent any

    stages {
        stage('Unittest') {
            steps {
                sh 'echo "testing"'
            }
        }
        stage('Installing Requirements') {
            steps {
                sh '''
                    echo "Installing Requirements"
                    python -m venv venv
                    ./venv/bin/activate
                    pip install -r requirements.txt
                    echo 'Hello Jenkins'
                 '''

            }
        }
        stage('Functional test') {
            steps {
                sh 'echo "testing"'
            }
        }
    }
}