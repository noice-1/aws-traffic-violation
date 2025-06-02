pipeline {
    agent{
        docker{
            image 'python:3.10'
        }
    }
    environment {
        PYTHONUNBUFFERED = '1'
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install boto3 pillow opencv-python'
                '''
            }
        }

        stage('Run Violation Detection') {
            steps {
                sh 'python trafficproj.py <<< "1\ntraffic6.jpg\n"'
            }
        }
    }
}
