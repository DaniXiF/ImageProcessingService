pipeline {
    agent { label 'ec2-fleet' }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        aws_region = "us-east-2"               // Replace with your AWS region
        ecr_registry = "023196572641.dkr.ecr.us-east-2.amazonaws.com"  // Replace with your AWS ECR registry
        ecr_repo = "${ecr_registry}/danchik/polybot-app" // Replace with your ECR repository
        image_tag = "v361"           // Image tag from the build pipeline
        cluster_name = "eks-X10-prod-01"     // Replace with your EKS cluster name
        kubeconfig_path = "~/.kube/config"     // Path to kubeconfig
        deployment_name = "polybot-app"    // Replace with your Kubernetes deployment name
        container_name = "polybot"      // Replace with your container name in the deployment
        namespace = "bino-dan-polybot"                  // Kubernetes namespace
        sns_topic_arn = "arn:aws:sns:us-east-2:023196572641:Polybot_Deployment" // Replace with your SNS Topic ARN
    }

    stages {
        stage('AWS Configure') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'Danchik AWS US-2-Ohio'
                ]]) {
                    script {
                        // Configure AWS CLI with the provided credentials and region
                        sh """
                            aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
                            aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
                            aws configure set region ${aws_region}
                        """
                    }
                }
            }
        }

        stage('Configure kubectl') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'Danchik AWS US-2-Ohio'
                ]]) {
                    script {
                        // Configure kubectl to use the EKS cluster
                        sh """
                            aws eks update-kubeconfig --name ${env.cluster_name} --region ${env.aws_region} --kubeconfig ${env.kubeconfig_path}
                        """
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    // Create or update the deployment without any checks
                    sh """
                        kubectl apply -f - <<EOF
                        apiVersion: apps/v1
                        kind: Deployment
                        metadata:
                          name: ${env.deployment_name}
                          namespace: ${env.namespace}
                        spec:
                          replicas: 1
                          selector:
                            matchLabels:
                              app: ${env.deployment_name}
                          template:
                            metadata:
                              labels:
                                app: ${env.deployment_name}
                            spec:
                              containers:
                              - name: ${env.container_name}
                                image: ${env.ecr_repo}:${env.image_tag}
                                ports:
                                - containerPort: 80
                        EOF
                        kubectl rollout status deployment/${env.deployment_name} -n ${env.namespace}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment to EKS completed successfully."
            sendSNSNotification("SUCCESS", "Deployment to EKS completed successfully for ${env.deployment_name}")
        }
        failure {
            echo "Deployment failed. Check logs for details."
            sendSNSNotification("FAILURE", "Deployment failed for ${env.deployment_name}. Check logs for details.")
        }
    }
}

def sendSNSNotification(status, message) {
    sh """
        aws sns publish \
            --region ${env.aws_region} \
            --topic-arn ${env.sns_topic_arn} \
            --message "Deployment Status: ${status}\\nMessage: ${message}" \
            --subject "Deployment ${status}: ${env.deployment_name}"
    """
}
