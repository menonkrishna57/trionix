pipeline {
    agent any
    
    environment {
        // These are placeholders for your Azure resources
        REGISTRY = 'youracrname.azurecr.io'  // We will change this once you create an Azure Container Registry
        IMAGE_NAME = 'trionix-app'
        
        // This relies on you saving your Azure details inside Jenkins's "Credentials" manager
        DOCKER_CREDS_ID = 'azure-acr-credentials'  
        AZURE_SERVICE_PRINCIPAL_ID = 'azure-sp-credentials'
        
        AZURE_RESOURCE_GROUP = 'trionix-rg'
        AZURE_WEB_APP = 'trionix-production'
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

        stage('Deploy to Azure Web App') {
            steps {
                echo "Deploying the new container to Azure..."
                // We use Azure CLI to restart the app service and pull the new container
                withCredentials([azureServicePrincipal(credentialsId: "${AZURE_SERVICE_PRINCIPAL_ID}", clientIdVariable: 'CLIENT_ID', clientSecretVariable: 'CLIENT_SECRET', subscriptionIdVariable: 'SUB_ID', tenantIdVariable: 'TENANT_ID')]) {
                    bat 'az login --service-principal -u %CLIENT_ID% -p %CLIENT_SECRET% --tenant %TENANT_ID%'
                    bat 'az webapp config container set --name %AZURE_WEB_APP% --resource-group %AZURE_RESOURCE_GROUP% --docker-custom-image-name %REGISTRY%/%IMAGE_NAME%:latest'
                    bat 'az webapp restart --name %AZURE_WEB_APP% --resource-group %AZURE_RESOURCE_GROUP%'
                }
            }
        }
    }
}
