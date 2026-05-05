# 🎫 কাস্টমার সাপোর্ট টিকেট ক্লাসিফায়ার প্রজেক্ট - বাংলা ডকুমেন্টেশন

## ✨ প্রজেক্ট ওভারভিউ

এই প্রজেক্টটি একটি **প্রোডাকশন-রেডি FastAPI সার্ভিস** যা কাস্টমার সাপোর্ট টিকেটগুলিকে স্বয়ংক্রিয়ভাবে ক্লাসিফাই করে, AI দ্বারা উত্তরের পরামর্শ দেয় এবং API খরচ ট্র্যাক করে।

**মূল উদ্দেশ্য:**
- গ্রাহকদের সাপোর্ট টিকেট আসলে সেগুলি বিভিন্ন ক্যাটাগরিতে বিভক্ত করা (Bug, Feature Request, Billing, General Inquiry, Urgent)
- Anthropic Claude AI ব্যবহার করে স্বয়ংক্রিয় ক্লাসিফিকেশন
- Redis ক্যাশিং ব্যবহার করে একই টিকেটের জন্য API কল কমানো
- SSE (Server-Sent Events) এর মাধ্যমে রিয়েল-টাইমে উত্তরের পরামর্শ স্ট্রিম করা
- প্রতিটি API কলের খরচ ট্র্যাক করা এবং দৈনিক বাজেট সীমা নির্ধারণ করা

---

## 🛠️ প্রযুক্তি স্ট্যাক এবং ডিপেন্ডেন্সিজ

### কেন এই ডিপেন্ডেন্সিজ দরকার?

```
**Backend Framework:**
- fastapi==0.115.0          → আধুনিক, দ্রুত ওয়েব ফ্রেমওয়ার্ক (Python)
- uvicorn==0.30.6           → FastAPI চালানোর জন্য ASGI সার্ভার

**Database & ORM:**
- sqlalchemy[asyncio]==2.0.35 → Async ডাটাবেস ইন্টারঅ্যাকশন (আধুনিক Python ওয়ে)
- asyncpg==0.29.0           → PostgreSQL এর সাথে দ্রুত async কানেকশন
- greenlet==3.1.1           → SQLAlchemy async এর জন্য গ্রিনলেট (হালকা থ্রেড)

**ডেটা ভ্যালিডেশন:**
- pydantic==2.9.2           → Request/Response স্কিমা ভ্যালিডেশন এবং টাইপ চেকিং
- pydantic-settings==2.5.2  → Environment variables থেকে কনফিগারেশন লোড করা

**Cache & Session Management:**
- redis==5.1.1              → Redis ক্লায়েন্ট (LLM response caching এর জন্য)

**AI/LLM:**
- anthropic==0.34.2         → Anthropic Claude API এর সাথে কথা বলার জন্য

**Rate Limiting:**
- slowapi==0.1.9            → API রেট লিমিটিং (DDoS থেকে রক্ষা)

**SSE Streaming:**
- sse-starlette==2.1.3      → Server-Sent Events ইমপ্লিমেন্টেশন

**Logging:**
- python-json-logger==2.0.7 → Structured JSON logging (প্রোডাকশনে গুরুত্বপূর্ণ)

**Testing:**
- pytest==8.3.3             → টেস্টিং ফ্রেমওয়ার্ক
- pytest-asyncio==0.24.0    → Async কোডের জন্য pytest সাপোর্ট
- httpx==0.27.2             → API টেস্টিং

**Quality & Type Checking:**
- ruff==0.6.9               → কোড ফরম্যাটিং এবং লিন্টিং
- mypy==1.11.2              → Static type checking
```

---

## 📁 প্রজেক্ট স্ট্রাকচার

```
project-1-ticket-classifier/
│
├── app/                          # মূল অ্যাপ্লিকেশন
│   ├── main.py                  # FastAPI এপ্লিকেশন এন্ট্রি পয়েন্ট
│   ├── config.py                # সেটিংস এবং কনফিগারেশন
│   ├── database.py              # Database ইঞ্জিন এবং সেশন ম্যানেজমেন্ট
│   ├── redis_client.py          # Redis ক্লায়েন্ট ইনিশিয়ালাইজেশন
│   │
│   ├── models/                  # Database মডেল
│   │   ├── ticket.py            # Ticket টেবিল মডেল
│   │   ├── classification.py    # Classification টেবিল মডেল
│   │   └── api_cost.py          # API Cost ট্র্যাকিং টেবিল মডেল
│   │
│   ├── schemas/                 # Pydantic ভ্যালিডেশন স্কিমা
│   │   ├── ticket.py            # Ticket Request/Response স্কিমা
│   │   ├── classification.py    # Classification স্কিমা
│   │   └── analytics.py         # Analytics স্কিমা
│   │
│   ├── services/                # ব্যবসায়িক যুক্তি
│   │   ├── classifier.py        # AI ক্লাসিফিকেশন লজিক + Redis কেশিং
│   │   ├── cost_tracker.py      # খরচ ট্র্যাকিং এবং বাজেট ম্যানেজমেন্ট
│   │   └── suggester.py         # SSE স্ট্রিমিং দ্বারা সাজেশন জেনারেশন
│   │
│   ├── routers/                 # API এন্ডপয়েন্টস
│   │   ├── tickets.py           # Ticket CRUD এবং classification এন্ডপয়েন্টস
│   │   ├── analytics.py         # Analytics এন্ডপয়েন্টস
│   │   └── health.py            # স্বাস্থ্য চেক এন্ডপয়েন্টস
│   │
│   └── utils/                   # হেল্পার ফাংশনস
│       ├── exceptions.py        # কাস্টম এক্সেপশন এবং হ্যান্ডলার
│       └── logging.py           # লগিং কনফিগারেশন
│
├── alembic/                     # ডাটাবেস মাইগ্রেশন (SQL আপডেট ম্যানেজমেন্ট)
├── tests/                       # টেস্ট স্যুট
├── requirements.txt             # Python ডিপেন্ডেন্সিজ
├── pyproject.toml               # প্রজেক্ট মেটাডেটা
├── Dockerfile                   # Docker ইমেজ বিল্ড নির্দেশাবলী
├── docker-compose.yml           # Multi-container সেটআপ
└── README.md                    # ইংরেজি ডকুমেন্টেশন
```

