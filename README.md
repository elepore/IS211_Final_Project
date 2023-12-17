# IS211 Final Project

## Overview

This project is a web-based application designed for managing a database of books. It facilitates user interaction with a `books.db` database through a friendly interface, built using Python and a web framework.

## Features

- **Book Management:** Core functionality for adding, viewing, updating, or deleting book records.
- **User Interface:** Web-based interface for seamless user interactions.
- **Search Functionality:** Enables searching for books in database.

## How It Works

### Application Entry Point: `app.py`

- Main script of the application.
- Initializes the web server.
- Handles routing of HTTP requests.

### Database Setup: `database_setup.py`

- Sets up the database.
- Includes code for creating tables and defining schemas.
- Initializes the database with default data.

### Database: `books.db`

- SQLite database storing all book-related data.
- Accessed and modified by the application for various operations.

### Templates Directory

- Contains HTML templates for the web pages.
- Defines the structure and layout of user interfaces.

## Installation and Setup

1. Ensure Python is installed on your system.
2. Install required dependencies (if any).
3. Run `database_setup.py` to initialize the database.
4. Start the application by running `app.py`.

## Usage

Navigate to the application's URL in a web browser after starting the application.
