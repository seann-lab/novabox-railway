# Novabox Web TUI - Railway Deployment Guide

Folder `novabox-railway` ini sudah dilengkapi dengan **Web Terminal (`ttyd`)**. 

Artinya, saat dideploy ke Railway, kamu akan mendapatkan **Domain Web (URL)**. Ketika dibuka di browser HP/Laptop, tampilan TUI Novabox akan muncul di layar dan **bisa diketik / dinavigasi pakai tombol keyboard secara interaktif!**

---

### 🚀 Cara Deploy ke Railway:

1. **Upload ke GitHub:**
   ```bash
   cd ~/storage/shared/opencode-projects/novabox-railway
   git init
   git add .
   git commit -m "Add ttyd Web TUI for Railway"
   git remote add origin <URL_REPO_GITHUB_ANDA>
   git push -u origin main
   ```

2. **Deploy di Railway:**
   - Masuk ke [Railway.app](https://railway.app).
   - Buat **New Project** -> **Deploy from GitHub repo** -> Pilih `novabox-railway`.

3. **Aktifkan Domain Web (Public URL):**
   - Di Railway dashboard, klik service Novabox kamu.
   - Buka tab **Settings** -> bagian **Networking** -> klik **Generate Domain**.
   - Buka link URL yang diberikan (contoh: `https://novabox-production.up.railway.app`).

4. **Gunakan TUI di Browser:**
   - Setelah link dibuka, TUI Novabox akan muncul di browser HP/Laptop.
   - Pilih menu menggunakan tombol **1, 2, 3, dst.** atau tombol panah keyboard.
