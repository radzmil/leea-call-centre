# Leea Bot — telefon Architech Systems (versi asas)

`phone_server.py` menerima webhook panggilan masuk Twilio dan menjawab menggunakan modul Leea Bot. Ini aliran **bergilir** (dengar satu soalan → jawab → dengar semula), bukan streaming audio dua hala. `Procfile` menjalankan pelayan telefon pada `0.0.0.0:$PORT` untuk hos seperti Railway. Tiada nombor telefon boleh aktif sebelum servis dideploy dan nombor Twilio dikonfigurasi.

Maklumat produk boleh diselaraskan dengan bot WhatsApp, tetapi **pembayaran melalui telefon tidak dibenarkan**. Bot telefon hanya menerangkan harga; ia tidak menerima bayaran, meminta kad/OTP/PIN/butiran bank atau mengesahkan resit dan transaksi. Pertanyaan pembayaran dialihkan kepada pasukan Architech Systems melalui saluran rasmi untuk semakan kaedah yang sah.

## Aktifkan panggilan masuk

1. Semak fakta/harga `knowledge.json`, privasi dan izin penggunaan transkripsi/suara bersama syarikat. Jangan gunakan data klien lain. Uji `python -m unittest discover -v`.
2. Deploy folder ini pada hos HTTPS yang menyokong `Procfile` (`web: python phone_server.py`). Tetapkan environment variable `PUBLIC_BASE_URL` kepada URL awam HTTPS **tepat** tanpa slash akhir, dan `TWILIO_AUTH_TOKEN` daripada akaun Twilio sebagai secret hos. Jangan commit token; `.env.example` hanya nama pembolehubah. `PORT` diberikan oleh hos.
3. Di konsol Twilio untuk nombor telefon voice milik anda, tetapkan **A CALL COMES IN → Webhook → POST** ke `https://domain-anda/voice/incoming`. URL mesti sepadan dengan `PUBLIC_BASE_URL` untuk pengesahan tandatangan. Sahkan `GET /health` memberi `ok`, kemudian buat panggilan sebenar dan uji pengenalan Bahasa Melayu, sebutan, harga serta penamatan "tamat".

Twilio mengurus speech-to-text dan text-to-speech dalam aliran telefon ini; **Deepgram dan Cartesia belum digunakan untuk panggilan**. Dokumentasi Twilio `<Gather>` menyenaraikan `ms-MY`, tetapi sokongan speech model berbeza; semak model yang dipilih dan uji transkripsi pada akaun sebenar. Untuk `<Say>`, pilih suara yang secara khusus menyokong `ms-MY` dalam tetapan Text-to-Speech Twilio; jangan anggap suara lalai akaun menyokong Bahasa Melayu. Uji sebutan sebelum trafik sebenar. Belum ada handoff kepada manusia, kawalan kos/rate, log audit, penyimpanan persetujuan atau high availability. Jangan buka kepada pelanggan sebelum itu diselesaikan.

`web_demo.py` dan `index.html` masih wujud sebagai artifak simulasi lama dalam folder ini; demo browser utama berada dalam projek `demo-ai-call-centre` yang berasingan. Jangan gunakan laman simulasi sebagai bukti panggilan telefon berfungsi.

## Jalankan

Perlukan Python 3; kod demo menggunakan pustaka standard Python. Dari folder ini:

```powershell
python -m unittest discover -v
python web_demo.py
```

Buka `http://127.0.0.1:8765/` dalam Chrome/Edge. Jika mikrofon tidak berfungsi, taip soalan dalam medan fallback. Untuk suara Cartesia, tetapkan `CARTESIA_API_KEY` sebagai environment variable pada pelayan; `CARTESIA_VOICE_ID` pilihan jika suara Aisyah tidak dapat dicari secara unik. `.env.example` ialah contoh nama sahaja dan tidak dibaca secara automatik. Tanpa Cartesia, browser mungkin menggunakan suara setempat. Jangan masukkan kunci dalam HTML, kod atau GitHub.

`knowledge.json` mengandungi katalog demo Architech Systems yang dirujuk daripada laman syarikat; sahkan harga, ciri dan ketersediaan dengan pemilik sebelum digunakan untuk jualan. `business_hours` dan `payment_method` kosong kerana belum disahkan. `bot_payment.py` tidak memproses transaksi; jangan minta butiran kad. Modul `bot_*` mengasingkan profil, fakta, persona Leea Bot, SOP dan aliran jawapan. `assistant.py` membekalkan demo CLI dan API jawapan untuk `web_demo.py`.

## GitHub

Semak sendiri `knowledge.json` dan `index.html` (termasuk nombor paparan) sebelum push. `.gitignore` mengecualikan `.env` dan cache Python; **jangan** tambah rahsia dengan `git add -f`. Folder ini belum semestinya mempunyai repositori atau remote Git; muat naik hanya selepas semakan dan sambungkan kepada repositori GitHub milik anda. `phone_server.py` mendengar pada `0.0.0.0:$PORT` apabila dimulakan melalui `Procfile`; webhook memerlukan HTTPS di hadapan pelayan.

## Status binaan AI Call Centre sebenar

Yang sudah ada: laman simulasi panggilan browser (`index.html`), API jawapan dan TTS (`web_demo.py`), profil syarikat (`knowledge.json`), modul `bot_*`, serta ujian. Pengecaman suara ialah fungsi browser, bukannya Deepgram; sintesis suara boleh menggunakan Cartesia jika dikonfigurasi. Tiada dependensi pip untuk demo ini, maka tiada `requirements.txt` diperlukan.

Yang **belum disahkan/dibina**: deployment HTTPS, konfigurasi nombor Twilio dan ujian panggilan sebenar; aliran audio dua hala/STT Deepgram; eskalasi kepada manusia, persetujuan privasi, had kadar, pemantauan dan ketahanan production. Webhook Twilio dengan pengesahan tandatangan sudah ada, tetapi ujian setempat sahaja tidak membuktikan panggilan telefon sudah berfungsi.