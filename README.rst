===============
Using CI/CD App
===============

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

For manually uploading the packages to Murano, user need to upload them
in special order, otherwise it may lead to automatic loading their dependencies
from App Catalog, which has probably the different versions of these packages.

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

For the CI/CD application in this repo specify the following parameters:
 1.First panel:
   - Root Username
   - Root Password
   - Root User Email
   - Username
   - Password
   - Email

This is user credentials - for admin and common user.
If you have you own .gitconfig file on desktop, you can change user credentials
or use default settings.

 2.Second panel:
   - Instance flavor
   - Instance image
   - Key Pair
   - Availability zone
   - Instance Naming Pattern

For successful deployment of murano app, user need to download special image
with pre-installed murano-agent. If you want to create your own image, then
follow the instruction:
http://docs.openstack.org/developer/murano/image_builders/linux.html

Then deploy your application in environment.

3. Find links on the deployed services
--------------------------------------

When application is finally deployed, go to **Environments** panel, choose
the newly deployed environment and open the **Latest Deployment Log** tab.
Scroll down and click on Jenkins, Gerrit URLs.

Known issue:

Need to add mapping hostname to your local desktop to have access to Gerrit Web
form. Also the same issue exists for Jenkins, so repeat it for Jenkins VM too.

How to fix:

Execute command: *sudo echo "<ip_address> <hostname> >> /etc/hosts* on your
local desktop and on Jenkins VM (via ssh). Where:

 - <ip_address> is IP of Gerrit VM, which is available at
   **Latest Deployment Log** tab. (it's a hyperlink like http://xx.xx.xx.xx:80)
 - <hostname> is a hostname displayed in web browser URL after click
   on the link at **Latest Deployment Log** tab. (as above, it's
   http://xx.xx.xx.xx:80).

4. Add new project
------------------

- Log in to Gerrit with login/password provided via UI on step 2 (they are
  also can be found at the **Latest Deployment Log** tab). Go to user’s
  **Settings** -> **SSH Public Keys**. Add your public ssh key.

- Open **Projects** -> **List**. Choose open-paas/project-config.
  Clone project via SSH. For example:
  *git clone ssh://<username_from_step_2>@hostname:29418/open-paas/project-config*

- Add new project to Gerrit config, like it works for Openstack Infra.
  Open gerrit/projects.yaml in project-config repo from previous step and add
  something like::

    - project: demo/petclinic
      description: petclinic description
      upstream: https://github.com/sn00p/spring-petclinic
      acl-config: /home/gerrit2/acls/open-paas/project-config.config

  Ideally ACL file should be different, but for simple example we can use
  the existing one.

- Set correct options as default from step 2 for your ~/.gitconfig on desktop
  by adding the following lines::

   [user]
   email = user@mail.com
   name = user

  Skip this step if you have your own ~/.gitconfig and you already specified
  correct name and mail on step 2.

- Commit changes and push to review::

   git add .
   git commit -am "Add Petclinic Project"
   git review -r origin master

- When change is uploaded to Gerrit, re-login with root user credentials.
  Open proposed patch, set Code-Review +2 and click **Submit**.

- Wait a while until your changes are being merged into the repository (it may
  take from 1 to 5 minutes). Re-login with user’s credentials and open
  **Projects** -> **List** again. New project should be in the project list
  now.

5. Configure and run Jenkins job for your project
-------------------------------------------------

Known issue:
We already have template for Maven job, but it is not applied by default.

How to fix:
To apply this job template you need to connect to Jenkins VM via ssh. Login
as **root** and execute command:
**jenkins-jobs update /etc/project-config/jenkins/jobs**

- Go to Jenkins UI form, open created job and configure it. Set
  **Source Code management** to *Git* .Set **Repository url** as it's displayed
  in Gerrit. For example:
  **ssh://<username>@<gerrit_hostname>:29418/demo/petclinic**

  Use **jenkins** user in link above instead of **<username>**.

- If you work with the demo/petclinic test project as it demostrated on
  previous steps, then you need an additional configuration here:
  Set **Branch** to *Spring-Security*, for current project.
  In section **Build** in field **Goals and Options** write: *tomcat7:deploy*

- Run Job and make sure that it is deployed in tomcat server.
  Currently it's hardcoded inside of the mentioned repository of custom
  petclinic project. For normal work you need to update **pom.xml** file to
  reference on correct IP address with Tomcat server. When it's ready, open URL
  with your project. For example:
  **http://<ip_of_tomcat_server>:8080/petclinic**

6. Update project and re-run Jenkins job
----------------------------------------

- Clone petclinic project. For example:
  **git clone ssh://<username>@<gerrit_hostname>:29418/demo/petclinic**

- Change branch in repo to **Spring-Security**::

   git checkout Spring-Security

- Change the following file in this repository:
  **src/main/webapp/WEB-INF/jsp/welcome.jsp**. For example,replace word
  **Welcome** with **Hi there!**. Commit and push on review::

   git add .
   git commit -am "Patch with changes"
   git review -r origin Spring-Security

- Re-login with root credentials and merge this patch.
- Re-run job in Jenkins. And re-check Tomcat server again.


Demonstration video
===================

Demo CI/CD Murano application - https://www.youtube.com/watch?v=waTqsHfnVSo
Demo CI/CD Murano application (with Zuul & Nodepool) - https://www.youtube.com/watch?v=p8ce-j2-a1M