---
চমৎকার প্রশ্ন! এই `main.py` ফাইলটি পুরো প্রজেক্টের **এন্ট্রি পয়েন্ট** (মূল প্রবেশদ্বার) - যেখান থেকে সবকিছু শুরু হয়। চলুন ডিটেইল ভাঙিয়ে বলি:

## 🎯 **এই ফাইলের মূল কাজ**

```
পুরো প্রজেক্টের "কন্ট্রোল সেন্টার" 
→ সব রাউটার এখানে রেজিস্টার হয়
→ সব মিডলওয়্যার এখানে সেট হয়  
→ সার্ভার শুরু/বন্ধ হওয়ার নিয়ম এখানে থাকে
```

## 📋 **পার্ট ১: ইমপোর্ট (কেন এইগুলো লাগে?)**

```python
import logging, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from slowapi import Limiter
```

| ইমপোর্ট | কেন লাগে? |
|---------|-----------|
| `logging` | প্রতিটি রিকোয়েস্ট লগ করতে (ডিবাগ ও মনিটরিংয়ের জন্য) |
| `time` | রিকোয়েস্ট কত সময় নিল সেটা মাপতে |
| `asynccontextmanager` | সার্ভার start/stop এ যা করতে হবে সেটা define করতে |
| `slowapi` | rate limiting - এক ইউজার অনেক রিকোয়েস্ট পাঠালে ব্লক করতে |
| `CORSMiddleware` | ব্রাউজার থেকে অন্য ডোমেইনে API call করতে দিতে |

## 🔧 **পার্ট ২: রেট লিমিটার (Protection System)**

```python
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
```

**কাজ:** একজন ইউজার ১ মিনিটে যতগুলো রিকোয়েস্ট করতে পারবে সেটা নির্ধারণ করে

```python
# উদাহরণ: যদি rate_limit = "10/minute" হয়
# তাহলে এক আইপি থেকে প্রতি মিনিটে ১০টির বেশি রিকোয়েস্ট আসলে
# ১১তম রিকোয়েস্টে error দিবে "Too many requests"
```

## 🔄 **পার্ট ৩: Lifespan (জীবনচক্র ব্যবস্থাপনা)**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup (সার্ভার চালু হওয়ার সময়)
    await init_db()  # ডাটাবেস টেবিল তৈরি করে
    logger.info("Database tables created/verified")
    
    yield  # সার্ভার চলছে
    
    # Shutdown (সার্ভার বন্ধ হওয়ার সময়)
    await close_db()      # DB connection বন্ধ করে
    await close_redis()   # Redis connection বন্ধ করে
```

**সোজা ভাষায়:** 
- **Startup:** সার্ভার চালু হলেই ডাটাবেস ready করে দেয়
- **Shutdown:** সার্ভার বন্ধ হলে connection গুলো clean করে

## 🏗️ **পার্ট ৪: FastAPI App (প্রধান অ্যাপ объект)**

```python
app = FastAPI(
    title="Customer Support Ticket Classifier & Suggester",
    description="...",  # API ডকুমেন্টেশনে দেখাবে
    version="1.0.0",
    lifespan=lifespan,  # উপরে define করা lifespan function
    docs_url="/docs",   # Swagger UI এখানে পাওয়া যাবে
)
```

**ফলাফল:** 
- ব্রাউজারে গেলেই API ডকুমেন্টেশন দেখাবে
- http://localhost:8000/docs → এখানে সব endpoint এর তালিকা

## 🛡️ **পার্ট ৫: মিডলওয়্যার (প্রত্যেক রিকোয়েস্টের আগে/পরে কাজ করে)**

### 5.1 CORS Middleware
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # সব ডোমেইন থেকে request নিবে (Production এ সীমিত করা ভাল)
)
```
**কাজ:** ফ্রন্টএন্ড (React/Vue) থেকে API কল করতে দেয়

### 5.2 Request Logging Middleware (সবচেয়ে গুরুত্বপূর্ণ)
```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    rid = generate_request_id()  # ইউনিক আইডি বানায় (যেমন: "req_abc123")
    
    start_time = time.perf_counter()  # সময় মাপা শুরু
    
    response = await call_next(request)  # আসল request টি execute করে
    
    duration_ms = (time.time() - start_time) * 1000  # কত সময় নিল?
    
    logger.info("Request completed", extra={
        "request_id": rid,
        "method": "POST",
        "path": "/tickets/classify",
        "status_code": 200,
        "duration_ms": 152.3
    })
    
    response.headers["X-Request-ID"] = rid  # ক্লায়েন্টকে আইডি জানিয়ে দেয়
    return response
```

**কাজ:** 
- প্রতিটি রিকোয়েস্টের **ইউনিক আইডি** বানায়
- কত সময় নিল সেটা মাপে
- সব লগ **JSON ফরম্যাটে** save করে (পরে analyze করার জন্য)
- Response এ `X-Request-ID` header যোগ করে (ডিবাগের জন্য)

## 🗺️ **পার্ট ৬: রাউটার রেজিস্ট্রেশন (API endpoints সংযুক্ত করা)**

```python
app.include_router(health.router)    # /health - সার্ভার alive কিনা চেক করে
app.include_router(tickets.router)   # /tickets - টিকেট classify করে
app.include_router(analytics.router) # /analytics - cost report দেখায়
```

**কাজ:** বিভিন্ন ফাইলে আলাদা করা API endpoints গুলোকে main app এ যুক্ত করে

## 📦 **পার্ট ৭: রুট এন্ডপয়েন্ট**

```python
@app.get("/")
async def root():
    return {
        "service": "Ticket Classifier",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
```

**কাজ:** http://localhost:8000/ এ গেলে API পরিচিতি দেখায়

## 🎨 **পুরো ফ্লো চিত্র (Visual Flow)**

