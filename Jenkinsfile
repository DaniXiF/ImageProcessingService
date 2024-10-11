pipeline {
    agent {
        label 'ec2-fleet-ohio'
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        image_tag = "v$BUILD_NUMBER"
        ecr_registry = "023196572641.dkr.ecr.us-east-1.amazonaws.com"
        ecr_repo = "${ecr_registry}/danchik-app/polybot-repo"
        aws_region = "us-east-1"
        s3_bucket = "danchik-s3liter-bucket" // Your S3 bucket environment variable
    }

    stages {
        stage('Setup Docker') {
            steps {
                script {
                    // Ensure Docker is ready and install multi-arch support
                    sh "docker run --privileged --rm tonistiigi/binfmt --install all"
                }
            }
        }

        stage('Build docker image') {
            steps {
                script {
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

        stage('Sec Scan Stage') {
            steps {
                script {
                    parallel(
                        "Trivy Scan AMD64": {
                            sh "trivy image  --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report_amd64 polybot:${env.image_tag}-amd64"
                        },
                        "Trivy Scan ARM64": {
                            sh "trivy image --severity HIGH,CRITICAL --ignore-unfixed --output trivy_report_arm64 polybot:${env.image_tag}-arm64"
                        }
                    )
                    archiveArtifacts artifacts: 'trivy_report_*'
                }
            }
        }

        stage('Upload Trivy Scan Reports to S3') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'aws-key'
                ]]) {
                    script {
                        // Upload the Trivy scan reports to S3
                        sh """
                            aws s3 cp trivy_report_amd64 s3://${env.s3_bucket}/trivy_reports/trivy_report_amd64_${env.BUILD_NUMBER}.txt
                            aws s3 cp trivy_report_arm64 s3://${env.s3_bucket}/trivy_reports/trivy_report_arm64_${env.BUILD_NUMBER}.txt
                        """
                    }
                }
            }
        }

        stage('Push to Amazon ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'aws-key'
                ]]) {
                    script {
                        sh """
                            # Authenticate Docker to the ECR registry
                            aws ecr get-login-password --region ${env.aws_region} | docker login --username AWS --password-stdin ${env.ecr_registry}

                            # Tag the images for ECR
                            docker tag polybot:${env.image_tag}-amd64 ${env.ecr_repo}:${env.image_tag}-amd64
                            docker tag polybot:${env.image_tag}-arm64 ${env.ecr_repo}:${env.image_tag}-arm64

                            # Push the images to ECR
                            docker push ${env.ecr_repo}:${env.image_tag}-amd64
                            docker push ${env.ecr_repo}:${env.image_tag}-arm64

                            # Create and push multi-architecture manifest
                            docker manifest create ${env.ecr_repo}:${env.image_tag} \\
                                --amend ${env.ecr_repo}:${env.image_tag}-amd64 \\
                                --amend ${env.ecr_repo}:${env.image_tag}-arm64
                            docker manifest push ${env.ecr_repo}:${env.image_tag}
                        """
                    }
                }
            }
        }
    }
}
