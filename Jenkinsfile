pipeline{
    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(defaultValue: false, description: 'Zip Image Gen Lambda Code', name: 'ZIP_IMAGE')
        booleanParam(defaultValue: false, description: 'Zip Insta Post Lambda Code', name: 'ZIP_INSTA')
        booleanParam(defaultValue: false, description: 'Upload Image Gen Zip to S3', name: 'IMAGE_S3_UPLOAD')
        booleanParam(defaultValue: false, description: 'Upload Insta Post Zip to S3', name: 'INSTA_S3_UPLOAD')
        booleanParam(defaultValue: false, description: 'Update Terraform Variables', name: 'UPDATE_TF_VAR')
        booleanParam(defaultValue: false, description: 'Apply Terraform Configuration', name: 'TERRAFORM_APPLY')
    }

    environment {
        IMAGE_GEN_ZIP_FILE = "image_gen_1.0.${BUILD_NUMBER}.zip"
        INSTA_POST_ZIP_FILE = "insta_post_1.0.${BUILD_NUMBER}.zip"
        TF_CLI_CONFIG_FILE = "${WORKSPACE}/.terraformrc"
    }

    stages{
        stage('Clean'){
            steps{
                echo 'Cleaning workspace'
                sh 'rm -rf *'
            }
        }

        stage('Checkout'){
            steps{
                echo 'Checking out code'
                checkout scm
                sh 'ls -la'
                sh 'pwd'
            }
        }

        stage('Zip Image Gen Lambda Package'){
            when{
                expression { params.ZIP_IMAGE == true }
            }
            steps{
                echo 'packaging zip file'
                sh 'pwd'
                sh "ls -la"
                
                sh "zip -r ./${env.IMAGE_GEN_ZIP_FILE} image_gen.py national-days.json"
                sh "ls -la"

                echo '********** image gen lambda zip file created'
            }
        }

        stage('Zip Insta Post Lambda Package'){
            when{
                expression { params.ZIP_INSTA == true }
            }
            steps{
                echo 'packaging zip file'
                sh 'pwd'
                sh "ls -la"
                
                sh "zip -r ./${env.INSTA_POST_ZIP_FILE} insta_post.py"
                sh "ls -la"
                echo '********** insta post lambda zip file created'
            }
        }

        stage('Upload Image Gen Zip to S3'){
            when{
                expression { params.IMAGE_S3_UPLOAD == true && params.ZIP_IMAGE == true }
            }
            steps{
                script{
                    upload_to_s3(env.IMAGE_GEN_ZIP_FILE)
                }
            }
        }

        stage('Upload Insta Post Zip to S3'){
            when{
                expression { params.INSTA_S3_UPLOAD == true && params.ZIP_INSTA == true }
            }
            steps{
                script{
                    upload_to_s3(env.INSTA_POST_ZIP_FILE)
                }
            }
        }

        stage('Terraform Init') {
            when{
                expression {
                    params.TERRAFORM_APPLY
                }
            }
            steps{
                script{
                    dir ('terraform-iac') {
                        sh 'pwd'
                        sh 'ls -la'

                        checkout([$class: 'GitSCM', branches: [[name: 'main']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'github_credentials', url: 'https://github.com/allenac86/spooky-days-twitter-iac']]])

                        dir ('./Terraform') {
                            env.TF_CLI_CONFIG_FILE = "./.terraformrc"
                            sh 'pwd'
                            sh 'ls -la'

                            withCredentials([string(credentialsId: 'terraform_backend_token', variable: 'TOKEN')]) {
                                writeFile file: env.TF_CLI_CONFIG_FILE, text: """
                                credentials "app.terraform.io" {
                                    token = "${TOKEN}"
                                }
                                """
                            }

                            sh 'terraform init'
                        }
                    }
                }
            }
        }

        stage('Update Terraform Variables'){
            when{
                expression {
                    params.UPDATE_TF_VAR == true && params.TERRAFORM_APPLY == true && (params.IMAGE_S3_UPLOAD == true || params.INSTA_S3_UPLOAD == true)
                }
            }
            steps{
                script{
                    dir ('terraform-iac/Terraform') {
                        if (params.IMAGE_S3_UPLOAD == true) {
                            sh 'pwd'
                            echo 'Updating Terraform Variable for Image Gen Lambda'

                            withCredentials([string(credentialsId: 'terraform_backend_token', variable: 'TOKEN'), string(credentialsId: 'image_lambda_file_var_id', variable: 'IMAGE_VAR_ID'), string(credentialsId: 'image_zip_var_key', variable: 'IMAGE_VAR_KEY'), string(credentialsId: 'terraform_workspace_id', variable: 'WORKSPACE_ID')]) {
                                update_terraform_variable(IMAGE_VAR_ID, IMAGE_VAR_KEY, env.IMAGE_GEN_ZIP_FILE, WORKSPACE_ID, TOKEN)
                            }
                        }

                        if (params.INSTA_S3_UPLOAD == true) {
                            sh 'pwd'
                            echo 'Updating Terraform Variable for Insta Post Lambda'

                            withCredentials([string(credentialsId: 'terraform_backend_token', variable: 'TOKEN'), string(credentialsId: 'insta_lambda_file_var_id', variable: 'INSTA_VAR_ID'), string(credentialsId: 'insta_zip_var_key', variable: 'INSTA_VAR_KEY'), string(credentialsId: 'terraform_workspace_id', variable: 'WORKSPACE_ID')]) {
                                update_terraform_variable(INSTA_VAR_ID, INSTA_VAR_KEY, env.INSTA_POST_ZIP_FILE, WORKSPACE_ID, TOKEN)
                            }
                        }
                    }
                }
            }
        }

        stage('Terraform Plan') {
            when{
                expression {
                    params.TERRAFORM_APPLY == true
                }
            }
            steps{
                script{
                    dir ('terraform-iac/Terraform') {
                        sh 'pwd'
                        sh 'ls -la'

                        withCredentials([string(credentialsId: 'terraform_backend_token', variable: 'TOKEN')]) {
                            writeFile file: env.TF_CLI_CONFIG_FILE, text: """
                            credentials "app.terraform.io" {
                                token = "${TOKEN}"
                            }
                            """
                        }

                        sh 'terraform plan'     
                    }
                }
            }
        }

        stage('Terraform Apply') {
            when{
                expression {
                    params.TERRAFORM_APPLY == true
                }
            }
            steps{
                script{
                    dir ('terraform-iac/Terraform') {
                        sh 'pwd'
                        sh 'ls -la'

                        withCredentials([string(credentialsId: 'terraform_backend_token', variable: 'TOKEN')]) {
                            writeFile file: env.TF_CLI_CONFIG_FILE, text: """
                            credentials "app.terraform.io" {
                                token = "${TOKEN}"
                            }
                            """
                        }

                        sh 'terraform apply -auto-approve'
                    }
                }
            }
        }
    }
}

def upload_to_s3(file) {
    echo "Using AWS CLI to upload package to s3"
                    withCredentials([string(credentialsId: 'aws_access_key_id', variable: 'AWS_ACCESS_KEY_ID'), string(credentialsId: 'aws_secret_access_key', variable: 'AWS_SECRET_ACCESS_KEY'), string(credentialsId: 'aws_s3_bucket_name', variable: 'AWS_S3_BUCKET')]) {
                        sh "aws s3 cp ./${file} ${AWS_S3_BUCKET}"
                    }
}

def update_terraform_variable(var_id, var_key, var_value, workspace_id, token) {
    def payload = """
        {
            "data": {
                "id": "${var_id}",
                "attributes": {
                    "key": "${var_key}",
                    "value": "${var_value}",
                    "category": "terraform",
                    "hcl": false,
                    "sensitive": false
                },
                "type": "vars"
                }
        }
    """

    sh """
        curl -s --header "Authorization: Bearer ${token}" \\
        --header "Content-Type: application/vnd.api+json" \\
        --request PATCH \\
        --data '$payload' \\
        "https://app.terraform.io/api/v2/workspaces/${WORKSPACE_ID}/vars/${var_id}"
    """
}