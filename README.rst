============================
How to start using CI/CD App
============================

This is a step by step guide how to use CI/CD application.

1. Download Murano Packages/Applications
----------------------------------------

For users
+++++++++

All Applications are available in App Catalog.
The main one is:
http://apps.openstack.org/#tab=murano-apps&asset=CiCdEnvironment

For Developers
++++++++++++++

If packages will be loaded manually via Murano UI, user should do it
in special order - otherwise packages in dependencies will be automatically
loaded from App Catalog and will be different!

For development purposes special script can be used:
https://github.com/openstack/ci-cd-pipeline-app-murano/blob/master/tools/prepare_packages.sh

The right order of manual load packages via Murano UI is
(same order is used in  script mentioned above):
- Puppet
- SystemConfig
- OpenLDAP
- Gerrit
- Jenkins
- Zuul
- NodePool
- CICDEnvironment

2. Install CI/CD Application via Murano UI
------------------------------------------

For more information how to use Murano is available here:
http://murano.readthedocs.io/en/latest/draft/enduser-guide/quickstart.html

For the CI/CD application in this repo specify follow paramaters:
* First panel:
 - Root Username
 - Root Password
 - Root User Email
 - Username
 - Password
 - Email

This is user credentials - for admin and common user.
If you have you own .gitconfig file on desktop, you can change user credentials
or use default settings.

* Second panel:
 - Instance flavor
 - Instance image
 - Key Pair
 - Availability zone
 - Instance Naming Pattern

For successful deployment of murano app, user need to download special image
with pre-installed murano-agent. If you want create your own image, then follow
instruction: http://docs.openstack.org/developer/murano/image_builders/linux.html

Then deploy your application in environment.

3. Find links on the deployed services
--------------------------------------

When application is finally deployed, go to “Environments” panel, choose
deployed environment and open “Latest Deployment Log” tab.
Scroll down and click on Jenkins, Gerrit URLs.

Known issue:
Need to add mapping hostname to your local desktop to have access to Gerrit Web
form. Also the same issue exists for Jenkins, so repeat it for Jenkins VM too.

How to fix:
Execute command: *sudo echo "<ip_address> <hostname> >> /etc/hosts* on your
local desktop and on Jenkins VM (via ssh). Where:
- <ip_address> is IP of Geriit VM, which is available on
**Latest Deployment Log** tab. (it's hyperlink like http://xx.xx.xx.xx:80)
- <hostname> is a hostname displayed in web browser URL after click on link on
**Latest Deployment Log** tab. (as above, it's http://xx.xx.xx.xx:80).

4. Add new project
------------------

- Log in Gerrit with login/password from provided via UI on step 2 (they are
  also can be found on **Latest Deployment Log** tab). Go to user’s
  **Settings** and **SSH Public Keys**. Add your public ssh key.

- Open **Projects** -> **List**. Choose open-paas/project-config.
  Clone project via SSH. For example:
*git clone ssh://<username_from_step_2>@hostname:29418/open-paas/project-config*

- Add new project to Gerrit config, like it work for Openstack Infra.
  Open gerrit/projects.yaml in project-config repo from previous step and add
   something like::
    - project: demo/petclinic
      description: petclinic description
      upstream: https://github.com/sn00p/spring-petclinic
      acl-config: /home/gerrit2/acls/open-paas/project-config.config

   Ideally ACL file should be different, but for simple example we can use
   existing.

- Set correct options as default srop step 2 for your ~/.gitconfig on desktop
  by adding follow lines::
    [user]
    email = user@mail.com
    name = user

  Skip this step if you have your own ~/.gitconfig and you already specified
  correct name and mail on step 2.

- Commit changes and push to review::
    git add .
    git commit -am "Add Petclinic Project"
    git review -r origin master

- When change will be uploaded to gerrit, re-login with root user credentials.
  Open proposed patch and +2,  Merge and Submit it.

- Wait some time to apply your changes to repository (it may take from 1 to 5
  minutes). Re-login with user’s credentials and open **Projects** -> **List**
  again. New project should be presented now in this list.

5. Configure and run Jenkins job for your project
-------------------------------------------------

Known issue:
We already have template for Maven job, but it did not applied by default.

How to fix:
To use it connect to Jenkins VM via ssh. Login as **root** and execute command:

**jenkins-jobs update /etc/project-config/jenkins/jobs**

- Go to Jenkims UI from, open created job and set follow configuration settings
  in it. Set **Source Code management** to *Git* .Set **Repository url** as
  it's displayed in Gerrit. For example:

**ssh://<username>@<gerrit_hostname>:29418/demo/petclinic**

  In this link replace your *username* on *jenkins*.

- Set **Branch** to *Spring-Security*, for current project.
  In section **Build** in field **Goals and Options** write: *tomcat7:deploy*

- Run Job and make sure, that it will be deployed in tomcat server.
  Currently it's hardcoded in mentioned repository of custom petclinic project.
  For normal work you need to update *pom* file to reference on correct IP
  address with Tomcat server.
  When it's ready open URL with your project. For example:

**http://<ip_of_tomcat_server>:8080/petclinic**

6. Update project and re-run Jenkins job
----------------------------------------

- Clone petclinic project. For example:
**git clone ssh://<username>@<gerrit_hostname>:29418/demo/petclinic**

- Change branch in repo to **Spring-Security**::
    git checkout Spring-Security

- Change in this repository file: **src/main/webapp/WEB-INF/jsp/welcome.jsp**
  For example replace word **Welcome** on **Hi there!**.
  Commit And push on review::
    git add .
    git commit -am "Patch with changes"
    git review -r origin Spring-Security

- Re-login with root credentials and merge this patch.
- Re-run job in Jenkins. And re-check Tomcat server again.
