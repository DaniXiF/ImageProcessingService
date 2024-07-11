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
                sh "docker run --privileged --rm tonistiigi/binfmt --install all"
                parallel(
                    amd64: {
                        sh "docker build --platform=linux/amd64 -t polybot:${env.image_tag}-amd64 ."
                    },
                    arm64: {
                        sh " docker build --platform=linux/arm64 -t polybot:${env.image_tag}-arm64 ."
                    }
                )
            }
        }    
        stage('Sec Scan Stage'){
            steps{
                parallel(
                    amd64: {
                        sh "trivy image --platform=linux/amd64 --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report polybot:${env.image_tag}-amd64"
                    },
                    arm64: {
                        sh "trivy image --platform=linux/arm64 --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report polybot:${env.image_tag}-arm64"
                    }
                )
                archiveArtifacts artifacts: 'trivy_report_*'
            }
        }
        stage('Push') {
            steps{
                sh """
                    docker manifest create polybot:${env.image_tag} -a polybot:${env.image_tag}-arm64 -a polybot:${env.image_tag}-amd64
                """
                parallel(
                    dockerhub: {
                        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                            sh "echo $USERPASS | docker login -u $USERNAME --password-stdin"
                        }       
                        parallel(
                            arm64: {
                                sh"""
                                    docker tag polybot:${env.image_tag}-arm64  ${env.dockerhub_repo}/polybot:${env.image_tag}-arm64
                                    docker push ${env.dockerhub_repo}/polybot:${env.image_tag}-arm64
                                """
                            },
                            amd64: {
                                sh"""
                                    docker tag polybot:${env.image_tag}-amd64  ${env.dockerhub_repo}/polybot:${env.image_tag}-amd64
                                    docker push ${env.dockerhub_repo}/polybot:${env.image_tag}-amd64
                                """
                            }
                        )
                        sh """
                            docker manifest create ${env.dockerhub_repo}/polybot:${env.image_tag} \
                                ${env.dockerhub_repo}/polybot:${env.image_tag}-arm64 \
                                ${env.dockerhub_repo}/polybot:${env.image_tag}-amd64
                            docker manifest push -p ${env.dockerhub_repo}/polybot:${env.image_tag}
                        """        
                    },
                    nexus: {
                        withCredentials([usernamePassword(credentialsId: 'Nexus_danchik', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                            sh """
                                echo $USERPASS | docker login ${env.nexus_repo} -u $USERNAME --password-stdin
                                docker tag polybot:${env.image_tag}  ${env.nexus_repo}/polybot:${env.image_tag}
                                docker push ${env.nexus_repo}/polybot:${env.image_tag}
                                docker manifest push ${env.nexus_repo}/polybot:${env.image_tag}
                            """
                        }
                    }
                )
                sh """ 
                
                """
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