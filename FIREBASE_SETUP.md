# Firebase Setup Guide

This guide explains the steps required to set up Firebase for the Prompt Management Application.

## 1. Firebase Project Initialization
- **Action**: Create a project in the [Firebase Console](https://console.firebase.google.com/).
- **Purpose**: This creates a centralized storage and authentication hub for your application across Google's infrastructure.

## 2. Enable Authentication
- **Action**: Go to **Authentication** > **Sign-in method** > **Email/Password** and click **Enable**.
- **Purpose**: By default, Firebase has all sign-in methods disabled. Since our app uses email/password for signup/login, this must be explicitly turned on to avoid `CONFIGURATION_NOT_FOUND` errors.

## 3. Backend Setup (Admin SDK)
The backend needs "Admin" level access to verify that the tokens sent by the frontend are authentic.

- **Action**:
    1. Go to **Project Settings** (gear icon) > **Service accounts**.
    2. Click **Generate new private key**.
    3. Save the JSON file in the `backend/` folder.
- **Project Specific File**: You have saved this as `prompt-pro-3df27-firebase-adminsdk-fbsvc-be73b150ee.json`.
- **Purpose**: This file contains private keys that allow the FastAPI server to talk to Firebase securely without needing a user to be present. It is used to decode the ID tokens sent by the React app.

## 4. Frontend Setup (Web SDK)
The frontend needs "Client" level access to perform the actual login and signup actions in the browser.

- **Action**:
    1. Go to **Project Settings** > **General**.
    2. Under **"Your apps"**, click the `</>` icon to add a Web App.
    3. Copy the `firebaseConfig` keys.
    4. Paste them into `frontend/.env`.
- **Purpose**: These keys are public. They identify your project to Firebase's public APIs so that users can sign up and receive a token.

## 5. Security & Git
- **Action**: Ensure `.env` and `.json` credential files are in `.gitignore`.
- **Purpose**: You should **never** check these files into GitHub, as they contain secrets that would allow anyone to access your Firebase project.

---

### Configuration Summary
| Component | Requirement | Configuration Path |
| :--- | :--- | :--- |
| **Backend** | Service Account JSON | `backend/FIREBASE_SETUP.md` references the `.json` file. |
| **Frontend** | Web Config Keys | `frontend/.env` |
