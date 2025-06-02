pipeline {
    agent any

    environment {
        PYTHONIOENCODING = 'utf-8'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/noice-1/AWS-traffic-violation.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Violation Detection') {
            steps {
                sh 'python trafficproj.py <<< "1\ntraffic6.jpg\n"'
            }
        }
    }
}