```
ইউজার রিকোয়েস্ট আসলো (POST /tickets/classify)
    ↓
1️⃣ Logging Middleware দেখে: request_id = "req_123", start_time = 10:00:00
    ↓
2️⃣ Rate Limiter চেক করে: এই IP আজ ১০টার মধ্যে ৩য় request? → হ্যাঁ, যেতে দাও
    ↓
3️⃣ CORS Middleware চেক করে: কোন domain থেকে এসেছে? → সব domain allowed
    ↓
4️⃣ Router খুঁজে বের করে: /tickets/classify → tickets.router এ পাঠায়
    ↓
5️⃣ আমাদের লজিক execute হয় (Claude API call, database save)
    ↓
6️⃣ Response তৈরি হয় (classification result)
    ↓
7️⃣ Logging Middleware আবার: duration_ms = 152ms, status=200, লগ সেভ করে
    ↓
ইউজার রেসপন্স পায় (Request-ID header সহ)
```

## 🔑 **কী কী শিখলাম এই ফাইল থেকে?**

| কনসেপ্ট | বাংলা অর্থ | কেন লাগে? |
|---------|-----------|-----------|
| **Entry Point** | শুরু করার জায়গা | পুরো app এখান থেকে চালু হয় |
| **Lifespan** | জীবনচক্র | সার্ভার চালু/বন্ধ করার সময় clean 작업 |
| **Middleware** | মাঝখানের স্তর | প্রতিটি request আগে/পরে কিছু করার জন্য |
| **Rate Limiting** | গতি সীমা | এক ইউজার অনেক request করলে ব্লক করতে |
| **Request ID** | ইউনিক শনাক্তকারী | সমস্যা হলে কোন request টা খারাপ হয়েছিল সেটা track করতে |
| **Structured Logging** | সাজানো লগ | পরে ডাটাবেসে query করে analyze করতে |

## 💡 **প্রোডাকশনে কেন এই ফাইল গুরুত্বপূর্ণ?**

1. **Debugging:** যখন প্রোডাকশনে error হবে, তখন request_id দেখে exact request টা খুঁজে বের করতে পারবেন
2. **Performance:** duration_ms দেখে জানবেন কোন endpoint slow
3. **Security:** rate limiting থাকায় কেউ ১ লাখ request পাঠিয়ে সার্ভার crash করতে পারবে না
4. **Maintainability:** সব router এক জায়গায় registered, কোড বোঝা সহজ

## 📝 **এই ফাইলে আমরা যা যা configure করলাম:**

✅ ডাটাবেস initialization  
✅ Redis connection management  
✅ Rate limiting  
✅ CORS (frontend থেকে access)  
✅ Request logging with unique ID  
✅ Exception handlers  
✅ Routers registration  

**মনে রাখবেন:** এই ফাইলটি একবার লিখে দিলে, পরবর্তীতে শুধু routers এবং models নিয়ে কাজ করতে হবে। সব infrastructure setup ready!

আপনার কি এই ফাইলের কোনো নির্দিষ্ট অংশ নিয়ে প্রশ্ন আছে? 🚀
-----

## 💾 ডাটাবেস মডেল এবং এদের সম্পর্ক

### 1️⃣ **Ticket মডেল** (`app/models/ticket.py`)

টিকেট টেবিলে গ্রাহকের সাপোর্ট রিকোয়েস্ট স্টোর করা হয়।

```python
class Ticket(Base):
    __tablename__ = "tickets"
    
    id: int                    # Primary key - প্রতিটি টিকেটের ইউনিক আইডি
    subject: str              # টিকেটের শিরোনাম (3-500 অক্ষর)
    description: str          # বিস্তারিত বর্ণনা (10-5000 অক্ষর)
    priority: Priority        # অগ্রাধিকার: LOW, MEDIUM, HIGH, CRITICAL
    created_at: datetime      # তৈরির সময় (স্বয়ংক্রিয়)
    updated_at: datetime      # শেষ আপডেটের সময় (স্বয়ংক্রিয়)
    
    # সম্পর্ক
    classification: Classification  # এক টিকেটের এক ক্লাসিফিকেশন (One-to-One)
```

**কেন এই ফিল্ডগুলি?**
- `subject` এবং `description` → গ্রাহকের সমস্যা বোঝার জন্য
- `priority` → টিকেটের জরুরিতা নির্ধারণ করতে
- `created_at` এবং `updated_at` → রেকর্ড ট্র্যাকিং এবং অ্যানালিটিক্সের জন্য
- `index=True` subject-এ → দ্রুত সার্চ করার জন্য

---

### 2️⃣ **Classification মডেল** (`app/models/classification.py`)

এই টেবিলে AI দ্বারা ক্লাসিফাই করা তথ্য স্টোর করা হয়।

```python
class Classification(Base):
    __tablename__ = "classifications"
    
    id: int                      # Primary key
    ticket_id: int              # Foreign key → Ticket টেবিল
    category: str               # ক্যাটাগরি: Bug, Feature Request, Billing, General Inquiry, Urgent
    confidence: float           # আত্মবিশ্বাসের স্কোর (0.0 - 1.0)
    reasoning: str              # কেন এই ক্যাটাগরি বেছে নিয়েছে, AI-র ব্যাখ্যা
    input_tokens: int           # ইনপুট টোকেন ব্যবহার (খরচ হিসাব করার জন্য)
    output_tokens: int          # আউটপুট টোকেন ব্যবহার (খরচ হিসাব করার জন্য)
    cost: float                 # এই API কলের খরচ (USD)
    cache_hit: bool             # Redis থেকে এসেছে কিনা?
    created_at: datetime        # ক্লাসিফিকেশনের সময়
    
    # সম্পর্ক
    ticket: Ticket              # এটি যে টিকেটের জন্য
```

**কেন এই ডিজাইন?**
- `ticket_id` এবং `ondelete="CASCADE"` → একটি টিকেট ডিলিট হলে এর ক্লাসিফিকেশনও ডিলিট হয়
- `unique=True` ticket_id-তে → প্রতিটি টিকেটের শুধু একটি ক্লাসিফিকেশন থাকবে
- `input_tokens`, `output_tokens`, `cost` → খরচ ট্র্যাকিংয়ের জন্য গুরুত্বপূর্ণ
- `cache_hit` → বিশ্লেষণের জন্য কতটা ক্যাশ হিট হয়েছে জানার জন্য

---

### 3️⃣ **ApiCost মডেল** (`app/models/api_cost.py`)

দৈনিক ভিত্তিতে খরচ সংগ্রহ করা হয়।

