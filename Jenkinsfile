pipeline {
    agent any
    stages {
        stage('Build docker image'){
            steps {
		    withCredentials(
                 [usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USERPASS', passwordVariable: 'USERPASS')]
              ) {
                    sh '''
                        echo "hello world"
                    '''
            }
        }
    }
}
