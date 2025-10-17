# Air Quality Data: Automated Publication Script
This workflow is designed to automatically pull data on a daily schedule from the [World Air Quality Index Project](https://waqi.info/) and create a summary JSON and HTML file. These files are then automatically copied to the production branch and deployed to github pages where they can be easily accessed. This deployment then automatically triggers a date based release.
---
## Relavent files in order of deployment..
1. daily-air-quality.yml
    - This script is scheduled to trigger at midnight (UTC). It takes the raw data directly from the World Air Quality Index Project for london on that day and populates templates/daily-air-quality-template.html and a json file with the relevant data. This workflow utilises /scripts/create-daily-air-quality-html.py which handles the data processing and file creation. The new JSON and html files are then saved to the 'content' folder on the main branch.
2. generate-and-deploy.yml
    - This script is scheduled to trigger on completion of daily-air-quality.yml. It creates the production branch and populates it with the required files. It then copies the content folder from main which includes the newly generated html and json files.
3. deploy.yml
    - This scipt is scheduled to trigger on completion of generate-and-deploy.yml. It configures the github pages environment and uploads the new html file as an artifact making it available to view as a webpage.
4. release.yml
    - This script is scheduled to trigger on completion of deploy.yml. This creates a date based version tag (ideal for daily deployments) and tags the deployment as a new release, uploading the new data as release assets.