```python
class ApiCost(Base):
    __tablename__ = "api_costs"
    
    id: int                  # Primary key
    date: date              # তারিখ (unique - প্রতিদিন একটি রেকর্ড)
    total_cost: float       # সেই দিনের মোট খরচ
    request_count: int      # কতটি API কল হয়েছে
    cache_hit_count: int    # কতটি ক্যাশ থেকে সেবা দেওয়া হয়েছে
    created_at: datetime    # রেকর্ড তৈরির সময়
```

**কেন?**
- দৈনিক বাজেট ট্র্যাকিং এবং লিমিট চেক করার জন্য
- `date` এ `unique=True` → প্রতিদিন শুধু একটি রেকর্ড আপডেট হবে
- `cache_hit_count` → ক্যাশ এফেক্টিভনেস মেপার করার জন্য

---

## 🔄 ডেটা ফ্লো এবং আর্কিটেকচার

### সম্পূর্ণ প্রক্রিয়া ফ্লো:

```
┌────────────────────────────────────────────────────────────────┐
│ ১. ক্লায়েন্ট একটি নতুন টিকেট তৈরি করে (POST /tickets)          │
│    Request: {subject, description, priority}                  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ ২. FastAPI Router (app/routers/tickets.py)                     │
│    - Pydantic দ্বারা ডেটা ভ্যালিডেশন                          │
│    - Priority enum চেক করা                                     │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ ३. Database এ Ticket সংরক্ষণ                                   │
│    INSERT INTO tickets (subject, description, priority)       │
│    → ticket_id ফেরত আসে (flush ব্যবহার করে ID পাওয়া যায়)     │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ ४. ক্লাসিফিকেশন সার্ভিস শুরু হয়                               │
│    (app/services/classifier.py)                              │
│                                                                │
│    Step A: Redis cache key তৈরি করা                           │
│    - cache_key = hash(subject + description)                 │
│    - এই কীটি দ্বারা Redis এ চেক করা                           │
│                                                                │
│    Step B: যদি Cache Hit হয় (ভাগ্যবান! 🎉)                  │
│    - Redis থেকে ক্লাসিফিকেশন ডেটা পাওয়া যায়                  │
│    - Database এ সংরক্ষণ করা হয় (cache_hit=True)             │
│    - খরচ = 0 (API কল হয়নি)                                   │
│    - দিনের খরচ রেকর্ডে cache_hit_count বৃদ্ধি                 │
│                                                                │
│    Step C: যদি Cache Miss হয় (API কল দরকার)                │
│    - বাজেট চেক করা (check_cost_limit)                       │
│      যদি আজকের খরচ >= দৈনিক লিমিট, Error ফেরত               │
│    - Anthropic Claude API কল করা                            │
│      system_prompt + user_message পাঠানো                     │
│      → Claude ক্লাসিফিকেশন JSON ফেরত দেয়                     │
│                                                                │
│    Step D: Response প্রসেস করা                               │
│    - JSON parse করা এবং ভ্যালিডেট করা                         │
│    - Token গণনা করা (input_tokens, output_tokens)           │
│    - খরচ গণনা করা:                                             │
│      cost = (input_tokens/1M * $3) + (output_tokens/1M * $15)│
│    - Database এ Classification সংরক্ষণ                       │
│    - Redis এ 1 ঘণ্টার জন্য ক্যাশ করা (TTL=3600)             │
│    - দিনের খরচ রেকর্ড আপডেট করা                               │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ ५. Response ফেরত দেওয়া (Create Ticket Response)               │
│    - Ticket + Classification details                         │
│    - Client কে সম্পূর্ণ রেসপন্স পায়                             │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 কী ফিচারস এবং কেন এগুলি দরকার

### 1️⃣ **Redis Caching** - কেন এবং কিভাবে?

**সমস্যা:** প্রতিটি টিকেটের জন্য Claude API কল করলে খরচ বাড়বে এবং স্লো হবে।

**সমাধান:** অভিন্ন টিকেটের জন্য একই ক্লাসিফিকেশন ব্যবহার করা।

```python
# Hash generate করা
cache_key = hashlib.sha256(f"{subject}:{description}".encode()).hexdigest()[:16]
# "classification:a1b2c3d4e5f6g7h8"

# Redis এ 1 ঘণ্টার জন্য স্টোর করা
await redis.set(cache_key, classification_json, ex=3600)

# পরবর্তী একই টিকেট আসলে সরাসরি Redis থেকে পাওয়া যায়
cached = await redis.get(cache_key)
if cached:
    # খরচ = 0, গতি = অতি দ্রুত! ⚡
```

**সুবিধা:**
- খরচ 70-80% কমানো যায় (বাস্তব ব্যবহারে)
- প্রতিক্রিয়া সময় 10x দ্রুত
- Claude API এর লোড কমায়

---

### 2️⃣ **খরচ ট্র্যাকিং** - সীমা নির্ধারণ

**সমস্যা:** Claude API ব্যবহার করা মানে প্রতি হাজার টোকেনের জন্য অর্থ ব্যয় হয়।

**সমাধান:** প্রতিটি API কলের খরচ ট্র্যাক করা এবং দৈনিক সীমা সেট করা।

```python
def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    # Anthropic Pricing (2025):
    # Input: $3 per 1M tokens
    # Output: $15 per 1M tokens
    
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    return input_cost + output_cost

# উদাহরণ:
# 500 input tokens + 150 output tokens
# cost = (500/1M * 3) + (150/1M * 15)
#      = $0.0015 + $0.00225 = $0.00375 (কম খরচ!)
```

**বাজেট চেক:**
```python
async def check_cost_limit(db: AsyncSession) -> None:
    today = date.today()
    daily_cost = await db.execute(
        select(ApiCost).where(ApiCost.date == today)
    )
    
    if daily_cost.total_cost >= settings.daily_cost_limit:
        raise CostLimitExceededError()  # আজকের বাজেট শেষ!
