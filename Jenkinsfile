pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: dind
                    image: danixif/dind:v1
                    command:
                    - dockerd
                    - --group=1000
                    - --insecure-registry=nexus:5000
                    securityContext:
                      privileged: true
                  - name: jnlp
                    image: jenkins/inbound-agent
                    tty: true
                  - name: trivy
                    image: aquasec/trivy:latest
                '''
        }
    }


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
        // stage('Lint') {
        //     agent {
        //         docker {
        //             image 'pipelinecomponents/pylint:edge'
        //              args  '-u root'

        //             reuseNode true
        //         }
        //     }
        //     steps {
        //         sh """
        //             pylint --exit-zero --output-format=parseable --reports=no polybot/*.py > pylint.log
        //         """
        //         archiveArtifacts artifacts: 'pylint.log'
        //     }
        //     post {
        //         always {
        //             sh 'cat pylint.log'
        //             recordIssues (
        //                 enabledForFailure: true,
        //                 aggregatingResults: true,
        //                 tools: [pyLint(name: 'Pylint', pattern: 'pylint.log')]
        //             )
        //         }
        //     }

        // }


        stage('Build docker image') {
            steps {
                container('dind') {
                    script {
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
            }
        }    
        stage('Sec Scan Stage'){
            steps{
                container('dind')
                    script {
                        parallel(
                            "Trivy Scan AMD64": {
                                sh "trivy image --platform=linux/amd64 --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report_amd64 polybot:${env.image_tag}-amd64"
                            },
                            "Trivy Scan ARM64": {
                                sh "trivy image --platform=linux/arm64 --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report_arm64 polybot:${env.image_tag}-arm64"
                            }
                        )
                        archiveArtifacts artifacts: 'trivy_report_*'
                    }
            }
        }
        stage('Push') {
            steps{
                script {
                    parallel(
                        Dockerhub: {
                            withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                                sh "echo $USERPASS | docker login -u $USERNAME --password-stdin"
                            }       
                            parallel(
                                "Docker Hub Push ARM64": {
                                    sh"""
                                        docker tag polybot:${env.image_tag}-arm64  ${env.dockerhub_repo}/polybot:${env.image_tag}-arm64
                                        docker push ${env.dockerhub_repo}/polybot:${env.image_tag}-arm64
                                    """
                                },
                                "Docker Hub Push AMD64": {
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
                        Nexus: {
                            withCredentials([usernamePassword(credentialsId: 'Nexus_danchik', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                                sh """
                                    echo $USERPASS | docker login ${env.nexus_repo} -u $USERNAME --password-stdin
                                """
                            }
                            parallel(
                                "Nexus Push ARM64": {
                                    sh"""
                                        docker tag polybot:${env.image_tag}-arm64  ${env.nexus_repo}/polybot:${env.image_tag}-arm64
                                        docker push ${env.nexus_repo}/polybot:${env.image_tag}-arm64
                                    """
                                },
                                "Nexus Push AMD64": {
                                    sh"""
                                        docker tag polybot:${env.image_tag}-amd64  ${env.nexus_repo}/polybot:${env.image_tag}-amd64
                                        docker push ${env.nexus_repo}/polybot:${env.image_tag}-amd64
                                    """
                                }
                            )
                            sh """
                                docker manifest create --insecure ${env.nexus_repo}/polybot:${env.image_tag} \
                                    ${env.nexus_repo}/polybot:${env.image_tag}-arm64 \
                                    ${env.nexus_repo}/polybot:${env.image_tag}-amd64
                                docker manifest push --insecure -p ${env.nexus_repo}/polybot:${env.image_tag}
                            """
                        }
                    )
                }
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