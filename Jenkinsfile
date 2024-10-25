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
    }

    stages {
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

        stage('Deploy to EKS') {
            steps {
                script {
                    // Set the image for the deployment and initiate the rollout
                    sh """
                        kubectl set image deployment/${env.deployment_name} ${env.container_name}=${env.ecr_repo}:${env.image_tag} -n ${env.namespace}
                        kubectl rollout status deployment/${env.deployment_name} -n ${env.namespace}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment to EKS completed successfully."
        }
        failure {
            echo "Deployment failed. Check logs for details."
        }
    }
}
