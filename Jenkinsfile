def image = "hyp3-rtc-gamma"
def registry = "docker-registry.asf.alaska.edu:5000"

pipeline {
    agent { node { label "docker" } }
    stages {
	stage("build") {
	    steps {
		// get some code into the Docker build environment
		dir("${WORKSPACE}/cloud-proj") {
		    git branch: 'proc-prod', credentialsId: 'fdc7a89b-13b0-4a73-9c40-76faf87eb607', url: 'git@github.com:asfadmin/cloud-proj.git'
		}
		dir("${WORKSPACE}/hyp3-lib") {
		    git branch: 'prod', credentialsId: 'fdc7a89b-13b0-4a73-9c40-76faf87eb607', url: 'git@github.com:asfadmin/hyp3-lib.git'
		}
		dir("${WORKSPACE}/hyp3-rtc-gamma") {
		    git branch: 'prod', credentialsId: 'fdc7a89b-13b0-4a73-9c40-76faf87eb607', url: 'git@github.com:asfadmin/hyp3-rtc-gamma.git'
		}

		// pull in the GAMMA tarball
		sh "cp /asfn/third-party/gamma/gamma_20170707.tar.gz ."

		// build
		sh "docker build -t ${registry}/${image}:latest -t ${registry}/${image}:build.${BUILD_NUMBER} --squash -f Dockerfile ."
		sh "docker push ${registry}/${image}:latest"
		sh "docker push ${registry}/${image}:build.${BUILD_NUMBER}"
	    }
	}
    }
}
