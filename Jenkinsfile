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
                    apt-get update && apt-get install -y libgl1
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install boto3 pillow opencv-python
                '''
            }
        }

        stage('Run Violation Detection') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo -e "1\ntraffic6.jpg" | python trafficproj.py
                '''
            }
        }
    }
}
