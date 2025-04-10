# **Waydroid Helper**  
**A Lomiri System Settings plugin for managing Waydroid containers and Android apps on Ubuntu Touch.**

---

## **Table of Contents**
1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Contributors](#contributors)
7. [License](#license)
8. [Acknowledgments](#acknowledgments)

---

## **Overview**

The **Waydroid Helper** is a **Lomiri System Settings plugin** designed to simplify the management of **Waydroid containers** and **Android apps** on Ubuntu Touch. It provides users with an intuitive interface to:
- Start, stop, freeze, and restart Waydroid containers.  
- Monitor real-time resource usage (CPU, RAM, storage).  
- Toggle visibility of Waydroid apps in the Ubuntu Touch app drawer.  
- Automate Waydroid initialization and updates.  

This project was developed as part of the **Foss FEST 2025 Hackathon** by **Team Nebula Nexus**.

---

## **Features**

- **Container Control**: Start, stop, freeze, and restart Waydroid containers.  
- **Resource Monitoring**: Display real-time CPU, RAM, and storage usage.  
- **App Visibility Management**: Toggle visibility of Waydroid apps in the app drawer.  
- **Automation**: Automate Waydroid initialization and updates.  
- **User-Friendly UI**: Integrated into Lomiri System Settings for seamless user experience.  

---

## **Requirements**

### **Software Requirements**
- **Ubuntu Touch**: The target platform for the application.  
- **Python 3.8+**: For backend logic.  
- **SQLite**: For database storage.  
- **Lomiri SDK**: For testing Ubuntu Touch apps.  

### **Hardware Requirements**
- A device running **Ubuntu Touch** or an emulator for testing.  

---

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/waydroid-helper.git
cd waydroid-helper
```

### **2. Set Up the Development Environment**
1. Install **Python 3.8+**:
   ```bash
   sudo apt install python3
   ```
2. Install required Python libraries:
   ```bash
   pip install psutil
   ```
3. Install **SQLite** (if not already installed):
   ```bash
   sudo apt install sqlite3
   ```

### **3. Create the Database**
Run the following command to create the database:
```bash
sqlite3 settings.db < database/schema.sql
```

### **4. Deploy to Ubuntu Touch**
1. Install the **Lomiri SDK** on your development machine.  
2. Deploy the QML frontend to your Ubuntu Touch device or emulator.  
3. Run the Python backend script to handle logic and database interactions.  

---

## **Usage**

1. **Open Lomiri System Settings**: Navigate to the **Waydroid Helper** plugin.  
2. **Control Waydroid Containers**: Use the buttons to start, stop, or freeze Waydroid.  
3. **Monitor Resources**: View real-time CPU, RAM, and storage usage.  
4. **Manage App Visibility**: Toggle visibility of Waydroid apps in the app drawer.  

---

## **Contributors**

This project was developed by **Team Nebula Nexus** during the **Foss FEST Hackathon**.  

### **Team Members**
- **Ismael N Mudjanima**  
- **Hilma Uupindi**  
- **Nelson Shishiveni**  
- **Emma Muulyao**  
- **Saya Mubiana**  

---

## **License**

This project is licensed under the **GNU General Public License v3.0**.  
See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**

- **PyCon Namibia 2025** for organizing the Hackathon.  
- **Ubuntu Touch Community** for their support and resources.  
- **Waydroid Developers** for creating an amazing tool for running Android apps on Linux.  

---

## **Contact**

For questions or feedback, please contact:  
**Team Nebula Nexus**  
Email: [team@nebulanexus.com]
GitHub: [https://github.com/Ally-Ismael/Nebula-Nexus]

---

Thank you for using **Waydroid Helper**! 🚀  

---

