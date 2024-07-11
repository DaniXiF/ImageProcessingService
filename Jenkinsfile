pipeline {
    agent any

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        image_tag="v$BUILD_NUMBER"
        nexus_repo="nexus:5000/repository/docker_images"
        dockerhub_repo="danixif"
    }
    

    stages {
        stage('Lint') {
            agent {
                docker {
                    image 'pipelinecomponents/pylint:edge'
                     args  '-u root'

                    reuseNode true
                }
            }
            steps {
                sh """
                    pylint --exit-zero --output-format=parseable --reports=no polybot/*.py > pylint.log
                """
                archiveArtifacts artifacts: 'pylint.log'
            }
            post {
                always {
                    sh 'cat pylint.log'
                    recordIssues (
                        enabledForFailure: true,
                        aggregatingResults: true,
                        tools: [pyLint(name: 'Pylint', pattern: 'pylint.log')]
                    )
                }
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
    post{
        always{
            cleanWs()
            sh"""
                docker image rm -f polybot:${env.image_tag} ${env.dockerhub_repo}/polybot:${env.image_tag} ${env.nexus_repo}/polybot:${env.image_tag} || true
            """
        }
    }
}