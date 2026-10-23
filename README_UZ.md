# Daemon Telegram AI — o'rnatish qo'llanmasi

## 0. Muhim
- Eski xotirani ko'chirmaymiz: yangi Supabase bazasi noldan boshlanadi.
- **ZIP ichidagi `result.json` bo'lmaydi**. Uni GitHub/Render'ga yuklamang.
- `DATABASE_URL` bo'lmasa bot ishga tushmaydi: ma'lumotlar vaqtinchalik diskda qolmasin.
- Guruh tarixini AI tahlil qilishi haqida a'zolarni xabardor qiling va rozilik oling.
- Rhaenyra har bir guruh uchun alohida saqlanadi.

## 1. Supabase
1. https://supabase.com/dashboard -> New project -> `daemon-memory`.
2. Database password yarating va saqlang.
3. Project -> Connect -> **Session pooler** yoki **Direct connection** PostgreSQL URI ni tanlang. IPv4-only hostingda session pooler ma'qul; pooler host/portni dashboarddan nusxalang.
4. `postgresql://...` URI'ni faqat Render Environment'ga `DATABASE_URL` sifatida joylang. URLda maxsus belgili parol bo'lsa URL-encode qiling. `?sslmode=require` kerak bo'lishi mumkin.
5. Supabase loyihasini to'xtatish yoki o'chirish xotiraga ta'sir qiladi. Reja cheklovlari va backup siyosatini tekshiring.

## 2. GitHub va Render
1. ZIP'ni oching. **Ichidagi fayllarni** GitHub repo ildiziga yuklang (qo'shimcha ichki papkaga emas).
2. `result.json`, `.env`, API kalitlari GitHub'ga yuklanmasin.
3. Render -> daemon-ai-bot -> Environment: avvalgi TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, ADMIN_USER_ID, WEBHOOK_SECRET ni saqlang; DATABASE_URL ni qo'shing.
4. `VOICE_ENABLED=true`, `FREE_TTS_ENABLED=true`, `BOT_USERNAME=DaemonDragonAI_bot` qo'ying. ElevenLabs kalitlari ixtiyoriy.
5. Render -> Manual Deploy -> Deploy latest commit (agar avtomatik boshlanmasa). Logs'ni tekshiring.
6. https://daemon-ai-bot.onrender.com/ manzilida `status: ok` chiqishi kerak. Telegram webhook avvalgidek qoladi (URL va secret o'zgarmagan bo'lsa).

## 3. Telegram guruhini sozlash
1. BotFather -> /setprivacy -> Disable (bot yangi guruh xabarlarini ko'ra olishi uchun). Botni guruhdan chiqarib qayta qo'shish kerak bo'lishi mumkin.
2. Guruhda `/chatid` yuboring va chiqgan manfiy chat ID ni yozib oling.
3. Guruh a'zolarini xabardor qiling, keyin bot admini `/learn on` yozadi. Shundan keyin guruhning yangi xabarlari xotiraga yoziladi.
4. Rhaenyra bo'ladigan foydalanuvchining xabariga Reply qilib `/rhaenyra` yuboring.
5. `/profileme Men ...` orqali odam o'zi haqidagi ma'lumotni ixtiyoriy qo'shadi. `/forgetme` profil va o'zining saqlangan xabarlarini o'chiradi (umumiy xulosalarni admin alohida tekshirishi kerak).

## 4. Telegram tarixini eksport qilish
1. Telegram Desktop -> kerakli guruh -> ⋮ -> Export chat history.
2. Machine-readable JSON, so'nggi bir yil, matnli xabarlar; foto/video shart emas.
3. `result.json` faylini shaxsiy kompyuterda saqlang. **Hech qachon GitHub'ga joylamang**.
4. ZIP'ni kompyuterga oching. Windows CMD'ni shu papkada oching.
5. `python -m pip install -r requirements.txt`
6. Lokal `.env` faylini `.env.example` dan yarating va faqat DATABASE_URL hamda GEMINI_API_KEY, GEMINI_MODEL ni to'ldiring. Boshqa tokenlar import uchun kerak emas.
7. Dastlab tekshiring: `python import_telegram_history.py "C:\\Users\\USERNAME\\Desktop\\ChatExport\\result.json" --chat-id -1001234567890 --days 365 --dry-run`
8. To'g'ri guruh ID bo'lsa, `--dry-run` ni olib tashlab qayta bajaring.
9. Tahlilni sinang: `python analyze_history.py --chat-id -1001234567890 --max-batches 1 --dry-run`
10. Tahlilni ishga tushiring: `python analyze_history.py --chat-id -1001234567890 --max-batches 10`. Har ishga tushganda keyingi 10 partiyani tahlil qiladi. 22 MB JSON uchun bir necha marta ishga tushirish kerak bo'lishi mumkin. Gemini API limiti va xarajatlari bor.
11. Boshqa guruhning tarixi bo'lsa, **boshqa chat ID va boshqa result.json** bilan shu amallarni takrorlang.

## 5. Ovoz
- Inglizcha matn bilan murojaat qilinsa va bot javob berishga qaror qilsa, `VOICE_ENABLED=true` bo'lganda ovozli xabar yuborishga urinadi.
- ElevenLabs kaliti/voice ID bo'lsa avval shu xizmat; bo'lmasa `edge-tts` (en-GB-RyanNeural).
- Bu **aktyorning aynan ovozi emas**. Bepul Edge TTS norasmiy servisga bog'liq; ishlamay qolishi mumkin, shunda bot matn yuboradi.
- Telegramga yuboriladigan ovozli xabarni tinglab tekshiring; MP3 sendVoice qo'llab-quvvatlanishi Telegram API versiyasiga bog'liq.

## 6. Cheklovlar
- Daemon har bir xabarni o'qishi mumkin, lekin hammasiga javob bermaydi. Guruhning o'z-o'zidan ishtiroki `/learn on` dan keyin ishlaydi.
- Hozir avtomatik tahlil **guruh voqealari** haqida; foydalanuvchilarga yashirin shaxsiyat baholari berilmaydi.
- `daemon_lore.md` 3-mavsumning batafsil voqealarini hali o'z ichiga olmaydi; tasdiqlanmagan syujetni to'qimaslik uchun bo'sh qoldirilgan.
- Botning xotirasi Supabase mavjudligi, loyihaning faol holati va zaxira nusxalarga bog'liq. Avtomatik backupni alohida yoqing.
- Telegram webhook so'rovlarini 200 bilan tez qabul qilib, background thread'da ishlaydi; Render qayta ishga tushsa ba'zi javoblar yo'qolishi mumkin.
