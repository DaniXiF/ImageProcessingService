pipeline {
    agent any

    stages {
        stage('Unittest') {
            steps {
                sh 'echo "testing"'
            }
        }
        stage('Lint') {
            steps {
                sh '''
                    pip install requirements.txt
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