# Appoint
Appointment scheduling system with JWT authentication and role-based access (Scheduler &amp; Booker) using Django REST Framework

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)

---

## Introduction

This project is a scheduling system written using Django and DRF that allows for registration, login, one-time password (OTP) verification, and receiving appointments from the scheduler.

---

## Features

- Register with phone number and send OTP
- Login with phone number and OTP
- Confirm OTP and receive JWT token
- Test registration and login and OTP

---

## Installation

First, make sure Python and pip are installed.


git clone https://github.com/OU-G-L/Appoint.git

cd project-folder

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

---

## Usage

Run the development server:
python manage.py migrate

Access the API:
http://localhost:8000/swagger/

---

## Running Tests

To run the automated test suite, use the following command:
python manage.py test
