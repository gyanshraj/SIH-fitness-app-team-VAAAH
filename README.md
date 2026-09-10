# SIH-fitness-app-team-VAAAH

Starter scaffold for a beginner-friendly **Android fitness app + website** project.

## Recommended Beginner Stack

### Android App
- **Kotlin** + **Jetpack Compose**
- **MVVM** architecture
- **Retrofit** for API calls
- **Room** for local offline data

### Website
- **React** + **Vite**
- **React Router**
- **Axios** for API calls
- Optional: **Tailwind CSS**

### Online Integration (App + Website)
- **Firebase** (best beginner option)
  - Authentication (login/signup)
  - Firestore (cloud database)
  - Storage (profile/workout media)
  - Hosting (website deployment)

## Basic Project Structure

```text
SIH-fitness-app-team-VAAAH/
├── android-app/
│   ├── README.md
│   └── app/
│       └── src/
│           └── main/
│               ├── AndroidManifest.xml
│               ├── java/com/vaaah/fitness/
│               └── res/layout/
├── website/
│   ├── README.md
│   ├── public/
│   └── src/
└── README.md
```

## Suggested Next Step
Initialize each folder with real tooling:
- Android Studio project in `android-app/`
- `npm create vite@latest website` in `website/`
