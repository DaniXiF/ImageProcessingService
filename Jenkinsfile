pipeline {
    agent any
    stages {
        stage('Build docker image'){
            steps {
		    withCredentials(
                 [usernamePassword(credentialsId: 'Nexus_danchik', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]
              ) {
                    sh '''
                        echo $USERPASS | docker login nexus:5000 -u $USERNAME --password-stdin
                        docker run --privileged --rm tonistiigi/binfmt --install all
                        docker buildx create --name builder --bootstrap --use || docker buildx use builder
                        docker build -t nexus:5000/repository/docker_images/polybot:v$BUILD_NUMBER .

                    '''
            }
        }
    }
        stage('Trivy'){
            steps{
                sh '''
                    trivy image nexus:5000/repository/docker_images/polybot:v$BUILD_NUMBER
                '''
            }
        }
         stage('Push'){
            steps{
                sh '''
                    docker push nexus:5000/repository/docker_images/polybot:v$BUILD_NUMBER
                '''
            }
        }
}
}