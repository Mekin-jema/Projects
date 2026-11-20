# 🤖 AI Financial Agent - Complete Project Documentation

> An intelligent financial research assistant powered by AI that provides real-time stock analysis, financial metrics, and investment insights through a modern chat interface.

---

## 📑 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Key Features](#key-features)
6. [Setup & Installation](#setup--installation)
7. [Core Components](#core-components)
8. [API Integration](#api-integration)
9. [Database Schema](#database-schema)
10. [Authentication Flow](#authentication-flow)
11. [AI Integration](#ai-integration)
12. [Development Workflow](#development-workflow)
13. [Deployment](#deployment)

---

## 🎯 Quick Overview

**AI Financial Agent** is an educational proof-of-concept that combines modern web technologies with AI/LLM capabilities to provide intelligent financial research and stock analysis. Think of it as a ChatGPT-like interface specifically trained for financial data.

### What it does:
- 💬 Chat-based financial research interface
- 📊 Real-time stock prices and historical data
- 📈 Financial statements (income, balance sheets, cash flow)
- 🔍 Stock screening and filtering
- 📰 News aggregation for companies
- 🎨 Generative UI that displays charts and tables on the fly
- 🔐 User authentication with session management

### Who it's for:
- Students learning about AI and finance
- Developers wanting to learn about LLM integration
- Researchers exploring AI in fintech
- **NOT for real trading** (educational only!)

---

## 🏗️ Tech Stack

### Frontend
- **Next.js 15** - React framework with server-side rendering
- **React 18** - UI components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component library
- **CodeMirror** - Code editor with syntax highlighting
- **Recharts** - Data visualization
- **ProseMirror** - Rich text editor

### Backend
- **Next.js API Routes** - Serverless functions
- **Node.js** - Runtime environment
- **Drizzle ORM** - Database management
- **PostgreSQL** - Primary database (via Vercel Postgres)

### AI & LLM
- **Vercel AI SDK** - Unified AI API interface
- **OpenAI GPT** - LLM provider
- **LangSmith** - LLM monitoring and debugging

### Authentication & Security
- **NextAuth.js 5** - Authentication framework
- **Bcrypt** - Password hashing
- **Fingerprinting** - Anonymous user tracking

### Data & APIs
- **Financial Datasets API** - Stock data, fundamentals, news
- **Vercel Blob** - File storage
- **Vercel Postgres** - Database hosting

### DevOps & Build
- **pnpm** - Fast package manager
- **Turbopack** - Next.js bundler
- **Biome** - Linting and formatting
- **TypeScript** - Compilation

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface (React)                │
│  Chat Component → Message Display → Financial Tables    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Next.js API Routes (Backend)                │
│  • Message Handling  • Chat History  • API Proxy         │
└──────────────────────┬──────────────────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
┌─────▼────┐    ┌──────▼──────┐  ┌────▼──────┐
│  OpenAI  │    │  Financial  │  │ PostgreSQL│
│   GPT    │    │  Datasets   │  │ Database  │
│  (LLM)   │    │   API       │  │           │
└──────────┘    └─────────────┘  └───────────┘
```

### Data Flow:
1. **User Input** → Chat interface captures user message
2. **API Call** → Request sent to Next.js API route
3. **AI Processing** → LLM processes message with tools
4. **Tool Execution** → Financial tools fetch external data
5. **Data Aggregation** → Results combined and formatted
6. **Response Stream** → Data streamed back to UI
7. **Database** → Messages and chat history saved

---

## 📁 Project Structure

```
ai-financial-agent/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication routes
│   │   ├── auth.ts              # NextAuth configuration
│   │   ├── auth.config.ts       # Auth settings
│   │   ├── actions.ts           # Auth server actions
│   │   ├── login/               # Login page
│   │   ├── register/            # Registration page
│   │   └── api/                 # Auth API endpoints
│   │
│   ├── (chat)/                   # Chat application routes
│   │   ├── page.tsx             # Main chat page
│   │   ├── layout.tsx           # Chat layout
│   │   ├── actions.ts           # Chat server actions
│   │   ├── chat/[id]/           # Individual chat view
│   │   ├── api/                 # Chat APIs
│   │   │   ├── chat/            # Message streaming
│   │   │   └── history/         # Chat history
│   │   └── components/          # Chat-specific components
│   │
│   ├── api/                      # Global API routes
│   │   └── auth/                # Auth endpoints
│   │
│   ├── layout.tsx               # Root layout
│   └── globals.css              # Global styles
│
├── components/                   # React Components
│   ├── chat.tsx                 # Main chat interface
│   ├── message.tsx              # Message display
│   ├── message-actions.tsx      # Message controls
│   ├── block.tsx                # Generative UI blocks
│   ├── code-block.tsx           # Code display
│   ├── auth-form.tsx            # Authentication form
│   ├── sidebar.tsx              # Navigation sidebar
│   ├── model-selector.tsx       # AI model selection
│   │
│   ├── financial-tables/        # Financial data components
│   │   ├── income-statements-table.tsx
│   │   ├── balance-sheets-table.tsx
│   │   ├── cash-flow-statements-table.tsx
│   │   ├── financial-metrics-table.tsx
│   │   └── stock-screener-table.tsx
│   │
│   ├── ui/                      # Radix UI components
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   ├── stock-chart.tsx
│   │   └── ...
│   │
│   └── styles/                  # Styling utilities
│       └── colors.ts
│
├── hooks/                        # React Hooks
│   ├── use-chat-visibility.ts   # Visibility state management
│   ├── use-block.ts             # Block state management
│   ├── use-mobile.tsx           # Mobile detection
│   ├── use-tool-loading.ts      # Tool execution state
│   └── use-query-loading.ts     # Query state
│
├── lib/                          # Utilities & Core Logic
│   ├── ai/                      # AI/LLM Integration
│   │   ├── index.ts             # Custom model wrapper
│   │   ├── models.ts            # Available LLM models
│   │   ├── prompts.ts           # System prompts
│   │   ├── custom-middleware.ts # LLM middleware
│   │   └── tools/
│   │       └── financial-tools.ts  # Financial tools for LLM
│   │
│   ├── db/                      # Database
│   │   ├── schema.ts            # Drizzle schema
│   │   ├── queries.ts           # Database queries
│   │   ├── api-keys.ts          # API key management
│   │   ├── migrate.ts           # Migration runner
│   │   └── migrations/          # SQL migrations
│   │
│   ├── api/                     # External API clients
│   │   └── stock-filters.ts     # Stock filtering logic
│   │
│   ├── types/                   # TypeScript types
│   ├── utils/                   # Utility functions
│   └── editor/                  # Editor utilities
│
├── public/                       # Static assets
│   ├── fonts/
│   └── images/
│
├── Configuration Files
│   ├── next.config.ts           # Next.js configuration
│   ├── tsconfig.json            # TypeScript config
│   ├── tailwind.config.ts       # Tailwind CSS config
│   ├── drizzle.config.ts        # Drizzle ORM config
│   ├── biome.jsonc              # Code linting/formatting
│   ├── middleware.ts            # Global middleware
│   ├── instrumentation.ts       # Monitoring setup
│   └── package.json             # Dependencies
```

---

## ✨ Key Features

### 1. **Chat Interface**
- Real-time message streaming
- Message editing and deletion
- Chat history preservation
- Visibility controls (private/public)
- User authentication

### 2. **Financial Data Tools**
```typescript
Available tools the AI can use:
- getStockPrices()           // Current & historical prices
- getIncomeStatements()      // Revenue, expenses, profit
- getBalanceSheets()         // Assets, liabilities, equity
- getCashFlowStatements()    // Cash movement analysis
- getFinancialMetrics()      // Ratios and metrics
- searchStocksByFilters()    // Stock screening
- getNews()                  // Company news & events
```

### 3. **Generative UI**
- Dynamic financial tables
- Interactive charts (via Recharts)
- Code blocks with syntax highlighting
- Markdown rendering
- Rich text editing

### 4. **Database Features**
- Persistent chat history
- Message versioning
- User session management
- API key storage
- Rate limiting capabilities

### 5. **Authentication**
- Passwordless authentication via fingerprinting
- Anonymous user support
- Session management
- Secure cookies

### 6. **AI Capabilities**
- GPT-4 powered responses
- Tool-calling for financial data
- Streaming responses
- Context-aware conversations

---

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+ 
- pnpm (npm install -g pnpm)
- PostgreSQL database (local or Vercel Postgres)
- OpenAI API key
- Financial Datasets API key

### Step 1: Clone & Install
```bash
git clone https://github.com/virattt/ai-financial-agent.git
cd ai-financial-agent
pnpm install
```

### Step 2: Environment Setup
Create `.env.local`:
```bash
# OpenAI
OPENAI_API_KEY=sk_test_...

# Financial Data
FINANCIAL_DATASETS_API_KEY=your_api_key

# Database (Vercel Postgres)
POSTGRES_PRISMA_URL=postgresql://...

# Auth
NEXTAUTH_SECRET=generate_random_string
NEXTAUTH_URL=http://localhost:3000

# Vercel Services (Optional)
BLOB_READ_WRITE_TOKEN=...
```

### Step 3: Database Setup
```bash
# Generate migrations
pnpm run db:generate

# Run migrations
pnpm run db:migrate

# Or push to database
pnpm run db:push

# View database (optional)
pnpm run db:studio
```

### Step 4: Start Development
```bash
pnpm run dev
```

Visit `http://localhost:3000` in your browser.

### Build for Production
```bash
pnpm run build
pnpm start
```

---

## 🎨 Core Components

### Chat Component (`components/chat.tsx`)
- Main chat interface container
- Manages message display and input
- Handles message streaming
- Integrates with sidebar

```typescript
<Chat
  id={chatId}
  initialMessages={messages}
  selectedModelId={modelId}
  selectedVisibilityType="private"
  isReadonly={false}
/>
```

### Message Component (`components/message.tsx`)
- Displays individual messages
- Shows user/assistant messages differently
- Renders markdown
- Handles message actions

### Block Component (`components/block.tsx`)
- Generative UI blocks
- Renders different content types
- Code blocks, tables, charts
- Handles tool-generated content

### Financial Tables
- **Income Statements Table**: Revenue, expenses, net income
- **Balance Sheets Table**: Assets, liabilities, equity
- **Cash Flow Table**: Operating, investing, financing activities
- **Financial Metrics Table**: Ratios and key metrics
- **Stock Screener Table**: Filtered stock results

### UI Components (Radix UI)
Accessible, unstyled components:
- Button, Input, Dialog, Select
- Table, Card, Separator, Tooltip
- Dropdown Menu, Alert Dialog

---

## 🔌 API Integration

### External APIs Used

#### 1. Financial Datasets API
```typescript
Base URL: https://api.financialdatasets.ai

Endpoints:
GET /prices/snapshot?ticker={ticker}
  → Current stock price and market cap

GET /prices/?ticker={ticker}&start_date={date}&end_date={date}
  → Historical price data

GET /financials/income-statements/?ticker={ticker}&period={period}
  → Income statement data

GET /financials/balance-sheets/?ticker={ticker}
  → Balance sheet data

GET /financials/cash-flow-statements/?ticker={ticker}
  → Cash flow data

GET /news/?ticker={ticker}&limit={limit}
  → Company news articles

Authentication: X-API-Key header
```

#### 2. OpenAI API
```typescript
Used via @ai-sdk/openai

Models Available:
- gpt-4o              // Primary model
- gpt-4.1-mini-2025-04-14  // Lightweight model

Capabilities:
- Chat completions with tool calling
- Streaming responses
- System prompts
```

### Next.js API Routes

**Chat Streaming** (`app/(chat)/api/chat/route.ts`)
```typescript
POST /api/chat
Body: {
  id: string
  messages: CoreMessage[]
  modelId: string
}

Returns: ReadableStream of messages
```

**Chat History** (`app/(chat)/api/history/route.ts`)
```typescript
GET /api/history/{id}
  → Get messages for a chat

DELETE /api/history/{id}
  → Delete messages
```

---

## 🗄️ Database Schema

### Key Tables (Drizzle ORM)

#### `users` Table
```typescript
{
  id: string              // UUID
  email: string          // Unique
  password: string       // Hashed
  createdAt: timestamp
}
```

#### `chats` Table
```typescript
{
  id: string              // UUID
  userId: string          // FK to users
  title: string          // Auto-generated
  createdAt: timestamp
  updatedAt: timestamp
  visibility: string     // 'private' | 'public'
}
```

#### `messages` Table
```typescript
{
  id: string              // UUID
  chatId: string          // FK to chats
  role: string           // 'user' | 'assistant'
  content: string        // Message text
  createdAt: timestamp
  updatedAt: timestamp
}
```

#### `api_keys` Table
```typescript
{
  id: string              // UUID
  userId: string          // FK to users
  key: string            // Encrypted API key
  provider: string       // 'openai', 'financial-datasets'
  createdAt: timestamp
}
```

---

## 🔐 Authentication Flow

### Passwordless Authentication
```
User visits app
    ↓
Check for existing fingerprint cookie
    ↓
No fingerprint? Generate random hex string
    ↓
Create auto-generated email: user-{fingerprint}@auto.generated
    ↓
Query database for user with that email
    ↓
User exists? → Log them in
User not exist? → Create new user account
    ↓
Set JWT session token
    ↓
User is authenticated ✓
```

### Why Fingerprinting?
- Enables anonymous authentication
- No password required
- Persistent user identity across sessions
- Simple implementation for educational purposes

### NextAuth.js 5 Setup
```typescript
// Custom credentials provider
Credentials({
  authorize: async (credentials, req) => {
    // Get or create fingerprint
    // Find or create user
    // Return user object
  }
})
```

---

## 🧠 AI Integration

### How the AI Works

#### 1. System Prompt
```
You are a financial research assistant.
Analyze company data objectively.
Use provided tools to fetch financial information.
Format responses clearly with key insights.
```

#### 2. Tool Calling Flow
```
User: "Tell me about Apple's revenue"
    ↓
LLM: "I'll get Apple's income statement"
    ↓
Execute: getIncomeStatements({ ticker: "AAPL" })
    ↓
Financial API: Returns income statement data
    ↓
LLM: Analyzes data and generates response
    ↓
Response: "Apple's revenue is $X billion..."
```

#### 3. Streaming Architecture
```typescript
// Using AI SDK streaming
const response = streamText({
  model: customModel('gpt-4o', apiKey),
  system: systemPrompt,
  messages: conversationHistory,
  tools: financialTools,
  temperature: 0.7,
  maxTokens: 2000,
});

// Stream back to client
return response.toDataStreamResponse();
```

#### 4. Middleware
```typescript
// Custom middleware intercepts LLM calls
- Logs prompts and responses
- Validates tool calls
- Caches duplicate requests
- Formats output for streaming
```

### Model Configuration
```typescript
// Available Models
const models = [
  { id: 'gpt-4o', label: 'GPT-4 Optimized' },
  { id: 'gpt-4.1-mini-2025-04-14', label: 'GPT-4 Mini' },
]

// Custom wrapper
const customModel = (modelId, apiKey) => {
  const provider = createOpenAI({ apiKey });
  return wrapLanguageModel({
    model: provider.chat(modelId),
    middleware: customMiddleware,
  });
};
```

---

## 💻 Development Workflow

### Running the Project
```bash
# Development (with Turbopack)
pnpm run dev

# Production build
pnpm run build

# Start production server
pnpm start

# Run tests (if configured)
pnpm test
```

### Code Quality
```bash
# Lint files
pnpm run lint

# Auto-fix lint errors
pnpm lint:fix

# Format code
pnpm format
```

### Database Management
```bash
# Generate migration from schema
pnpm run db:generate

# Run pending migrations
pnpm run db:migrate

# Open Drizzle Studio GUI
pnpm run db:studio

# Push changes to database
pnpm run db:push

# Pull schema from database
pnpm run db:pull
```

### File Organization
- **Server Components** end with `.tsx` in `app/` directory
- **Client Components** use `'use client'` directive
- **Server Actions** use `'use server'` directive
- **Custom Hooks** in `hooks/` directory
- **Utilities** in `lib/utils/`, `lib/api/`, `lib/db/`

### Environment Variables
```bash
# Required
OPENAI_API_KEY
FINANCIAL_DATASETS_API_KEY
POSTGRES_PRISMA_URL
NEXTAUTH_SECRET

# Optional
VERCEL_BLOB_TOKEN
NODE_ENV
NEXT_PUBLIC_SITE_URL
```

---

## 🚀 Deployment

### Deploy to Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Deployment Checklist
- [ ] Environment variables set in hosting platform
- [ ] Database migrations run
- [ ] Build completes successfully
- [ ] Test chat functionality
- [ ] Test authentication
- [ ] Monitor logs for errors

### Production Optimizations
```typescript
// next.config.ts
experimental: {
  ppr: true,  // Partial Prerendering
}

// Image optimization
images: {
  remotePatterns: [{
    protocol: 'https',
    hostname: '**',
  }],
}
```

### Monitoring
- **LangSmith**: Monitor LLM calls and performance
- **Vercel Analytics**: Track user metrics
- **OpenTelemetry**: Distributed tracing
- **Database**: Monitor Postgres connections

---

## 📊 Performance Tips

### Frontend
- Use React Server Components for data fetching
- Implement proper loading states
- Stream responses instead of waiting
- Cache API responses with SWR

### Backend
- Dedup duplicate tool calls
- Use connection pooling for database
- Cache model responses when appropriate
- Optimize prompts for token usage

### Database
- Add indexes on frequently queried fields
- Archive old messages periodically
- Monitor connection pool usage
- Use read replicas for analytics

---

## 🐛 Debugging

### Enable Debug Logs
```bash
# Add to .env.local
DEBUG=*

# Or specific modules
DEBUG=ai:*
DEBUG=db:*
```

### Common Issues

**Issue**: "OPENAI_API_KEY not found"
- Check `.env.local` file exists
- Verify API key is correct
- Restart dev server

**Issue**: "Database connection failed"
- Check `POSTGRES_PRISMA_URL`
- Ensure database is running
- Run migrations: `pnpm run db:migrate`

**Issue**: "Tool call returned null"
- Check API keys for Financial Datasets
- Verify ticker symbol is valid
- Check rate limits

### Useful Commands
```bash
# Check TypeScript errors
npx tsc --noEmit

# Run linter
pnpm lint

# Open database GUI
pnpm run db:studio
```

---

## 📚 Learning Resources

### For Understanding the Project
1. **Next.js Documentation**: https://nextjs.org/docs
2. **AI SDK Docs**: https://sdk.vercel.ai/docs
3. **Drizzle ORM**: https://orm.drizzle.team
4. **NextAuth.js**: https://authjs.dev
5. **Tailwind CSS**: https://tailwindcss.com

### Key Concepts
- **Server Components**: Render on server, send HTML to client
- **API Routes**: Serverless functions at `/api/*`
- **Streaming**: Send data progressively instead of all at once
- **Tool Calling**: LLM can invoke functions to get real data
- **Generative UI**: Generate React components based on LLM output

---

## 🎓 Educational Value

This project demonstrates:
1. ✅ LLM Integration patterns
2. ✅ Real-time data streaming
3. ✅ Full-stack TypeScript development
4. ✅ Database design and ORM usage
5. ✅ Authentication flows
6. ✅ API integration
7. ✅ Modern React patterns (Server Components)
8. ✅ Financial data processing
9. ✅ Generative UI concepts
10. ✅ Production deployment

---

## ⚠️ Important Disclaimers

### Educational Use Only
- This is a **proof-of-concept** for learning purposes
- **NOT** intended for real trading or investment decisions
- Past performance ≠ future results
- No warranties or guarantees provided
- Always consult a financial advisor

### Financial Responsibility
- Use simulated data only
- Don't risk real money
- Understand the risks
- Creator assumes no liability

---

## 🤝 Contributing

To improve this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 Summary

**AI Financial Agent** is a complete, production-ready application that combines:
- Modern React and Next.js
- LLM AI integration with GPT-4
- Real financial data APIs
- Full authentication system
- Professional UI/UX
- Streaming architecture
- Database persistence

It's perfect for learning how to build AI-powered applications while exploring the intersection of AI and finance.

**Happy coding! 🚀**

---

*Last Updated: 2025 | Educational Purpose | Not for Trading*
