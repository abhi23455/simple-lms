# Simple LMS - Django & Docker

Proyek ini adalah inisialisasi pengembangan Simple LMS menggunakan Django dan Docker.

## Prasyarat
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Struktur Proyek
```text
simple-lms/
├── config/                 # Konfigurasi utama Django
├── courses/                # Aplikasi manajemen kursus (Progres 2)
│   ├── fixtures/           # Data awal kursus
│   ├── admin.py            # Kustomisasi Admin Panel
│   └── models.py           # Database Schema (ORM)
├── users/                  # Aplikasi manajemen user (Custom User Model)
├── optimization_demo.py    # Script demo optimasi query N+1
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .env
├── requirements.txt
├── manage.py
└── README.md
```

## Progres 2: Django ORM & Models
Fitur yang telah diimplementasikan:
- **Custom User Model**: Mendukung role `admin`, `instructor`, dan `student`.
- **Database Schema**: Model `Category`, `Course`, `Lesson`, `Enrollment`, dan `Progress` dengan relasi yang tepat.
- **Optimasi Query**: Implementasi custom QuerySet dengan `select_related` dan `prefetch_related` untuk menghindari masalah N+1.
- **Django Admin**: Kustomisasi tampilan list, filter, search, dan inline editing untuk `Lesson`.
- **Demo Optimasi**: Jalankan `docker-compose exec web python optimization_demo.py` untuk melihat perbandingan performa query.

## Progres 3: REST API dengan Django Ninja & JWT
Fitur yang telah diimplementasikan:
- **Authentication**: Register, Login, Refresh Token, dan Profile Management menggunakan JWT.
- **REST API**: Endpoint lengkap untuk Courses, Enrollments, dan Progress tracking.
- **RBAC (Role-Based Access Control)**: Izin akses berdasarkan role (Admin, Instructor, Student).
- **API Documentation**: Swagger UI otomatis tersedia di `/api/docs`.
- **Validation**: Schema validation menggunakan Pydantic v2.

### Endpoints Utama:
- `POST /api/auth/register`: Daftar user baru.
- `POST /api/auth/login`: Login untuk mendapatkan Access & Refresh token.
- `GET /api/auth/me`: Informasi profil user saat ini (perlu Token).
- `GET /api/courses/`: Daftar semua kursus (Public).
- `POST /api/courses/`: Membuat kursus baru (Instructor only).
- `POST /api/courses/enroll`: Mendaftar ke kursus (Student only).

## Cara Menjalankan
1. Jalankan Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
2. Akses Dokumentasi API (Swagger):
   Buka [http://localhost:8000/api/docs](http://localhost:8000/api/docs) di browser Anda.

## Cara Testing (CLI)
Anda dapat menjalankan script testing otomatis:
```bash
python test_api.py
```

## Environment Variables
- `DEBUG`: Mengaktifkan mode debug (1 untuk aktif, 0 untuk nonaktif).
- `SECRET_KEY`: Kunci rahasia Django.
- `DB_NAME`: Nama database PostgreSQL.
- `DB_USER`: Username database.
- `DB_PASSWORD`: Password database.
- `DB_HOST`: Host database (gunakan `database` untuk Docker).
- `DB_PORT`: Port database (default `5432`).
- `ALLOWED_HOSTS`: Daftar host yang diizinkan.

## Services
- **Web**: Django application running on Python 3.11.
- **Database**: PostgreSQL 15 database.

## screenshoot progress 1-3
- ![weclome page](ssDjangowelcome.png)

- ![Django admin](ssDjangoAdmin.png)

- ![rest api1](<ssREST API.png>)

- ![rest api2](<ssREST API2.png>)

## Author --
Abhirama Maulana Putra
