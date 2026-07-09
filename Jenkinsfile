pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        UV_BIN = '/usr/local/bin/uv'
        DEPLOY_DIR = '/var/www/fastapi-react'
        BACKEND_DEPLOY_DIR = '/opt/fastapi-react-backend'
        BACKEND_SERVICE = 'fastapi-fullstack'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment Check') {
            steps {
                sh '''
                    set -eux

                    echo "===== GIT ====="
                    git --version

                    echo "===== NODE ====="
                    node --version

                    echo "===== NPM ====="
                    npm --version

                    echo "===== UV ====="
                    ${UV_BIN} --version
                '''
            }
        }

        stage('Backend Sync') {
            steps {
                dir('backend') {
                    sh '''
                        set -eux
                        ${UV_BIN} sync --frozen
                        ${UV_BIN} run python --version
                    '''
                }
            }
        }

        stage('Backend Syntax Check') {
            steps {
                dir('backend') {
                    sh '''
                        set -eux

                        ${UV_BIN} run python -m py_compile \
                            main.py \
                            database.py \
                            models.py \
                            routers/users.py
                    '''
                }
            }
        }

        stage('Backend Import Test') {
            steps {
                dir('backend') {
                    sh '''
                        set -eux

                        ${UV_BIN} run python -c \
                          "from main import app; print('FastAPI app import successful')"
                    '''
                }
            }
        }

        stage('Frontend Install') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eux
                        npm ci
                    '''
                }
            }
        }

        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eux
                        npm run lint
                    '''
                }
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eux

                        cat > .env.production <<'EOF'
VITE_API_BASE_URL=
EOF

                        npm run build
                        test -f dist/index.html
                    '''
                }
            }
        }

        stage('Deploy Frontend') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eux

                        sudo /usr/bin/rsync \
                          -a \
                          --delete \
                          dist/ \
                          ${DEPLOY_DIR}/
                    '''
                }
            }
        }

        stage('Publish Backend') {
            steps {
                dir('backend') {
                    sh '''
                        set -eux

                        /usr/bin/rsync \
                          -a \
                          --delete \
                          --exclude '.venv' \
                          ./ \
                          ${BACKEND_DEPLOY_DIR}/

                        cd ${BACKEND_DEPLOY_DIR}
                        ${UV_BIN} sync --frozen
                    '''
                }
            }
        }

        stage('Deploy Backend') {
            steps {
                sh '''
                    set -eux

                    sudo /usr/bin/systemctl restart ${BACKEND_SERVICE}

                    sleep 3

                    sudo /usr/bin/systemctl is-active ${BACKEND_SERVICE}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    set -eux

                    echo "===== BACKEND HEALTH ====="
                    curl --fail --silent --show-error \
                      http://127.0.0.1:8000/health
                    echo

                    echo "===== USERS API THROUGH NGINX ====="
                    curl --fail --silent --show-error \
                      http://127.0.0.1/api/users/
                    echo

                    echo "===== FRONTEND THROUGH NGINX ====="
                    curl --fail --silent --show-error \
                      http://127.0.0.1/ > /dev/null

                    echo "Frontend health check successful"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
            echo 'Application: http://13.235.113.90'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage logs.'
        }

        always {
            echo "Build finished: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}

