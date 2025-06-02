pipeline {
    agent any
    environment {
        PYTHONUNBUFFERED = '1'
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'python -m pip install boto3 pillow opencv-python'
            }
        }

        stage('Run Violation Detection') {
            steps {
                sh 'python trafficproj.py <<< "1\ntraffic6.jpg\n"'
            }
        }
    }
}
