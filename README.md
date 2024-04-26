<p align="center"><img src="https://github.com/GeovanaSLima/TransQuality/blob/main/project/static/images/logo/PNG/Group-42.png?raw=true" width=80%></p>

</br>

## Project description

The objective of this project is to develop a web application for leeping records of bus maintanance procedures based on a questionnaire created by the company. The answers are saved on the database relating the form id to the user that answered the questionnaire. Later on the user can access the questionnaire and create PDF files with the answers and images.

### Demonstration

[transquality_demo.webm](https://github.com/GeovanaSLima/TransQuality/assets/66534549/1d9616d4-3921-400e-b6ca-b65df213e4a6)

</br>
</br>

## 🏭 Database

For this project, we're using MongoDB to create our database and hold the project's data. To connect the project and the database, we're using FastAPI for developing the routes and main HTTP request/responses functions.

</br>
</br>

## 🚀 Features

- [x] MongoDB Database Integration
- [x] User Authentication
- [x] User creation/deletion
- [x] Creation of Forms
- [x] Access and Edit old forms
- [x] Creation of PDF from forms answers
- [x] Route's Unit Tests 

</br>
</br>

## 🔨 Installation and Configuration

Before starting, you'll need to have installed the following tools:
* [Python](https://www.python.org/)

```bash

## Create the Virtual Env 
$ python -m venv .venv       

## Activating the virtual env (Windows)
$ .venv/Scripts/activate    

## Activating the virtual env (Ubuntu/MacOS)
$ source .venv/bin/activate

## Install project requirements
$ pip install -r requirements.txt      
```

<br>
<br>

## 💻 Running locally

To run the project locally and debug run:

```bash
## On the project folder
$ cd project
$ uvicorn main:app

## Expected result
INFO:     Started server process [83554]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</br>
</br>

## ✒️ Author

<a href="https://learningdata.dev/sobre">  
 <img src="https://raw.githubusercontent.com/GeovanaSLima/GeovanaSLima/main/GitProfile.png" alt="Geovana Sousa"/>
  <p><b>Geovana Sousa 🚀</b></p></a>
<p><i>A passionate Developer ❤️</i></br>
   Get in touch! 👋🏽</p>


[![LearningData Badge](https://img.shields.io/badge/-LearningData-%23FC5C65?style=&logo=ghost)](https://learningdata.dev)
[![Portfolio Badge](https://img.shields.io/badge/-Portfolio-%238390A2?style=&logo=adobe)](https://geovanasousa.com)
[![Linkedin Badge](https://img.shields.io/badge/-Geovana-blue?style=&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/geovana--sousa/)](https://www.linkedin.com/in/geovana--sousa/) 
[![Gmail Badge](https://img.shields.io/badge/-geovanasslima-c14438?style=&logo=Gmail&logoColor=white&link=mailto:geovanasslima@gmail.com)](mailto:geovanasslima@gmail.com)
