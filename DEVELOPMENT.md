# Development & Deployment Guide

This guide explains how to maintain the live production app while developing new features.

## 1. Running in Development Mode

Since the production backend is running on port `8000`, we use port **`8001`** for development.

### Backend (Terminal 1)
Run the Django development server on port 8001 with `DEBUG` enabled:
```bash
cd backend
source .venv/bin/activate
export DJANGO_DEBUG=1
python manage.py runserver 0.0.0.0:8001
```

### Frontend (Terminal 2)
Run the Vite development server:
```bash
cd frontend
npm run dev
```
Access the development app at: `http://<YOUR_IP>:5173` (or whatever IP/port Vite shows).

---

## 2. Deploying Changes to Production

When you are ready to push your changes to the live site:

### Backend Changes (Python/Django)
1.  **Restart the Service**:
    ```bash
    sudo systemctl restart rfms_backend
    ```
    *(Note: If you changed database models, run `python manage.py migrate` first. If you added static files, run `python manage.py collectstatic` first.)*

### Frontend Changes (Vue/JS)
1.  **Build for Production**:
    ```bash
    cd frontend
    npm run build
    ```
    The changes will be live immediately (Nginx serves the new files).

---

## 3. Troubleshooting

-   **500 Error**: Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
-   **Backend Error**: Check Gunicorn logs: `sudo journalctl -u rfms_backend -f`
