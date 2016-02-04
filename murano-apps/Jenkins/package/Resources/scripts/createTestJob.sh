cd ~/jenkins-job-builder

jenkins-jobs test -o output tests/yamlparser/fixtures/templates002.yaml
cat etc/jenkins_jobs.ini
ping -c 5 `grep 'url' etc/jenkins_jobs.ini | awk '{split($0,a,"/"); split(a[3],a,":"); print a[1]}'`
jenkins-jobs --conf etc/jenkins_jobs.ini update tests/yamlparser/fixtures/templates002.yaml
