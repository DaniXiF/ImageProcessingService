pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: dind
                    image: danixif/dind:v2
                    command:
                    - dockerd
                    args:
                    - --group=1000
                    - --insecure-registry=nexus:5000
                    securityContext:
                      privileged: true
                  - name: jnlp
                    image: jenkins/inbound-agent
                    tty: true
            '''
        }
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        image_tag = "v$BUILD_NUMBER"
        nexus_repo = "nexus:5000/repository/docker_images"
        dockerhub_repo = "danixif"
    }

    stages {
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
                                sh "docker build --platform=linux/arm64 -t polybot:${env.image_tag}-arm64 ."
                            }
                        )
                    }
                }
            }
        }

        stage('Sec Scan Stage') {
            steps {
                container('dind') {
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
        }

        stage('Push') {
            steps {
                container('dind') {
                    script {
                        sh """
                            aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 023196572641.dkr.ecr.us-east-1.amazonaws.com
                            docker tag polybot:${env.image_tag}-amd64 023196572641.dkr.ecr.us-east-1.amazonaws.com/danchik-app/polybot-repo:${env.image_tag}-amd64
                            docker push 023196572641.dkr.ecr.us-east-1.amazonaws.com/danchik-app/polybot-repo:${env.image_tag}-amd64
                        """
                    }
                }
            }
        }
    }
}
