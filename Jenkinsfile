pipeline {
    agent any
    
    environment {
        // These are placeholders for your Azure resources
        REGISTRY = 'trionix.azurecr.io'
        IMAGE_NAME = 'trionix-app'
        
        // This relies on you saving your Azure details inside Jenkins's "Credentials" manager
        DOCKER_CREDS_ID = 'azure-acr-credentials'  
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls the latest code from GitHub
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                // Build the image using the Dockerfile we just created
                bat 'docker build -t %REGISTRY%/%IMAGE_NAME%:%BUILD_ID% .'
                bat 'docker build -t %REGISTRY%/%IMAGE_NAME%:latest .'
            }
        }
        
        stage('Push to Azure Container Registry') {
            steps {
                echo "Pushing Docker image to Azure..."
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDS_ID}", passwordVariable: 'ACR_PASSWORD', usernameVariable: 'ACR_USERNAME')]) {
                    bat 'docker login -u %ACR_USERNAME% -p %ACR_PASSWORD% %REGISTRY%'
                    bat 'docker push %REGISTRY%/%IMAGE_NAME%:%BUILD_ID%'
                    bat 'docker push %REGISTRY%/%IMAGE_NAME%:latest'
                }
            }
        }
    }
}
