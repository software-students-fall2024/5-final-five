![CI/CD](https://github.com/software-students-fall2024/5-final-five/actions/workflows/web-app.yml/badge.svg)
![CI/CD](https://github.com/software-students-fall2024/5-final-five/actions/workflows/deploy.yml/badge.svg)

# **📄 resume.ly**

## Description

Our Resume Builder is a streamlined webapp that allows users to easily build a formatted resume. It also stores users' generated resumes to be accessed at will.

## Docker Image

You can access the Docker image for **resume.ly** on Docker Hub:

[**resume.ly Docker Image**](https://hub.docker.com/r/fav2019/flask-app)

## Try it out yourself
[Live Link](https://resume-builder-wwcqm.ondigitalocean.app/) 

## Run the App

### Environment Setup

Before running the app, ensure your `.env` file in the `web_app` directory contains the following MongoDB URI configuration:

```
MONGO_URI=mongodb://mongodb:27017/
```

Start by building:

```
docker-compose up --build
```

If you've already built previously, you may compose the containers like so:

```
docker-compose up
```

Once that is completed, you can access the site [HERE](http://localhost:5002/)



## Team Members

[Shray Awasti](https://github.com/shrayawasti)

[Safia Billah](https://github.com/safiabillah)

[Fatima Villena](https://github.com/favils)

[Melanie Zhang](https://github.com/melanie-y-zhang)

## Test Coverage

<img src="coverage.png" alt="coverage" width="300"/>
