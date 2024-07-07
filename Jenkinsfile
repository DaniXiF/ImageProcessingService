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
                        docker run --privileged --rm tonistiigi/binfmt --install all
                        docker buildx create --name builder --bootstrap --use || docker buildx use builder
                        docker buildx build --platform linux/amd64,linux/arm64 --push -t danixif/polybot:v$BUILD_NUMBER .

                    '''
            }
        }
    }
        stage('Trivy'){
            steps{
                sh '''
                    trivy image danixif/polybot:v$BUILD_NUMBER
                '''
            }
        }
}
}