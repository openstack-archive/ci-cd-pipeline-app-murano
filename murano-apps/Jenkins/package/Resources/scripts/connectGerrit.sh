#!/bin/bash
GERRIT_IP="$1"
DOMAIN="$2"

cat << CONFIG >> /var/lib/jenkins/credentials.xml
<?xml version='1.0' encoding='UTF-8'?>
<com.cloudbees.plugins.credentials.SystemCredentialsProvider plugin="credentials@1.18">
  <domainCredentialsMap class="hudson.util.CopyOnWriteMap\$Hash">
      <entry>
      <com.cloudbees.plugins.credentials.domains.Domain>
        <specifications/>
      </com.cloudbees.plugins.credentials.domains.Domain>
      <java.util.concurrent.CopyOnWriteArrayList>
        <com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@1.10">
          <scope>GLOBAL</scope>
          <id>10055155-5c33-4318-8161-96a3ccd270a8</id>
          <description></description>
          <username>jenkins</username>
          <passphrase>aE53R1jYUuH1K2BgkbGqfw==</passphrase>
          <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey\$FileOnMasterPrivateKeySource">
            <privateKeyFile>/var/lib/jenkins/.ssh/jenkins-id_rsa</privateKeyFile>
          </privateKeySource>
        </com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
      </java.util.concurrent.CopyOnWriteArrayList>
    </entry>
  </domainCredentialsMap>
</com.cloudbees.plugins.credentials.SystemCredentialsProvider>
CONFIG

