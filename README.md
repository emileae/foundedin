foundedin
=========

Foundedin template, a quick way for people to start their own foundedin initiative, see http://foundedinsouthafrica.com

This a a very basic template for a webapp similar to http://foundedinholland.com

Credit goes to:

http://foundedinholland.com, for the cool idea and wicked frontend code
https://github.com/codrops/MinimalForm, for the super cool sliding single input form

This project is almost ready to be pasted into a google app engine project and deployed, the app.yaml should be adapted to take your project id into account, a mandrill key should be inserted in the utils.py file, so that early adopters can receive their mail, and then the necessary scripts for google analytics, twitter and facebook should be included in the index.html file.

We've kept the scripts in the various html files, but these should be put in their own folder and minified in production.

Artwork specific to foundedinsouthafrica should be replaced, our artwork was greatly influenced by foundedinholland.com and was put together by Johann (https://www.behance.net/JohannduBruyn)

================

What this does...
- Sets up a basic DB consisting of startups and early adopters
- Each time a startup completes the form they are saved and await approval
- Access the url /admin to see a list of startups, you will need to download their logo image, process it (change colour/size or whatever) and then upload the image to the DB, google is very generous and provides 5GB(I think) free space for the blobstore.
- Once an image is uploaded the startup is 'approved' and will appear on the front page
- You can also delete startup submissions by clicking the delete button, this will remove a startup from the DB
- We also included an early adopter form at the bottom of the page, this collects emails and promises to send them product offerings/ opportunities related to the startups... early adoption... use it for good and not evil, we dont want the foundedin initiative to be thought of as a spamming scheme
- Some logic is included for unsubscribing from the mailing list


