# License Plate & QR Code Access Control System

## Description
This project is an automated access control system that uses **license plate recognition** and **QR code scanning** to authorize vehicle and user entry.  
The system verifies the scanned data against a **SQLite database** and, if access is authorized, sends a signal via **Ethernet/Wi-Fi** to an **Arduino**, which triggers a gate opening mechanism.

This project was developed as an academic project and focuses on backend logic, data validation, and integration between software and hardware.

---

## Features
- License plate recognition
- QR Code scanning
- Access authorization based on database records
- SQLite database integration
- Communication with Arduino via Ethernet/Wi-Fi
- Automated gate control logic

---

## Technologies Used
- **Python**
- **SQLite**
- **OpenCV** (for image processing / license plate recognition)
- **QR Code Reader**
- **Arduino**
- **Ethernet / Wi-Fi Communication**

---

## How It Works
1. The system reads a **QR Code** or captures an image of a vehicle license plate.
2. The extracted data is validated against records stored in a **SQLite database**.
3. If the access is authorized:
   - A signal is sent to the Arduino via Ethernet or Wi-Fi.
   - The Arduino activates the gate opening mechanism.
4. If the access is not authorized, the gate remains closed.

---

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/Arthyxx/projeto-leitor_placa.git
