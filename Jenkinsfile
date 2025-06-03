pipeline {
    agent{
        docker{
            image 'python:3.10'
        }
    }
    environment {
        PYTHONUNBUFFERED = '1'
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    apt-get update && apt-get install -y libgl1
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install boto3 pillow opencv-python-headless
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
