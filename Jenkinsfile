pipeline {
    agent any

    environment {
        BACKEND_DOCKER_IMAGE   = "waterchallenge_backend"
        BACKEND_DOCKER_NAME    = "waterchallenge-backend"

        FRONTEND_DOCKER_IMAGE  = "waterchallenge_web"
        FRONTEND_DOCKER_NAME   = "waterchallenge-web"

        APP_NETWORK   = "waterchallenge-network"
        DOCKER_TAG    = "latest"

        BACKEND_PORT  = "8459"
        FRONTEND_PORT = "8458"

        waterchallenge_ENV   = "/var/lib/jenkins/secret/waterchallenge"
        BACKEND_ENV  = "/var/lib/jenkins/secret/waterchallenge/backend.env"
        FRONTEND_ENV = "/var/lib/jenkins/secret/waterchallenge/frontend.env"

        MEDIA_DIR = "/var/lib/jenkins/app/waterchallenge/media"
    }

    triggers {
        GenericTrigger(
            genericVariables: [
                [key: 'git_branch', value: '$ref'],
                [key: 'git_commit', value: '$after']
            ],
            token: 'xPlcSnKwlm37u6qpUbp5cpK7Vnlt3jpGeBRCmxYEYE2TkaP9Da7lH4nbMYad3gPp0Ak4hzxojg9hSeLCU0du7IIsVLp4M1O2HeQQQyx5KbKTsS0rwlAXm68RsKc5ZtDrkxiv4vmUiaArHhowozAkXblUIP60RKUknMGHGnPWV5AhAHEj949T4byjwJ2BKYiq0PcDyjUXSP9nOQvfj68d6tp2e3wEwtdJTDRiKxTPkGjznDSBoAeutm3zn2e7of6',
            printContributedVariables: true,
            printPostContent: false
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Preflight') {
            steps {
                sh """
                    test -f ${BACKEND_ENV} || (echo "❌ backend.env introuvable: ${BACKEND_ENV}" && exit 1)
                    test -f ${FRONTEND_ENV} || (echo "❌ frontend.env introuvable: ${FRONTEND_ENV}" && exit 1)

                    mkdir -p ${MEDIA_DIR}
                    docker network create ${APP_NETWORK} || true
                """
            }
        }

        stage('Build Backend') {
            when {
                anyOf {
                    branch 'backend'
                    branch 'rebuild'
                }
            }
            steps {
                sh """
                    docker build \
                        -t ${BACKEND_DOCKER_IMAGE}:${DOCKER_TAG} \
                        -f backend/Dockerfile .
                """
            }
        }

        stage('Deploy Backend') {
            when {
                anyOf {
                    branch 'backend'
                    branch 'rebuild'
                }
            }
            steps {
                script {
                    sh "docker network create ${APP_NETWORK} || true"
                    sh "docker stop ${BACKEND_DOCKER_NAME} || true"
                    sh "docker rm ${BACKEND_DOCKER_NAME} || true"

                    def backendCommand = ""

                    if (env.BRANCH_NAME == 'rebuild') {
                        backendCommand = "python manage.py reset_db --noinput && python manage.py makemigrations && python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${BACKEND_PORT} --workers 3 --timeout 120"
                    } else {
                        backendCommand = "python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${BACKEND_PORT} --workers 3 --timeout 120"
                    }

                    sh """
                        docker run -d \
                            --name ${BACKEND_DOCKER_NAME} \
                            --restart unless-stopped \
                            --env-file ${BACKEND_ENV} \
                            --network ${APP_NETWORK} \
                            --add-host=host.docker.internal:host-gateway \
                            -v ${MEDIA_DIR}:/app/media \
                            -p 127.0.0.1:${BACKEND_PORT}:${BACKEND_PORT} \
                            ${BACKEND_DOCKER_IMAGE}:${DOCKER_TAG} \
                            sh -c '${backendCommand}'
                    """

                    sh """
                        sleep 8
                        curl -sf http://127.0.0.1:${BACKEND_PORT}/ || echo "⚠️ Backend lancé, mais / ne retourne pas 200"
                    """
                }
            }
        }

        stage('Build Frontend') {
            when {
                anyOf { branch 'frontend' }
            }
            steps {
                sh """
                    cp ${FRONTEND_ENV} mon-app/.env.production

                    docker build \
                        -t "${FRONTEND_DOCKER_IMAGE}:${DOCKER_TAG}" \
                        -f mon-app/Dockerfile .

                    rm -f mon-app/.env.production
                """
            }
        }

        stage('Deploy Frontend') {
            when {
                anyOf {
                    branch 'frontend'
                }
            }
            steps {
                sh """
                    docker stop ${FRONTEND_DOCKER_NAME} || true
                    docker rm ${FRONTEND_DOCKER_NAME} || true

                    docker run -d \
                        --name ${FRONTEND_DOCKER_NAME} \
                        --restart unless-stopped \
                        --env-file ${FRONTEND_ENV} \
                        --network ${APP_NETWORK} \
                        -p 127.0.0.1:${FRONTEND_PORT}:80 \
                        ${FRONTEND_DOCKER_IMAGE}:${DOCKER_TAG}
                """

                sh """
                    sleep 5
                    curl -sf http://127.0.0.1:${FRONTEND_PORT}/ || echo "⚠️ Frontend pas encore prêt"
                """
            }
        }
    }

    post {
        success {
            echo "✅ [${env.BRANCH_NAME}] Pipeline terminé avec succès."
        }

        failure {
            echo "❌ [${env.BRANCH_NAME}] Pipeline échoué."
        }
    }
}