```

**উপকার:**
- অপ্রত্যাশিত খরচ এড়ানো
- বাজেট পরিকল্পনা করা সহজ
- ব্যবহারকারীদের খরচ-সচেতনতা

---

### 3️⃣ **SSE Streaming** - কেন রিয়েল-টাইম পরামর্শ?

**সমস্যা:** সাজেশন জেনারেশন 2-3 সেকেন্ড লাগতে পারে। Client যদি 3 সেকেন্ড অপেক্ষা করে তাহলে খারাপ UX।

**সমাধান:** Claude API এর streaming ব্যবহার করে প্রতিটি টোকেন যেমন আসে তাই পাঠানো।

```python
async def generate_suggestion_stream(subject, description, category):
    # Streaming response
    async with client.messages.stream(...) as stream:
        async for text in stream.text_stream:
            yield text  # প্রতিটি টোকেন এক এক করে যায়
```

**Client দিক (Browser):**
```javascript
const eventSource = new EventSource(`/tickets/1/suggest`);
eventSource.onmessage = (event) => {
    console.log(event.data);  // প্রতিটি টোকেন এক এক করে দেখা যায়
    // "I understand your..."
    // "I understand your issue..."
    // "I understand your issue with..."
};
```

**ফলাফল:**
- ধারণা দেয় যে সিস্টেম কাজ করছে
- ইন্টারঅ্যাক্টিভ অভিজ্ঞতা
- পূর্ণ প্রতিক্রিয়া না হওয়া পর্যন্ত অপেক্ষা করতে হয় না

---

### 4️⃣ **রেট লিমিটিং** - সুরক্ষা

**সমস্যা:** কোন বটও যদি লক্ষ লক্ষ API কল করে দেয় তাহলে সার্ভার ক্র্যাশ হবে এবং খরচ বেড়ে যাবে।

**সমাধান:** প্রতি মিনিটে সর্বোচ্চ 20 অনুরোধ অনুমতি দেওয়া।

```python
from slowapi import Limiter

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20/minute"]  # প্রতি মিনিটে 20 রিকোয়েস্ট
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
```

**সুবিধা:**
- DDoS আক্রমণ থেকে সুরক্ষা
- ন্যায্য ব্যবহার নিশ্চিত করা
- সার্ভার রিসোর্স সুরক্ষা

---

## 🚀 স্টেপ বাই স্টেপ ইমপ্লিমেন্টেশন

### ধাপ ১: প্রজেক্ট সেটআপ

```bash
# 1. প্রজেক্ট ডিরেক্টরি তৈরি করা
mkdir project-1-ticket-classifier
cd project-1-ticket-classifier

# 2. requirements.txt তৈরি করা (উপরে দেখা ডিপেন্ডেন্সিজ)
# 3. Python virtual environment তৈরি
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 4. ডিপেন্ডেন্সিজ ইনস্টল করা
pip install -r requirements.txt
```

---

### ধাপ ২: Database সেটআপ

**`app/database.py` তৈরি:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Async database engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/ticket_classifier",
    pool_size=20,
    max_overflow=10,
)

async_session = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # সব টেবিল তৈরি
```

---

### ধাপ ৩: Database মডেল তৈরি

**`app/models/ticket.py`:**
```python
from datetime import datetime
from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        Enum(Priority),
        default=Priority.MEDIUM,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Database এ default value
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    classification: Mapped["Classification"] = relationship(
        "Classification",
        back_populates="ticket",
        uselist=False,  # শুধু একটি (One-to-One)
    )
```

**`app/models/classification.py`:**
```python
class Classification(Base):
    __tablename__ = "classifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),  # টিকেট ডিলিট হলে ক্লাস্যিফিকেশনও ডিলিট
        nullable=False,
        unique=True,  # প্রতিটি টিকেটের একটি ক্লাসিফিকেশন
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cache_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    ticket: Mapped["Ticket"] = relationship(
        "Ticket",
        back_populates="classification",
    )
```

**`app/models/api_cost.py`:**
```python
class ApiCost(Base):
    __tablename__ = "api_costs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cache_hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

---

### ধাপ ৪: Pydantic স্কিমা (Input/Output ভ্যালিডেশন)

**`app/schemas/ticket.py`:**
```python
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    """Client থেকে আসা নতুন টিকেট ডেটা"""
    subject: str = Field(
        ...,  # required
        min_length=3,
        max_length=500,
        description="টিকেটের শিরোনাম"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="বিস্তারিত বর্ণনা"
    )
    priority: Optional[str] = Field(
        default="medium",
        description="অগ্রাধিকার: low, medium, high, critical"
    )

class TicketResponse(BaseModel):
    """API থেকে ফেরত যাওয়া টিকেট ডেটা"""
    id: int
    subject: str
    description: str
    priority: str
    created_at: datetime
    updated_at: datetime
    classification: Optional[ClassificationDetail] = None
    
    model_config = {"from_attributes": True}  # SQLAlchemy মডেল থেকে অটো-ম্যাপিং
```

---

### ধাপ ৫: Redis ক্যাশিং এবং ক্লাসিফিকেশন লজিক

**`app/services/classifier.py`:**

এটি প্রজেক্টের কোর যুক্তি:

```python
import hashlib
import json
import anthropic
import redis.asyncio as aioredis

CACHE_TTL = 3600  # 1 ঘণ্টা

def _cache_key(subject: str, description: str) -> str:
    """
    টিকেটের content থেকে একটি unique hash তৈরি করা।
    যদি দুটি টিকেটের subject+description একই থাকে,
    তাহলে একই cache_key থাকবে।
    """
    content_hash = hashlib.sha256(f"{subject}:{description}".encode()).hexdigest()[:16]
    return f"classification:{content_hash}"

