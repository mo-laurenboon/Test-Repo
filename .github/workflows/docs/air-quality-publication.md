# Air Quality Data: Automated Publication Script
This workflow is designed to automatically pull data on a daily schedule from the [World Air Quality Index Project](https://waqi.info/) and create a summary JSON and HTML file. These files are then automatically copied to the production branch and deployed to github pages where they can be easily accessed. This deployment then automatically triggers a date based release.
---
## Relavent files in order of deployment..
1. daily-air-quality.yml
2. generate-and-deploy.yml
3. deploy.yml
4. release.yml

