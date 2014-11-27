foundedin
=========

Foundedin template, a quick way for people to start their own foundedin initiative, see http://foundedinsouthafrica.com

This a a very basic template for a webapp similar to http://foundedinholland.com

Credit goes to:

http://foundedinholland.com, for the cool idea and wicked frontend code<br>
https://github.com/codrops/MinimalForm, for the super cool sliding single input form, which was inspired by http://www.pagelanes.com/ who is a Foundedx member!<br>
<br>
<br>
This repo is python based using the webapp2 framework, pretty much beginner Google App Engine stuff, although you dont have to know that to use this repo.
<br>
<br>
How to setup a page with this code:<br>
1) Download the google app engine sdk for python - https://cloud.google.com/appengine/downloads (if you're not on a mac you will need to make sure that python 2.7 is on your system - https://www.python.org/download/releases/2.7/)<br>
2) Once google app engine is downloaded, create a new project (probably file --> create a new project)<br>
3) Get a gmail address to use as an admin account for your foundedin page<br>
4) Go to http://cloud.google.com<br>
5) log in with your new gmail<br>
6) Select create a new project (blue button towards the top of the page)<br>
7) Name your project and take note of the unique project id (you can specify your own project id, google will let you know if its not unique), the project id will be your temporary appspot domain, eg. http://your-project-id.appspot.com<br>
8) Go back to your freshly installed google app engine launcher ( the one you downloaded in step 1 ) and create a project with the same name as the project you created in step 6, you will need to specify a folder to save the project, remember where this folder is.<br>
9) Download and unzip the contents of this repo, copy the contents from this repo and paste it into the new project's folder created in step 8, overwrite the existing project.<br>
10) Go into your new folder and open the file app.yaml in a text editor<br>
11) Change the first line of app.yaml to your project id see below:<br>
<br>
<br>
application: your-project-id<br>
version: 1<br>
runtime: python27<br>
api_version: 1<br>
threadsafe: yes<br>
<br>
<br>
12) Save the file, navigate to your app engine sdk and click deploy, you will have to provide your login details from step 3<br>
13) Navigate to your new appspot domain: http://your-project-id.appspot.com/dashboard, you will have to log in using your gmail details from step 3 since this is an admin page<br>
14) Fill out your founded in details... and navigate to your new founded in page: http://your-project-id.appspot.com<br>
<br>
Some things to note:<br>
<br>
You may have some problems deploying your project, where you get the error invalid username/password, this may be for a number of reasons, you can:<br>
1 - go to https://www.google.com/settings/security/lesssecureapps, log in using your new gmail details and set your security to allow less secure apps to access the account<br>
2 - deploy using the command line by navigating to your project directory, typing:<br>
appcfg.py update . --oauth2<br>
you will be redirected to a login page in your browser, where you can login and deployment should go smoothly<br>
<br>
Also:<br>
<br>
The app works best if you have twitter and mandrill integrated<br>
<br>
To get your twitter API tokens go to: https://dev.twitter.com/, login with your foundedin twitter account and create a twitter app, you will have to verify your twitter account on mobile and then activate read & write permissions, once you have done that you can get your access tokens<br>
<br>
For mandrill:<br>
<br>
Signup for mandrill: https://mandrill.com/<br>
Create a mandrill app (straight forward), and get your mandrill key<br>
<br>
<br>
----<br>
<br>
Then to really get the most out of the repo, you can access the template mailer.html in the templates folder and change it accordingly to suit your foundedin style.<br>
<br>
<br>
---------------<br>
<br>
Some of the pages functionality:<br>
<br>
- Founders can upload their own companies as per normal, using pagelane's sweet form<br>
- You can curate and upload new, white logos on the backend<br>
- All data is accessible from the dashboard or through the google cloud console<br>
- you can collect mailers through the early adopter mailing list form<br>
<br>
- If the twitter api is activated, then a tweet will be sent out every time a new company logo is added (eg. New #startup on <bitly link>: <startup name> via <@yourtwitterhandle>)<br>
<br>
- If the mandrill api is activated then you will receive a notification email everytime a startup submits to your page and a confirmation email will be sent to every early adopter that signs up to your mailing list<br>
<br>
- you can access your early adopter emails as well as startup emails on the dashboard... use the emilas for good not evil, we dont want the Foundedx community to be known for spamming.<br>
<br>
<br>
If you use this repo to build your foundedin page you're pretty much set in most respects, hosting will be taken care of, scaling will be pretty much taken care of and if your traffic levels are not huge you'll remain on the free tier, so no hosting fees!!! yay!!! But you may need to add your credit details at some point to remain on the cloud paltform, even though you wont be charges, and of course if you have a large spike in traffic, say for example you land up on product hunt, then you might have to activate a credit card to remain live.<br>
I think you have about 1GB of free storage on GAE, if you upload so many logos that you exceed that amount then you may also ahve to activate billing.
You can read more about the google cloud platform at http://cloud.google.com
<br>
<br>
..........if all this is too much for you look me up on slack and if I have a minute I'll help you out.