async def classify_ticket(
    subject: str,
    description: str,
    ticket_id: int,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> Classification:
    """
    Main classification logic with caching
    """
    
    cache_key = _cache_key(subject, description)
    
    # === STEP 1: Check Redis Cache ===
    cached = await redis.get(cache_key)
    if cached:
        logger.info("Cache hit!", extra={"ticket_id": ticket_id})
        cached_data = json.loads(cached)
        
        # Redis থেকে ডেটা আছে, সরাসরি database এ save করা
        db_classification = Classification(
            ticket_id=ticket_id,
            category=cached_data["category"],
            confidence=cached_data["confidence"],
            reasoning=cached_data["reasoning"],
            input_tokens=0,  # Cache hit - কোন API call নেই
            output_tokens=0,
            cost=0.0,
            cache_hit=True,  # চিহ্নিত করা যে এটি cache থেকে এসেছে
        )
        db.add(db_classification)
        await db.flush()
        
        # খরচ লগ করা (0, কারণ cache hit)
        await log_api_cost(db, input_tokens=0, output_tokens=0, cache_hit=True)
        
        return db_classification
    
    # === STEP 2: Check Daily Cost Limit ===
    await check_cost_limit(db)  # If limit exceeded, exception raised
    
    # === STEP 3: Call Claude API ===
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    user_message = f"Subject: {subject}\n\nDescription: {description}"
    
    response = await client.messages.create(
        model=settings.anthropic_model,  # "claude-sonnet-4-20250514"
        max_tokens=300,  # সর্বোচ্চ 300 টোকেন response
        system=CLASSIFICATION_SYSTEM_PROMPT,  # Classification এর জন্য instruction
        messages=[
            {"role": "user", "content": user_message},
        ],
    )
    
    # === STEP 4: Parse & Validate Claude's Response ===
    response_text = response.content[0].text.strip()
    # Claude JSON ফেরত দেবে, যেমন:
    # {
    #   "category": "Bug",
    #   "confidence": 0.95,
    #   "reasoning": "User describes a software error"
    # }
    
    classification_data = json.loads(response_text)
    classification = TicketClassification(**classification_data)  # Pydantic validation
    
    # === STEP 5: Calculate Cost ===
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = calculate_cost(input_tokens, output_tokens)
    
    # === STEP 6: Save to Database ===
    db_classification = Classification(
        ticket_id=ticket_id,
        category=classification.category,
        confidence=classification.confidence,
        reasoning=classification.reasoning,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        cache_hit=False,  # API থেকে এসেছে
    )
    db.add(db_classification)
    await db.flush()
    
    # === STEP 7: Cache for 1 hour ===
    cache_data = {
        "category": classification.category,
        "confidence": classification.confidence,
        "reasoning": classification.reasoning,
    }
    await redis.set(cache_key, json.dumps(cache_data), ex=CACHE_TTL)
    
    # === STEP 8: Log Cost ===
    await log_api_cost(db, input_tokens, output_tokens, cache_hit=False)
    
    logger.info(
        "Classification successful",
        extra={
            "ticket_id": ticket_id,
            "category": classification.category,
            "cost": cost,
        }
    )
    
    return db_classification
```

---

### ধাপ ৬: খরচ ট্র্যাকিং

**`app/services/cost_tracker.py`:**

```python
def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Anthropic Pricing (2025):
    - Input: $3 per 1M tokens
    - Output: $15 per 1M tokens
    """
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    return round(input_cost + output_cost, 6)

async def log_api_cost(
    db: AsyncSession,
    input_tokens: int,
    output_tokens: int,
    cache_hit: bool = False,
) -> CostInfo:
    """
    প্রতিটি API কলের cost লগ করা এবং দৈনিক aggregation আপডেট করা।
    """
    
    cost = calculate_cost(input_tokens, output_tokens) if not cache_hit else 0.0
    today = date.today()
    
    # আজকের cost রেকর্ড পাওয়া বা তৈরি করা
    result = await db.execute(
        select(ApiCost).where(ApiCost.date == today)
    )
    daily_record = result.scalar_one_or_none()
    
    if daily_record is None:
        # আজ প্রথম API কল
        daily_record = ApiCost(
            date=today,
            total_cost=cost,
            request_count=1,
            cache_hit_count=1 if cache_hit else 0,
        )
        db.add(daily_record)
    else:
        # আজ আগে API কল হয়েছে, আপডেট করা
        daily_record.total_cost += cost
        daily_record.request_count += 1
        if cache_hit:
            daily_record.cache_hit_count += 1
    
    await db.flush()
    
    logger.info(
        "API cost logged",
        extra={
            "cost": cost,
            "daily_total": daily_record.total_cost,
        }
    )
    
    return CostInfo(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        daily_total=daily_record.total_cost,
        budget_remaining=settings.daily_cost_limit - daily_record.total_cost,
    )

async def check_cost_limit(db: AsyncSession) -> None:
    """
    দৈনিক বাজেট সীমা অতিক্রম করলে exception ফেরত দেওয়া।
    """
    today = date.today()
    result = await db.execute(
        select(ApiCost).where(ApiCost.date == today)
    )
    daily_record = result.scalar_one_or_none()
    
    if daily_record and daily_record.total_cost >= settings.daily_cost_limit:
        raise CostLimitExceededError(
            daily_total=daily_record.total_cost,
            limit=settings.daily_cost_limit,
        )
```

---

### ধাপ ७: API Endpoints তৈরি

**`app/routers/tickets.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> TicketResponse:
    """
    নতুন টিকেট তৈরি করা এবং স্বয়ংক্রিয় ক্লাসিফিকেশন।
    
    Request:
    {
        "subject": "Cannot login to my account",
        "description": "I've been trying...",
        "priority": "high"
    }
    """
    
    # Priority validate করা
    priority = Priority(ticket_data.priority.lower())
    
    # Database এ Ticket সংরক্ষণ করা
    ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        priority=priority,
    )
    db.add(ticket)
    await db.flush()  # ID পাওয়ার জন্য
    
    logger.info("Ticket created", extra={"ticket_id": ticket.id})
    
    # ক্লাসিফিকেশন শুরু করা
    try:
        classification = await classify_ticket(
            subject=ticket.subject,
            description=ticket.description,
            ticket_id=ticket.id,
            db=db,
            redis=redis,
        )
    except Exception as e:
        logger.warning("Classification failed", extra={"error": str(e)})
    
    # Relationships লোড করা
    await db.refresh(ticket)
    
    return _ticket_to_response(ticket)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """
    একটি specific টিকেট পাওয়া।
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return _ticket_to_response(ticket)
```

---

### ধাপ ८: Analytics এবং রিপোর্টিং

**`app/routers/analytics.py`:**

```python
@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    """
    সমস্ত Analytics ডেটা একসাথে:
    - মোট টিকেট সংখ্যা
    - ক্যাটাগরি অনুযায়ী ভাঙ্গন
    - আত্মবিশ্বাস স্কোর
    - মাসিক খরচ সারসংক্ষেপ
    """
    
    # ১. মোট টিকেট
    total_result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_result.scalar() or 0
    
    # ২. ক্যাটাগরি breakdown
    category_query = (
        select(
            Classification.category,
            func.count(Classification.id).label("count"),
            func.avg(Classification.confidence).label("avg_confidence"),
            func.sum(Classification.cost).label("total_cost"),
        )
        .group_by(Classification.category)
        .order_by(func.count(Classification.id).desc())
    )
    category_rows = await db.execute(category_query)
    
    categories = [
        CategoryStat(
            category=row.category,
            count=row.count,
            avg_confidence=round(row.avg_confidence, 3),
            total_cost=round(row.total_cost, 4),
        )
        for row in category_rows
    ]
    
    # ३. সামগ্রিক গড় আত্মবিশ্বাস
    avg_conf_result = await db.execute(
        select(func.avg(Classification.confidence))
    )
    avg_confidence = avg_conf_result.scalar() or 0.0
    
    # ४. মাসিক খরচ সারসংক্ষেপ
    cost_summary = await get_monthly_cost_summary(db)
    
    return AnalyticsSummary(
        total_tickets=total_tickets,
        categories=categories,
        cost_summary=cost_summary,
        avg_classification_confidence=round(avg_confidence, 3),
    )
```

---

### ধাপ ९: FastAPI মূল এপ্লিকেশন সেটআপ

**`app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from contextlib import asynccontextmanager

# Lifespan: startup এবং shutdown হুক
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    logger.info("Database initialized")
    
    yield  # এপ্লিকেশন চলছে
    
    # Shutdown
    await close_db()
    await close_redis()
    logger.info("Application closed")

# FastAPI এপ্লিকেশন তৈরি
app = FastAPI(
    title="Customer Support Ticket Classifier & Suggester",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware - সব origins থেকে requests অনুমতি (production এ সীমিত করুন)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    rid = generate_request_id()
    request_id_ctx.set(rid)
    
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    logger.info(
        "Request completed",
        extra={
            "request_id": rid,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    
    return response

# Routers mount করা
app.include_router(tickets.router)
app.include_router(analytics.router)
app.include_router(health.router)
```

---

## 🏗️ সম্পূর্ণ আর্কিটেকচার ডায়াগ্রাম

```
                    ┌─────────────────────────────────┐
                    │      Client/Frontend            │
                    │  (Mobile/Web App/Curl/API)      │
                    └──────────────┬────────────────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  │                                  │
            POST /tickets                     GET /tickets/{id}
         (Create Ticket)                   (Get Details)
                  │                                  │
                  ▼                                  ▼
        ┌─────────────────────────────────────────────────────┐
        │            FastAPI Server (app/main.py)             │
        │                                                      │
        │  ┌──────────────────────────────────────────────┐   │
        │  │ Middleware:                                  │   │
        │  │ - CORS (allow cross-origin)                  │   │
        │  │ - Rate Limiting (20/minute)                  │   │
        │  │ - Request Logging (structured JSON)          │   │
        │  │ - Error Handling (custom exceptions)         │   │
        │  └──────────────────────────────────────────────┘   │
        │                                                      │
        │  ┌─── Routers/Endpoints ──────────────────────────┐  │
        │  │                                                │  │
        │  │ POST /tickets → tickets.create_ticket()       │  │
        │  │   ├─ Pydantic ভ্যালিডেশন                      │  │
        │  │   ├─ Database save করা                        │  │
        │  │   ├─ classifier.classify_ticket() কল          │  │
        │  │   │   ├─ Redis cache check                    │  │
        │  │   │   ├─ cost_limit check                     │  │
        │  │   │   ├─ Claude API call                      │  │
        │  │   │   ├─ Response parse & validate            │  │
        │  │   │   ├─ Database save                        │  │
        │  │   │   └─ Redis cache save (1 hour TTL)        │  │
        │  │   └─ cost_tracker.log_api_cost() কল          │  │
        │  │       ├─ খরচ গণনা                            │  │
        │  │       └─ দৈনিক aggregation আপডেট            │  │
        │  │                                                │  │
        │  │ GET /analytics/summary → analytics.summary()  │  │
        │  │   ├─ Total tickets count                      │  │
        │  │   ├─ Category breakdown with aggregations     │  │
        │  │   └─ Monthly cost summary                     │  │
        │  │                                                │  │
        │  └────────────────────────────────────────────────┘  │
        │                                                      │
        └──────────┬──────────────┬──────────────┬─────────────┘
                   │              │              │
                   ▼              ▼              ▼
        ┌──────────────────┐  ┌─────────────┐  ┌──────────────┐
        │   PostgreSQL     │  │    Redis    │  │ Anthropic    │
        │   Database       │  │   Cache     │  │ Claude API   │
        │                  │  │             │  │              │
        │ ┌──────────────┐ │  │ String KV   │  │ POST /msg    │
        │ │ tickets      │ │  │ Store       │  │ classification│
        │ ├──────────────┤ │  │             │  │ & suggester  │
        │ │ classific.   │ │  │ TTL=3600s   │  │ streaming    │
        │ ├──────────────┤ │  │ (1 hour)    │  │              │
        │ │ api_costs    │ │  │             │  └──────────────┘
        │ └──────────────┘ │  └─────────────┘
        │                  │
        │ Async +          │  Hash(subject+
        │ Connection       │  description) →
        │ Pool (20-30)     │  Cache Key
        │                  │
        └──────────────────┘

                   ▲
                   │
        ┌──────────┴──────────┐
        │  docker-compose.yml │
        │  (Production-ready) │
        │                     │
        │ - PostgreSQL        │
        │ - Redis             │
        │ - FastAPI (Uvicorn) │
        │ - Environment vars  │
        └─────────────────────┘
```

---

## 🔄 ডেটা ট্রান্সফর্ম এবং ফ্লো

### Ticket তৈরির সম্পূর্ণ ফ্লো:

```
Client Request:
───────────────
POST /tickets
{
  "subject": "Login button not working",
  "description": "When I click the login button, nothing happens...",
  "priority": "high"
}

                    ↓ (Pydantic Validation)

Validated Data:
──────────────
TicketCreate(
  subject="Login button not working",
  description="When I click the login button, nothing happens...",
  priority="high"
)

                    ↓ (Database Insert)

Database Row (tickets table):
──────────────────────────────
id: 1
subject: "Login button not working"
description: "When I click the login button, nothing happens..."
priority: "high"
created_at: 2025-05-04 10:30:00+00:00
updated_at: 2025-05-04 10:30:00+00:00

                    ↓ (Classification Logic)

Cache Key Generation:
─────────────────────
SHA256("Login button not working:When I click...") → "a1b2c3d4e5f6g7h8"
Redis Key: "classification:a1b2c3d4e5f6g7h8"

Check Redis:
─────────────
await redis.get("classification:a1b2c3d4e5f6g7h8") → NULL (Miss)

Cost Limit Check:
─────────────────
SELECT * FROM api_costs WHERE date = TODAY
→ daily_total = $5.20 (< $10 limit) ✅

Claude API Call:
────────────────
request:
{
  "model": "claude-sonnet-4-20250514",
  "system": "You are an expert customer support ticket classifier...",
  "messages": [{
    "role": "user",
    "content": "Subject: Login button not working\n\nDescription: When I click..."
  }],
  "max_tokens": 300
}

response (streaming):
{
  "content": [{
    "text": "{\"category\": \"Bug\", \"confidence\": 0.98, \"reasoning\": \"User reports a non-functional button (software defect)\"}"
  }],
  "usage": {
    "input_tokens": 450,
    "output_tokens": 65
  }
}

                    ↓ (Parse & Calculate Cost)

Parsed Classification:
──────────────────────
TicketClassification(
  category="Bug",
  confidence=0.98,
  reasoning="User reports a non-functional button (software defect)"
)

Cost Calculation:
─────────────────
input_cost = (450 / 1_000_000) * 3.00 = $0.00135
output_cost = (65 / 1_000_000) * 15.00 = $0.000975
total_cost = $0.001325 ≈ $0.00 (মাত্র কয়েক মিলি সেন্ট!)

                    ↓ (Save to Database)

Database Row (classifications table):
──────────────────────────────────────
id: 1
ticket_id: 1
category: "Bug"
confidence: 0.98
reasoning: "User reports a non-functional button (software defect)"
input_tokens: 450
output_tokens: 65
cost: 0.001325
cache_hit: false
created_at: 2025-05-04 10:30:02+00:00

Update api_costs:
─────────────────
UPDATE api_costs 
SET total_cost = 5.20135, request_count = 6 
WHERE date = TODAY

                    ↓ (Cache for 1 hour)

Redis Set:
──────────
SET classification:a1b2c3d4e5f6g7h8 
'{
  "category": "Bug",
  "confidence": 0.98,
  "reasoning": "User reports..."
}' 
EX 3600

                    ↓ (API Response)

API Response (200 Created):
──────────────────────────
{
  "id": 1,
  "subject": "Login button not working",
  "description": "When I click...",
  "priority": "high",
  "created_at": "2025-05-04T10:30:00+00:00",
  "updated_at": "2025-05-04T10:30:00+00:00",
  "classification": {
    "category": "Bug",
    "confidence": 0.98,
    "reasoning": "User reports...",
    "cache_hit": false,
    "created_at": "2025-05-04T10:30:02+00:00"
  }
}
```

---

## 📊 Analytics Example

যদি 100টি টিকেট প্রসেস করা হয়েছে:

```
Request:
GET /analytics/summary

Response:
{
  "total_tickets": 100,
  "categories": [
    {
      "category": "Bug",
      "count": 45,
      "avg_confidence": 0.92,
      "total_cost": 0.08
    },
    {
      "category": "Feature Request",
      "count": 30,
      "avg_confidence": 0.85,
      "total_cost": 0.05
    },
    {
      "category": "Billing",
      "count": 15,
      "avg_confidence": 0.88,
      "total_cost": 0.03
    },
    {
      "category": "General Inquiry",
      "count": 8,
      "avg_confidence": 0.90,
      "total_cost": 0.02
    },
    {
      "category": "Urgent",
      "count": 2,
      "avg_confidence": 0.95,
      "total_cost": 0.01
    }
  ],
  "cost_summary": {
    "total_cost": 0.19,
    "total_requests": 100,
    "total_cache_hits": 35,           # 35% cache hit rate!
    "cache_hit_rate": 0.35,
    "avg_cost_per_request": 0.00190   # মাত্র $0.0019 প্রতি টিকেট!
  },
  "avg_classification_confidence": 0.90
}
```

---

## ✅ সারসংক্ষেপ: এই প্রজেক্ট কেন গুরুত্বপূর্ণ

| বৈশিষ্ট্য | উপকার | বাস্তব ব্যবহার |
|---------|-------|-------------|
| **AI Classification** | স্বয়ংক্রিয় রাউটিং | সাপোর্ট টিকেটগুলি সঠিক দলে যায় |
| **Redis Caching** | 70-80% খরচ সাশ্রয় | একই সমস্যা বারবার আসলে শুধু lookup |
| **Cost Tracking** | বাজেট নিয়ন্ত্রণ | API খরচ সীমা অতিক্রম করা যায় না |
| **SSE Streaming** | ভাল UX | ব্যবহারকারীরা রিয়েল-টাইমে সাজেশন দেখে |
| **Rate Limiting** | নিরাপত্তা | DDoS আক্রমণ এবং অপব্যবহার প্রতিরোধ |
| **Async/Await** | উচ্চ কর্মক্ষমতা | 10,000+ একযোগে অনুরোধ সামলাতে পারে |
| **Structured Logging** | ডিবাগিং | প্রতিটি লেনদেন ট্র্যাক করা যায়, সমস্যা খুঁজে পাওয়া সহজ |

---

এই প্রজেক্টটি একটি **উৎপাদন-প্রস্তুত, স্কেলযোগ্য সিস্টেম** যা দেখায় কিভাবে:
- ✅ আধুনিক Python ওয়েব সার্ভার তৈরি করতে হয়
- ✅ AI API ইন্টিগ্রেশন করতে হয়
- ✅ খরচ এবং পারফরম্যান্স ম্যানেজ করতে হয়
- ✅ প্রোডাকশন-গ্রেড কোড লিখতে হয়

**হ্যাপি কোডিং!** 🚀
