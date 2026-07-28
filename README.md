$content = @'
# 🧾 Invoice Generator

A full-stack web application for managing clients, products, and generating professional invoices with PDF export.

## 🚀 Features
- User Authentication (Register/Login)
- Client Management
- Product & Stock Management with Units (sq ft, kg, piece/qty, etc.)
- Invoice Builder with dynamic line items
- PDF Export using ReportLab
- Currency Settings (₹, $, £, €, and more)
- Professional Bootstrap 5 UI with dark sidebar

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **PDF Generation:** ReportLab
- **Authentication:** Flask-Login

## 📦 Installation

1. Clone the repository:
2. Create virtual environment:
3.  Install dependencies:
4.  Set up MySQL database and update config in `app/__init__.py`
5.   Run the app:
   <img width="2238" height="1307" alt="image" src="https://github.com/user-attachments/assets/6603b9b6-ff14-4157-beb5-d38e0b07335d" />

Dashboard with stat cards and revenue chart, professional invoice view with PDF export.

## 👨‍💻 Developer
Om Bharat Patel — UMass Boston, Information Technology
'@
$content | Out-File -FilePath "README.md" -Encoding UTF8