cat << CONFIG >> /var/lib/jenkins/gerrit-trigger.xml 
<?xml version='1.0' encoding='UTF-8'?>
<com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl plugin="gerrit-trigger@2.12.0">
  <servers class="java.util.concurrent.CopyOnWriteArrayList">
    <com.sonyericsson.hudson.plugins.gerrit.trigger.GerritServer>
      <name>Gerrit</name>
      <noConnectionOnStartup>false</noConnectionOnStartup>
      <config class="com.sonyericsson.hudson.plugins.gerrit.trigger.config.Config">
        <gerritHostName>${GERRIT_IP}</gerritHostName>
        <gerritSshPort>29418</gerritSshPort>
        <gerritProxy></gerritProxy>
        <gerritUserName>jenkins</gerritUserName>
        <gerritEMail>jenkins@${DOMAIN}</gerritEMail>
        <gerritAuthKeyFile>/var/lib/jenkins/.ssh/jenkins-id_rsa</gerritAuthKeyFile>
        <gerritAuthKeyFilePassword>aE53R1jYUuH1K2BgkbGqfw==</gerritAuthKeyFilePassword>
        <useRestApi>false</useRestApi>
        <restCodeReview>false</restCodeReview>
        <restVerified>false</restVerified>
        <gerritBuildCurrentPatchesOnly>false</gerritBuildCurrentPatchesOnly>
        <gerritVerifiedCmdBuildSuccessful>gerrit review &lt;CHANGE&gt;,&lt;PATCHSET&gt; --message &apos;Build Successful &lt;BUILDS_STATS&gt;&apos; --verified &lt;VERIFIED&gt; --code-review &lt;CODE_REVIEW&gt;</gerritVerifiedCmdBuildSuccessful>
        <gerritVerifiedCmdBuildUnstable>gerrit review &lt;CHANGE&gt;,&lt;PATCHSET&gt; --message &apos;Build Unstable &lt;BUILDS_STATS&gt;&apos; --verified &lt;VERIFIED&gt; --code-review &lt;CODE_REVIEW&gt;</gerritVerifiedCmdBuildUnstable>
        <gerritVerifiedCmdBuildFailed>gerrit review &lt;CHANGE&gt;,&lt;PATCHSET&gt; --message &apos;Build Failed &lt;BUILDS_STATS&gt;&apos; --verified &lt;VERIFIED&gt; --code-review &lt;CODE_REVIEW&gt;</gerritVerifiedCmdBuildFailed>
        <gerritVerifiedCmdBuildStarted>gerrit review &lt;CHANGE&gt;,&lt;PATCHSET&gt; --message &apos;Build Started &lt;BUILDURL&gt; &lt;STARTED_STATS&gt;&apos; --verified &lt;VERIFIED&gt; --code-review &lt;CODE_REVIEW&gt;</gerritVerifiedCmdBuildStarted>
        <gerritVerifiedCmdBuildNotBuilt>gerrit review &lt;CHANGE&gt;,&lt;PATCHSET&gt; --message &apos;No Builds Executed &lt;BUILDS_STATS&gt;&apos; --verified &lt;VERIFIED&gt; --code-review &lt;CODE_REVIEW&gt;</gerritVerifiedCmdBuildNotBuilt>
        <gerritFrontEndUrl>http://${GERRIT_IP}:8080/</gerritFrontEndUrl>
        <gerritBuildStartedVerifiedValue>0</gerritBuildStartedVerifiedValue>
        <gerritBuildStartedCodeReviewValue>0</gerritBuildStartedCodeReviewValue>
        <gerritBuildSuccessfulVerifiedValue>1</gerritBuildSuccessfulVerifiedValue>
        <gerritBuildSuccessfulCodeReviewValue>0</gerritBuildSuccessfulCodeReviewValue>
        <gerritBuildFailedVerifiedValue>-1</gerritBuildFailedVerifiedValue>
        <gerritBuildFailedCodeReviewValue>0</gerritBuildFailedCodeReviewValue>
        <gerritBuildUnstableVerifiedValue>0</gerritBuildUnstableVerifiedValue>
        <gerritBuildUnstableCodeReviewValue>-1</gerritBuildUnstableCodeReviewValue>
        <gerritBuildNotBuiltVerifiedValue>0</gerritBuildNotBuiltVerifiedValue>
        <gerritBuildNotBuiltCodeReviewValue>0</gerritBuildNotBuiltCodeReviewValue>
        <enableManualTrigger>true</enableManualTrigger>
        <enablePluginMessages>true</enablePluginMessages>
        <buildScheduleDelay>3</buildScheduleDelay>
        <dynamicConfigRefreshInterval>30</dynamicConfigRefreshInterval>
        <categories class="linked-list">
          <com.sonyericsson.hudson.plugins.gerrit.trigger.VerdictCategory>
            <verdictValue>Code-Review</verdictValue>
            <verdictDescription>Code Review</verdictDescription>
          </com.sonyericsson.hudson.plugins.gerrit.trigger.VerdictCategory>
          <com.sonyericsson.hudson.plugins.gerrit.trigger.VerdictCategory>
            <verdictValue>Verified</verdictValue>
            <verdictDescription>Verified</verdictDescription>
          </com.sonyericsson.hudson.plugins.gerrit.trigger.VerdictCategory>
        </categories>
        <replicationConfig>
          <enableReplication>false</enableReplication>
          <slaves class="linked-list"/>
          <enableSlaveSelectionInJobs>false</enableSlaveSelectionInJobs>
        </replicationConfig>
        <watchdogTimeoutMinutes>0</watchdogTimeoutMinutes>
        <watchTimeExceptionData>
          <daysOfWeek/>
          <timesOfDay class="linked-list"/>
        </watchTimeExceptionData>
        <notificationLevel>ALL</notificationLevel>
      </config>
    </com.sonyericsson.hudson.plugins.gerrit.trigger.GerritServer>
  </servers>
  <pluginConfig>
    <numberOfReceivingWorkerThreads>3</numberOfReceivingWorkerThreads>
    <numberOfSendingWorkerThreads>1</numberOfSendingWorkerThreads>
    <replicationCacheExpirationInMinutes>360</replicationCacheExpirationInMinutes>
  </pluginConfig>
</com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl>
CONFIG

cat << CONFIG >> /var/lib/jenkins/hudson.plugins.git.GitTool.xml 
<?xml version='1.0' encoding='UTF-8'?>
<hudson.plugins.git.GitTool_-DescriptorImpl plugin="git-client@1.16.1">
  <installations class="hudson.plugins.git.GitTool-array">
    <hudson.plugins.git.GitTool>
      <name>Default</name>
      <home>git</home>
      <properties/>
    </hudson.plugins.git.GitTool>
  </installations>
</hudson.plugins.git.GitTool_-DescriptorImpl>
CONFIG

# Restart jenkins
service jenkins restart

# Grab jenkins key from gerrit
