# REST API Specification

**System Name**: StyleAI — Face Shape Based Hairstyle Recommendation System  
**Base URL**: `http://127.0.0.1:5000/api`  
**API Version**: `v1.0`  
**Data Format**: JSON (`Content-Type: application/json`), Multipart (`multipart/form-data`) for file uploads  

---

## 1. Global Conventions & Architecture

### Authentication Mechanism
Authentication uses **JSON Web Tokens (JWT)**.
Upon successful authentication via `POST /api/auth/login` or `POST /api/auth/register`, a JWT access token is returned.
Client applications MUST include the token in the `Authorization` HTTP header for all protected endpoints:

```http
Authorization: Bearer <JWT_TOKEN>
```

### Standard HTTP Status Codes

| Code | Status | Meaning |
| :--- | :--- | :--- |
| `200` | **OK** | Request completed successfully. |
| `201` | **Created** | Resource successfully created. |
| `400` | **Bad Request** | Invalid inputs, missing required fields, or unsupported file formats. |
| `401` | **Unauthorized** | Missing, invalid, or expired JWT token. |
| `403` | **Forbidden** | User authenticated but lacks required role (e.g. non-admin accessing `/api/admin/*`). |
| `404` | **Not Found** | Requested resource or endpoint does not exist. |
| `422` | **Unprocessable Entity** | Business logic validation failed (e.g. no face detected in uploaded image). |
| `500` | **Internal Server Error** | Unexpected server or database exception. |

### Standard Error Response Format
All error responses adhere to the following JSON structure:

```json
{
  "error": "Descriptive error message explaining the failure."
}
```

---

## 2. Authentication API (`/api/auth`)

### 2.1 User Registration
- **Endpoint**: `POST /api/auth/register`
- **Auth**: Public
- **Request Body**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "SecurePassword123",
    "gender": "female"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "message": "User registered successfully",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "user_id": "60d5ec49f1a2c8123456789a",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "gender": "female",
        "role": "user"
      }
    }
    ```
  - `400 Bad Request`: Validation error or email already registered.

---

### 2.2 User Login
- **Endpoint**: `POST /api/auth/login`
- **Auth**: Public
- **Request Body**:
  ```json
  {
    "email": "jane@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "user_id": "60d5ec49f1a2c8123456789a",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "role": "user"
      }
    }
    ```
  - `401 Unauthorized`: Invalid credentials.

---

## 3. Face Detection & Shape Prediction API (`/api/analyze`)

### 3.1 Upload Portrait & Analyze Face Shape
- **Endpoint**: `POST /api/analyze`
- **Auth**: Required (`Bearer <token>`)
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `image`: File (JPEG, PNG, WEBP, max size 10MB)
  - `gender`: String (optional, e.g. `female`, `male`, `unisex`)
  - `hair_type`: String (optional, e.g. `wavy`, `straight`, `curly`)
  - `hair_length`: String (optional, e.g. `short`, `medium`, `long`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "analysis_id": "60d5ec49f1a2c8123456789b",
      "face_shape": "oval",
      "confidence": 0.965,
      "all_scores": {
        "oval": 0.965,
        "heart": 0.020,
        "round": 0.008,
        "square": 0.004,
        "diamond": 0.002,
        "oblong": 0.001
      },
      "ai_advice": {
        "explanation": "Oval face shapes have balanced proportions. You can wear almost any length and texture.",
        "recommendations": [
          {"name": "Long Layered Waves", "reason": "Frame cheekbones beautifully."}
        ],
        "styles_to_avoid": [
          {"name": "Heavy Blunt Bangs", "reason": "Can shorten an elegant oval outline."}
        ],
        "styling_tips": ["Maintain natural volume at the crown."]
      },
      "recommendations": [
        {
          "id": "60d5ec49f1a2c81234567801",
          "name": "Long Layered Waves",
          "compatibility": 0.965,
          "gender": "female",
          "hair_length": "long",
          "category": "classic",
          "image_url": "/uploads/hairstyles/long_waves.jpg"
        }
      ]
    }
    ```
  - `422 Unprocessable Entity`: No human face detected in image.

---

## 4. Hairstyle Recommendation Engine API (`/api/recommend`)

