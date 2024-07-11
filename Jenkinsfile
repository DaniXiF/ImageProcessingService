pipeline {
    agent any

    environment {
        image_tag="v$BUILD_NUMBER"
        nexus_repo="nexus:5000/repository/docker_images"
        dockerhub_repo="danixif"
    }

    stages {
        stage('Build') {
            agent {
                docker {
                    image 'pipelinecomponents/pylint:edge'
                     args  '--user root'

                    reuseNode true
                }
            }
            steps {
                sh """
                    pylint --output-format=text:pylint_results.txt polybot/*.py 
                """
                archiveArtifacts artifacts: 'pylint_result.txt'
            }
        }


        stage('Build docker image') {
            steps {
                sh """
                    docker run --privileged --rm tonistiigi/binfmt --install all
                    docker build -t polybot:${env.image_tag} .
                """
            }
        }
        stage('Sec Scan Stage'){
            steps{
                sh """
                    trivy image --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report polybot:${env.image_tag}

                """
                archiveArtifacts artifacts: 'trivy_report'
            }
        }
        stage('Push') {
            steps{
                parallel(
                    dockerhub: {
                        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                            sh """
                                echo $USERPASS | docker login -u $USERNAME --password-stdin
                                docker tag polybot:${env.image_tag}  ${env.dockerhub_repo}/polybot:${env.image_tag}
                                docker push ${env.dockerhub_repo}/polybot:${env.image_tag}
                            """
                        }
                    },
                    nexus: {
                        withCredentials([usernamePassword(credentialsId: 'Nexus_danchik', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                            sh """
                                echo $USERPASS | docker login ${env.nexus_repo} -u $USERNAME --password-stdin
                                docker tag polybot:${env.image_tag}  ${env.nexus_repo}/polybot:${env.image_tag}
                                docker push ${env.nexus_repo}/polybot:${env.image_tag}
                            """
                        }
                    }
                )
            }
        }
    }
}