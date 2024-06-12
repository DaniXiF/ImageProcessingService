pipeline {
    agent any
    stages {
        stage('Build docker image'){
            steps {
		    withCredentials(
                 [usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]
              ) {
                    sh '''
                        echo $USERPASS | docker login -u $USERNAME --password-stdin
                        docker build -t danixif/polybot:$BUILD_NUMBER .
                        docker push danixif/polybot:$BUILD_NUMBER
                    '''
            }
        }
    }
}
}