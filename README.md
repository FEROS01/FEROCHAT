# Ferochat Messenger App

- <img src="static/messenger/images/ferochat_logo3.png" width="200" height="200">
- <img src="static/messenger/images/ferochat1.png" height="60">

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
<a name="introduction"></a>
Welcome to the FEROCHAT Messenger App! This is a Django-based messaging application that allows users to send text, images, audio, videos, and various other types of files. It is designed to facilitate communication between individuals, helping them make friends, create chat groups, and stay connected.
#### It should be noted that this project is still a work in progress and contributions are welcomed. Check [Contibuting](#contributing) for more infos :)

## Features
<a name="features"></a>
### 1. User Registration and Authentication

- Users can create accounts securely and log in.
- Passwords are hashed and stored securely.
- Users can reset passwords when forgotten using the "forgot password" link in the login page

### 2. User Profile Management

- Users can set up and update their profiles with profile pictures and personal information.

### 3. Friends Management

- Users can send and accept friend requests.
- A user's friend list is displayed in the app.
- Users can remove friends from their friend list.

### 4. Chat Groups

- Users can create chat groups and invite friends to join.
- Group admins can manage group settings, such as group name and profile picture.
- Group members can send messages to the group.
- Group members can exit group

### 5. Real-time Messaging

- Instantly send text messages, images, audio, videos, and files.
- Messages are displayed in real-time, ensuring a seamless conversation experience.

### 6. Multimedia Sharing

- Share images, videos, audio clips, and files within chats.
- Preview images and videos directly in the chat interface.

### 7. Message Search

- Users can search for specific messages within a chat or group conversation.

### 8. Notifications

- Receive push notifications for new messages and friend requests.
- Notifications keep users informed of important events.

### 9. Privacy and Security

- Messages and user data are encrypted to protect user privacy.

## Installation
<a name="installation"></a>

To run the FEROCHAT Messenger App locally, follow these steps in your console:

1. Clone this repository:

   ```bash
   git clone https://github.com/FEROS01/FEROCHAT.git
   ```

2. Install python's venv module

   ```bash
   pip install virtualenv
   ```

3. Enter the Messenger folder

   ```bash
   cd Messenger
   ```

4. Create a folder named 'media':

      ```bash
      mkdir media
      ```

5. Create a `.env` file and configure your environment variables (e.g., database settings, secret key).
   ```bash
   #In the .env file
   SECRET_KEY = "yourSecretKey"
   EMAIL_USER = "yourEmailAddress"
   EMAIL_PASSWORD = 'yourEmailPassword'
   ```
   Checkout this [link](https://dev.to/earthcomfy/django-reset-password-3k0l#set-up-sending-email-in-django) to learn how to setup your django email

6. Create a virtual environment (recommended) and activate it:

   ```bash
   #on mac
   python -m venv venv
   source venv/bin/activate
   
   #on windows
   python -m venv venv
   venv/Scripts/activate
   ```

7. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
8. Navigate to this file `venv/Lib/site-packages/magic/__init__.py` and replace its content with this

   ```py
   from .magic import *
   __version__ = '0.4.14'
   ```

8. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

9. Create a User object for the FeroChat app:

   ```bash
   python manage.py createsuperuser --username 'FeroChat' --email 'dummyEmailAddress'

   # You will be required to give a password
   ```

10. Create a User account for yourself:

      ```bash
      python manage.py createsuperuser
      # follow the prompts
      ```


11. Start the development server:

      ```bash
      python manage.py runserver
      ```

12. Access the application in your web browser at `http://localhost:8000`.

## Usage
<a name="usage"></a>

1. Register for an account or log in using your username .
2. Add friends by searching for their usernames and sending friend requests.
3. Create chat groups and invite friends to join.
4. Start conversations by clicking on a friend's name or a chat group.
5. Send messages, images, audio, videos, and files by clicking the respective icons in the chat input box.
6. Enjoy real-time communication and stay connected with your friends!

## Contributing
<a name="contributing"></a>

We welcome contributions to the FEROCHAT Messenger App. To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix. (Please only fix one issue per pull request)
3. Make your changes and commit them with descriptive messages.
4. Push your branch to your fork.
5. Create a pull request to merge your changes into the main repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Thank you for using the FEROCHAT Messenger App. I hope you enjoyed the experience and found it useful in one way or another. If you have any questions or encounter any issues, please don't hesitate to contact me on [twitter](https://twitter.com/oluwaferos) or on [Linkedin](https://www.linkedin.com/in/oluwaferanmi-ope-20a091232/).