### 4.1 Get Recommendations
- **Endpoint**: `GET /api/recommend`
- **Auth**: Required (`Bearer <token>`)
- **Query Parameters**:
  - `shape`: String (required: `oval`, `round`, `square`, `heart`, `diamond`, `oblong`)
  - `gender`: String (optional: `female`, `male`, `unisex`)
  - `hair_type`: String (optional: `straight`, `wavy`, `curly`, `coily`)
  - `hair_length`: String (optional: `short`, `medium`, `long`)
  - `category`: String (optional: `classic`, `modern`, `edgy`, `formal`, `casual`)
  - `maintenance_level`: String (optional: `low`, `medium`, `high`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "face_shape": "square",
      "count": 4,
      "hairstyles": [
        {
          "id": "60d5ec49f1a2c81234567802",
          "name": "Layered Shag Cut",
          "compatibility": 0.94,
          "face_shapes": ["square", "round"],
          "gender": "female",
          "hair_length": "medium",
          "maintenance_level": "low",
          "popularity": 92
        }
      ]
    }
    ```

---

## 5. Generative AI Virtual Try-On API (`/api/tryon`)

### 5.1 Generate Virtual Hairstyle Try-On
- **Endpoint**: `POST /api/tryon`
- **Auth**: Required (`Bearer <token>`)
- **Request Body**:
  ```json
  {
    "analysis_id": "60d5ec49f1a2c8123456789b",
    "hairstyle_id": "60d5ec49f1a2c81234567802"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "tryon_id": "60d5ec49f1a2c8123456789c",
      "hairstyle_name": "Layered Shag Cut",
      "result_image": "data:image/jpeg;base64,...",
      "model_used": "Gemini 2.0 Flash / Fallback Blender",
      "created_at": "2026-07-21T22:45:00Z"
    }
    ```

---

## 6. History Management API (`/api/history`)

### 6.1 Get Scan History
- **Endpoint**: `GET /api/history`
- **Auth**: Required (`Bearer <token>`)
- **Query Params**: `search`, `shape`, `page`, `limit`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "analyses": [
        {
          "analysis_id": "60d5ec49f1a2c8123456789b",
          "face_shape": "oval",
          "confidence": 0.965,
          "created_at": "2026-07-21T20:15:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "limit": 10
    }
    ```

### 6.2 Update Selected Hairstyle
- **Endpoint**: `PATCH /api/history/<analysis_id>/select-hairstyle`
- **Auth**: Required (`Bearer <token>`)
- **Request Body**:
  ```json
  {
    "hairstyle_id": "60d5ec49f1a2c81234567802",
    "name": "Layered Shag Cut"
  }
  ```
- **Responses**: `200 OK` `{"updated": true}`

### 6.3 Delete History Record / Clear History
- **Endpoint**: `DELETE /api/history/<analysis_id>` or `DELETE /api/history`
- **Auth**: Required (`Bearer <token>`)
- **Responses**: `200 OK` `{"deleted": true}`

---

## 7. Profile & User Preferences API (`/api/auth/profile`)

### 7.1 Get & Update User Profile
- **Endpoint**: `GET /api/auth/profile` and `PUT /api/auth/profile`
- **Auth**: Required (`Bearer <token>`)
- **Request Body (PUT)**:
  ```json
  {
    "name": "Jane Smith",
    "gender": "female",
    "hair_type": "wavy",
    "hair_length": "long"
  }
  ```
- **Responses**: `200 OK` with updated profile.

---

## 8. Admin Operations API (`/api/admin`)

### 8.1 System Analytics Dashboard
- **Endpoint**: `GET /api/admin/analytics`
- **Auth**: Admin Required (`@admin_required`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "total_users": 150,
      "active_users": 142,
      "admin_users": 3,
      "total_scans": 482,
      "total_tryons": 310,
      "total_hairstyles": 16,
      "face_shape_distribution": {
        "oval": 120, "round": 95, "square": 80,
        "heart": 75, "diamond": 62, "oblong": 50
      }
    }
    ```

### 8.2 User Management (RBAC Role Assignment & Deletion)
- **Endpoints**: `GET /api/admin/users`, `PATCH /api/admin/users/<id>`, `DELETE /api/admin/users/<id>`
- **Auth**: Admin Required (`@admin_required`)

### 8.3 Hairstyle Catalog CRUD
- **Endpoints**: `POST /api/admin/hairstyles`, `PUT /api/admin/hairstyles/<id>`, `DELETE /api/admin/hairstyles/<id>`
- **Auth**: Admin Required (`@admin_required`)
