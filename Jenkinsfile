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
                        docker build -t nexus:5000/repository/docker_images/polybot:v$BUILD_NUMBER .

                    '''
            }
        }
    }
        stage('Sec Scan Stage'){
            environment{
                SNYK_TOKEN = credential("SNYK_TOKEN")
            }
            steps{
                sh '''
                    trivy image --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report nexus:5000/repository/docker_images/polybot:v$BUILD_NUMBER

                '''
                archiveArtifacts artifacts: 'trivy_report'
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