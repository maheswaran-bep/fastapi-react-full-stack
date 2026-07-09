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

        stage('Backend CI') {
            steps {
                dir('backend') {
                    sh '''
                        set -eux

                        echo "===== SYNC DEPENDENCIES ====="
                        ${UV_BIN} sync --frozen

                        echo "===== PYTHON VERSION ====="
                        ${UV_BIN} run python --version

                        echo "===== SYNTAX CHECK ====="
                        ${UV_BIN} run python -m py_compile \
                            main.py \
                            database.py \
                            models.py \
                            routers/users.py

                        echo "===== IMPORT TEST ====="
                        ${UV_BIN} run python -c \
                          "from main import app; print('FastAPI app import successful')"
                    '''
                }
            }
        }

        stage('Frontend CI') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eux

                        echo "===== INSTALL DEPENDENCIES ====="
                        npm ci

                        echo "===== LINT ====="
                        npm run lint

                        echo "===== CREATE PRODUCTION ENV ====="
                        cat > .env.production <<'EOF'
VITE_API_BASE_URL=
EOF

                        echo "===== BUILD ====="
                        npm run build

                        echo "===== VERIFY BUILD ====="
                        test -f dist/index.html
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -eux

                    echo "===== DEPLOY FRONTEND ====="

                    sudo /usr/bin/rsync \
                      -a \
                      --delete \
                      frontend/dist/ \
                      ${DEPLOY_DIR}/

                    echo "===== PUBLISH BACKEND ====="

                    /usr/bin/rsync \
                      -a \
                      --delete \
                      --exclude '.venv' \
                      backend/ \
                      ${BACKEND_DEPLOY_DIR}/

                    echo "===== SYNC PRODUCTION BACKEND ====="

                    cd ${BACKEND_DEPLOY_DIR}
                    ${UV_BIN} sync --frozen

                    echo "===== RESTART BACKEND ====="

                    sudo /usr/bin/systemctl restart \
                      ${BACKEND_SERVICE}

                    sleep 3

                    sudo /usr/bin/systemctl is-active \
                      ${BACKEND_SERVICE}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    set -eux

                    echo "===== BACKEND HEALTH ====="

                    curl --fail \
                      --silent \
                      --show-error \
                      http://127.0.0.1:8000/health

                    echo

                    echo "===== USERS API THROUGH NGINX ====="

                    curl --fail \
                      --silent \
                      --show-error \
                      http://127.0.0.1/api/users/

                    echo

                    echo "===== FRONTEND THROUGH NGINX ====="

                    curl --fail \
                      --silent \
                      --show-error \
                      http://127.0.0.1/ \
                      > /dev/null

                    echo "All health checks successful"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
            echo 'Application deployed successfully through Nginx.'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage logs.'
        }

        always {
            echo "Build finished: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}
