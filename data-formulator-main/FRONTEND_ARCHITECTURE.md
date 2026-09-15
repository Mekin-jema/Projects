# Data Formulator Frontend Architecture Guide

**Document Version:** 1.0  
**Last Updated:** 2026-09-01  
**Technology Stack:** React 18 + TypeScript + Redux + Material-UI + Vite

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Build & Development](#build--development)
4. [Entry Point & Initialization](#entry-point--initialization)
5. [Redux State Management](#redux-state-management)
6. [API Client & Communication](#api-client--communication)
7. [Data Types & Semantics](#data-types--semantics)
8. [View Components & Layout](#view-components--layout)
9. [Internationalization (i18n)](#internationalization-i18n)
10. [Styling & Theming](#styling--theming)
11. [Data Flow Patterns](#data-flow-patterns)
12. [Component Hierarchy](#component-hierarchy)
13. [Key Concepts & Data Structures](#key-concepts--data-structures)

---

## Overview

**Data Formulator** is an AI-powered data visualization and exploration platform. The frontend is a React/TypeScript single-page application that:

- **Accepts user input** (data uploads, questions, interactions)
- **Communicates with backend** via REST APIs and Server-Sent Events (SSE) for real-time streaming
- **Manages complex state** with Redux (charts, tables, threads, agent messages)
- **Renders visualizations** using Flint semantic language + Vega-Lite
- **Supports i18n** (English, Chinese)
- **Provides flexible layouts** with responsive design

**Key Features:**
- Chart synthesis via LLM agents
- Multi-threaded analysis (branching alternative paths)
- Semantic table metadata (ID, Measure, Date, Region, Ordinal)
- Connector-based data loading (SQL, Cloud, APIs, Files, Paste)
- Workspace persistence (local filesystem or Azure Blob)
- Report generation with Tiptap editor

---

## Directory Structure

### `/src` - Main Source Directory

```
src/
├── index.tsx              # React entry point, Redux Provider, PersistGate
├── index.css              # Global styles, CSS variables, design tokens
├── types.d.ts             # TypeScript module declarations (PNG, SVG, SCSS, CSS, prettier, vm-browserify)
├── mui.d.ts               # Material-UI type extensions
├── icons.tsx              # Icon components (re-exports from @mui/icons-material)
├── App.tsx                # Root component (in app/ directory - see below)
│
├── app/                   # Redux, configuration, and core app logic
│   ├── store.ts           # Redux store + persistor configuration
│   ├── dfSlice.tsx        # Main Redux slice (state, actions, selectors, thunks)
│   ├── App.tsx            # Root component with routing, theme, auth
│   ├── AuthButton.tsx     # Authentication UI (login/logout)
│   ├── OidcCallback.tsx   # OIDC authentication callback handler
│   ├── oidcConfig.ts      # OIDC provider configuration
│   ├── IdentityMigrationDialog.tsx  # User identity migration UI
│   ├── apiClient.ts       # Unified API request client with error handling
│   ├── identity.ts        # Identity management (browser ID, auth types)
│   ├── utils.tsx          # Utility functions (URL building, fetch with identity, triggers)
│   ├── tableThunks.ts     # Async thunks for table operations
│   ├── tableResolution.ts # Table preview materialization
│   ├── workspaceService.ts # Workspace CRUD operations
│   ├── workspaceDB.ts     # Local workspace database
│   ├── agentInteractionPolicy.ts # Policy for agent interactions
│   ├── intentClassifier.ts # Intent classification from user input
│   ├── tokens.ts          # Design tokens (colors, spacing, typography)
│   ├── layout.ts          # Layout constants (min width, max columns, etc.)
│   ├── LayoutProvider.tsx # Context for responsive layout management
│   ├── restyle.ts         # Theme restyle utilities
│   ├── stateMigrations.ts # Redux state migration logic (version upgrades)
│   ├── errorHandler.ts    # Global error handling
│   ├── errorCodes.ts      # Error code enumeration
│   ├── clarification.ts   # Agent clarification questions handling
│   ├── chartCache.ts      # Module-scoped chart thumbnail cache
│   ├── chartRecommendation.ts # Chart recommendation logic
│   ├── displayRowsCache.ts    # Display rows (preview data) caching
│   ├── inputTablePreviewCache.ts # Input table preview materialization
│   ├── connectorFormPersistence.ts # Connector form field persistence
│   ├── connectorNames.ts  # Connector name formatting
│   ├── useAutoSave.tsx    # Hook for auto-saving workspace
│   ├── useWorkspaceAutoName.tsx # Hook for auto-naming workspaces
│   ├── useDataRefresh.tsx # Hook for data refresh logic
│   ├── useKnowledgeStore.ts # Hook for knowledge base integration
│   ├── loadableState.ts   # Loadable state helpers
│   └── identity.ts        # Browser identity generation
│
├── data/                  # Data types and utilities
│   ├── types.ts           # Type system (Type enum, coercion, testing, Vega-Lite mapping)
│   ├── column.ts          # Column class (array-based column storage)
│   ├── table.ts           # ColumnTable class (column-oriented table representation)
│   └── utils.ts           # Data transformation utilities:
│       ├── readFileText   # Read CSV/JSON files (UTF-8 + GBK fallback)
│       ├── createTableFromText    # Parse text → DictTable
│       ├── createTableFromFromObjectArray # JS objects → DictTable
│       ├── inferTypeFromValueArray # Type inference for columns
│       └── refineTemporalType     # DateTime/Date/Time refinement
│
├── api/                   # API clients (extends app/apiClient.ts)
│   └── knowledgeApi.ts    # Knowledge base API wrapper
│
├── components/            # Reusable React components
│   ├── ComponentType.tsx   # 49 types and interfaces (Chart, Field, Table, Message, etc.)
│   ├── ChartTemplates.tsx  # Chart type definitions and channel mapping
│   ├── DndTypes.ts        # Drag-and-drop type definitions
│   ├── AnvilLoader.tsx    # Anvil no-code integration component
│   ├── CatalogTree.tsx    # Virtualized tree view for data catalog
│   ├── VirtualizedCatalogTree.tsx # Optimized version with react-virtuoso
│   ├── ConnectorFormCard.tsx # Data connector configuration form
│   ├── ConnectorTablePreview.tsx # Preview data from connector
│   ├── DataOperationCard.tsx # Data cleaning/transformation card
│   ├── LoadPlanCard.tsx    # Load plan visualization
│   ├── MarkdownEditor.tsx  # Editor for markdown content
│   ├── ResizeHandle.tsx    # Splitter resize handle
│   ├── RotatingTextBlock.tsx # Animated text rotation
│   ├── ScrollFade.tsx      # Fade effect at scroll edges
│   ├── TablePreviewRow.tsx # Table row preview component
│   ├── FunComponents.tsx   # Utility components (containers, badges, etc.)
│   ├── filterFormat.ts     # Filter formatting utilities
│   └── ComponentType.tsx   # Type definitions for components
│
├── views/                 # Page-level components and layouts
│   ├── DataFormulator.tsx     # Main landing/workspace view
│   ├── VisualizationView.tsx  # Chart rendering and encoding panel
│   ├── DataThread.tsx         # Individual thread/analysis view
│   ├── DataThreadCards.tsx    # Thread preview cards
│   ├── DataView.tsx           # Table/data view component
│   ├── DataLoadingChat.tsx    # Conversational data loading interface
│   ├── DataSourceSidebar.tsx  # Data connector sidebar
│   ├── DBTableManager.tsx     # Database table management
│   ├── AgentChatInput.tsx     # Agent interaction input box
│   ├── AgentPausePanel.tsx    # Agent pause/clarification UI
│   ├── AgentRulesDialog.tsx   # Agent rules/constraints dialog
│   ├── AgentToyIcon.tsx       # Agent avatar icon
│   ├── ChatDialog.tsx         # Chat message display
│   ├── ReportView.tsx         # Generated report view
│   ├── ChartifactDialog.tsx   # Export to chartifact format
│   ├── ChartQuickConfig.tsx   # Quick chart configuration panel
│   ├── ChartRenderService.tsx # Off-screen chart rendering service
│   ├── ChartUtils.tsx         # Chart utility functions
│   ├── ChartVariantStrip.tsx  # Chart variant/style selector
│   ├── ColumnFilterPopover.tsx # Column filtering UI
│   ├── EncodingBox.tsx        # Encoding channel selector
│   ├── EncodingShelfCard.tsx  # Encoding shelf card
│   ├── EncodingShelfThread.tsx # Per-thread encoding shelf
│   ├── ExampleSessions.tsx    # Demo session cards
│   ├── ExplComponents.tsx     # Exploratory components
│   ├── InteractionEntryCard.tsx # Agent interaction log display
│   ├── KnowledgePanel.tsx     # Knowledge base panel
│   ├── LocalInstallUpgradePanel.tsx # Desktop upgrade UI
│   ├── LogViewerDialog.tsx    # Debug log viewer
│   ├── MessageSnackbar.tsx    # Toast notifications
│   ├── ModelSelectionDialog.tsx # LLM model picker
│   ├── MultiTablePreview.tsx  # Multiple table preview
│   ├── OperatorCard.tsx       # Data operator card
│   ├── ReactTable.tsx         # React Table integration
│   ├── RefreshDataDialog.tsx  # Data refresh confirmation
│   ├── SelectableDataGrid.tsx # Selectable data table
│   ├── SessionDistill.tsx     # Session summary/distill
│   ├── SimpleChartRecBox.tsx  # Simple chart recommendation box
│   ├── SourceTableShelf.tsx   # Source table selector
│   ├── TestPanel.tsx          # Testing utilities panel
│   ├── TiptapReportEditor.tsx # Report editor with Tiptap
│   ├── UnifiedDataUploadDialog.tsx # Unified file/data upload
│   ├── About.tsx              # About/help dialog
│   ├── ViewUtils.tsx          # View utility functions
│   ├── workflowContext.ts     # Workflow context provider
│   ├── threadLayout.ts        # Thread layout calculations
│   ├── dataLoadingSuggestions.ts # Data loading suggestions
│   ├── DataOperationCard.tsx  # Data operation UI
│   └── [more view components...]
│
├── dataOperations/        # Data transformation logic
│   └── models.ts          # Data operation type definitions (DataOperation, LoadQuery, etc.)
│
├── i18n/                  # Internationalization
│   ├── index.ts           # i18next initialization (en, zh, auto-detect)
│   ├── vega-locale.ts     # Vega-Lite locale configuration
│   ├── locales/
│   │   ├── en/            # English translations
│   │   │   ├── common.json # Common UI strings
│   │   │   ├── chart.json  # Chart-related strings
│   │   │   ├── data.json   # Data operation strings
│   │   │   └── ...         # [many more JSON files]
│   │   └── zh/            # Chinese (Simplified) translations
│   │       └── [same structure as en/]
│   ├── TRANSLATION_GUIDE.md # Guide for adding translations
│   └── locales/index.ts   # Export all locale files
│
├── scss/                  # Styling (SCSS modules)
│   ├── App.scss           # Main app styles
│   ├── DataView.scss      # Data view styles
│   ├── VisualizationView.scss # Chart view styles
│   ├── EncodingShelf.scss # Encoding panel styles
│   ├── DraggableCard.scss # Draggable card styles
│   └── [other SCSS files...]
│
├── assets/                # Static assets
│   ├── icon-design.md     # Icon design documentation
│   ├── df-logo.svg        # Data Formulator logo
│   └── [other images, icons...]
```

### `/public` - Public Static Assets

```
public/
├── manifest.json          # PWA manifest
├── robots.txt             # SEO robots configuration
├── df_*.json              # Example datasets (gas prices, energy, movies, stocks, unemployment)
└── demos/
    └── demos.yaml         # Demo session catalog
```

---

## Build & Development

### Configuration Files

#### **vite.config.ts** - Build Configuration
- **Build output:** `py-src/data_formulator/dist/`
- **Bundler:** Vite with React SWC for fast builds
- **Chunk splitting:** Vendor chunks for React, MUI, Vega, D3, utils, editor, markdown, misc
- **Entry file:** `DataFormulator.js`
- **API proxy:** `/api` routes proxied to `http://localhost:5567`
- **Alias:** `@` → `./src`
- **Advanced dev:** Optional local `flint-chart` via `FLINT_CHART_LOCAL` env var

```javascript
// Key vendor chunks:
'vendor-react': ['react', 'react-dom', 'react-redux', 'redux', '@reduxjs/toolkit']
'vendor-mui': ['@mui/material', '@mui/icons-material', '@mui/lab', '@emotion/react']
'vendor-vega': ['vega', 'vega-lite', 'vega-embed', 'react-vega']
'vendor-d3': ['d3']
'vendor-utils': ['lodash', 'localforage', 'dompurify', 'validator']
'vendor-editor': ['prismjs', 'prism-react-renderer', 'prettier']
'vendor-markdown': ['markdown-to-jsx', 'katex', 'react-katex']
'vendor-misc': ['exceljs', 'html2canvas', 'allotment', 'react-dnd', 'react-virtuoso']
```

#### **vitest.config.ts** - Test Configuration
- **Environment:** jsdom (browser-like)
- **Setup:** `tests/frontend/setup.ts`
- **Test files:** `tests/frontend/**/*.test.{ts,tsx}`
- **Test globals:** enabled (describe, it, expect without imports)

#### **package.json** - Dependencies & Scripts
```json
{
  "name": "data-formulator",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",              // Start dev server on :5173
    "build": "vite build",      // Build for production
    "preview": "vite preview",  // Preview production build
    "test": "vitest",           // Run tests
    "lint": "eslint src/**/*.{ts,tsx}"  // Lint source
  },
  "dependencies": {
    // React & state management
    "react": "^18",
    "react-dom": "^18",
    "react-redux": "^9",
    "@reduxjs/toolkit": "^2.12.0",
    "redux-persist": "^6",
    "localforage": "^1.10",
    
    // UI framework
    "@mui/material": "^7.1.1",
    "@mui/icons-material": "^7.1.1",
    "@mui/x-tree-view": "^9.0.1",
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.0",
    
    // Chart visualization
    "flint-chart": ">=0.5.0",
    "vega": "^5",
    "vega-lite": "^5",
    "react-vega": "^7",
    "d3": "^7.3.0",
    
    // Data processing
    "duckdb": "^1",
    "duckdb-wasm": "^1",
    "exceljs": "^4.4.0",
    
    // Utilities
    "lodash": "^4.18.1",
    "i18next": "^23.7.6",
    "react-i18next": "^13.5.0",
    
    // Rich editing
    "@tiptap/react": "^3.29.2",
    "@tiptap/starter-kit": "^3.29.2",
    "@uiw/react-codemirror": "^4.25.11",
    
    // Drag & drop
    "react-dnd": "^16.0.1",
    "react-dnd-html5-backend": "^16.0.1",
    
    // Routing
    "react-router-dom": "^6",
    
    // Other
    "allotment": "^1.20.4",        // Split panes
    "react-virtuoso": "^4",        // Virtual scrolling
    "html2canvas": "^1.4.1",       // Screenshot export
    "dompurify": "^3.4.0",         // HTML sanitization
    "validator": "^13.12.2",       // Data validation
  }
}
```

### Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Backend server (for full stack development)
uv run data_formulator  # Runs on :5567
```

---

## Entry Point & Initialization

### `src/index.tsx` - Application Entry Point

```typescript
import React from 'react';
import './index.css';
import './i18n';  // Initialize i18next

import store, { persistor } from './app/store'
import { Provider } from 'react-redux'
import { AppFC } from './app/App';
import { PersistGate } from 'redux-persist/integration/react'
import { createRoot } from 'react-dom/client';

const domNode = document.getElementById('root') as HTMLElement;
const root = createRoot(domNode);

root.render(<React.StrictMode>
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <AppFC />
    </PersistGate>
  </Provider>
</React.StrictMode>);
```

**Initialization Sequence:**
1. **Global styles** loaded from `index.css` (CSS variables, design tokens)
2. **i18n** initialized (`./i18n/index.ts`)
3. **Redux store** created with persistence config
4. **Provider wrapper** sets Redux state tree
5. **PersistGate** gates rendering until Redux state is rehydrated from localStorage
6. **AppFC** component renders

### `src/app/App.tsx` - Root Component

**Purpose:** Top-level app shell with:
- Router setup (React Router v6)
- Material-UI theming
- Authentication handling (OIDC, GitHub OAuth)
- Workspace management
- Menu and toolbar UI

**Key structures:**
```typescript
export const AppFC = () => {
  const theme = createTheme({...});  // MUI theme
  const dispatch = useDispatch<AppDispatch>();
  
  // Auth callback routing
  // Workspace picker or main UI
  // Menu with settings, language selection, workspace operations
  // Auto-save hooks (useAutoSave, useWorkspaceAutoName)
}
```

---

## Redux State Management

### Store Configuration (`src/app/store.ts`)

```typescript
// Redux persist setup
const persistConfig = {
  key: 'root',
  storage: localforage,  // Use IndexedDB via localforage
  blacklist: [
    'serverConfig',           // Always fetch fresh from server
    'globalModels',           // Always fetch fresh
    'chartSynthesisInProgress', // Transient flag
    'starterQuestionsStatus'  // Transient status
  ],
  transforms: [stripConnectorPrefill],  // Strip sensitive form data
  migrate: migrateState,  // Version upgrade handler
};

// Redux store with middleware
const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false })  // Allow non-serializable (Map/Set)
});
```

### Redux Slice (`src/app/dfSlice.tsx`)

The main Redux slice manages **all application state** in a single reducer. This is the heart of state management.

#### State Interface (`DataFormulatorState`)

```typescript
export interface DataFormulatorState {
  // ── Identity & Configuration ────────────────────────────
  identity: Identity;                    // 'local', 'browser', or user auth
  globalModels: ModelConfig[];          // LLM models from server
  models: ModelConfig[];                // User-added models
  selectedModelId: string | undefined;
  testedModels: Array<{id, status, message}>;

  // ── Tables & Data ──────────────────────────────────────
  inputTables: InputTable[];            // Source tables (uploaded/pasted)
  derivedTables: DictTable[];           // AI-generated derived tables
  loadedTableNodes: LoadedTableNode[];  // Async-loaded table metadata
  tableSemantics: TableSemanticsInfo[]; // Semantic types per column
  draftNodes: DraftNode[];              // In-progress table nodes

  // ── Charts & Visualization ─────────────────────────────
  charts: Chart[];                      // Rendered charts
  chartThumbnails: Record<string, string>; // PNG data URLs
  chartSynthesisInProgress: string[];   // Chart IDs currently generating

  // ── Interaction & UI ──────────────────────────────────
  conceptShelfItems: FieldItem[];       // Fields in concept shelf
  messages: Message[];                  // Log messages
  displayedMessageIdx: number;
  focusedId: FocusedId;                 // Selected table/chart/thread
  focusedDataCleanBlockId: {blockId, itemId} | undefined;
  viewMode: 'editor' | 'report';        // View mode

  // ── Agent & Chat ──────────────────────────────────────
  dataLoadingChatMessages: ChatMessage[];      // Data loading chat
  dataLoadingChatInProgress: boolean;
  dataLoadingChatPending: {text, images, attachments} | null;
  analystChatPending: {text, images, attachments} | null;
  agentHandoffRequest: {target, prompt, images} | null;

  // ── Reports & Text ───────────────────────────────────
  generatedReports: GeneratedReport[];
  textTurns: TextTurn[];  // Clarifications and explanations

  // ── Workspace & UI State ──────────────────────────────
  activeWorkspace: {id, displayName, readOnly} | null;
  sessionLoading: boolean;
  sessionLoadingLabel: string;
  dataSourceSidebarOpen: boolean;
  dataSourceSidebarTab: 'sources' | 'sessions' | 'knowledge';
  focusedConnectorId?: string;

  // ── Configuration ─────────────────────────────────────
  serverConfig: ServerConfig;
  config: ClientConfig;

  // ── Other State ───────────────────────────────────────
  dataLoaderConnectParams: Record<string, Record<string, string>>;
  tableLoadsInFlight: number;
  displayRowsTick: number;
  connectorRefreshRequest: number;
  starterQuestions: {[tableId: string]: {questions, signature}};
  starterQuestionsStatus: {[tableId: string]: 'idle' | 'loading' | 'error'};
}
```

#### Selectors (`dfSelectors`)

```typescript
// Key selectors for accessing state
dfSelectors.getDerivedTables()     // All derived tables
dfSelectors.getInputTables()       // All input tables
dfSelectors.selectTableIds()       // All table IDs
dfSelectors.selectCanvasTarget()   // Currently focused table/chart
dfSelectors.selectSessionEmpty()   // Boolean: no data loaded
dfSelectors.getAllModels()         // Global + user models
dfSelectors.selectRefreshConfigs() // Refresh configurations
dfSelectors.getDataFieldItems()    // Fields from base table
```

#### Actions (`dfActions`)

Key action creators:
```typescript
// Table management
addTable(table: InputTable)
updateTable(payload: {tableId, table})
deleteTable(tableId)
addChart(chart)
updateChart({chartId, chart})
deleteChart(chartId)
setFocusedId(id)

// Agent & Chat
addDataLoadingChatMessage(message)
updateChartSynthesisInProgress(chartIds)
setDataLoadingChatPending({text, images, attachments})

// Workspace
setActiveWorkspace(workspace)
setSessionLoading(boolean)
setViewMode('editor' | 'report')

// UI
setDataSourceSidebarOpen(boolean)
setDataSourceSidebarTab('sources' | 'sessions' | 'knowledge')
setFocusedConnectorId(id)
```

#### Async Thunks

```typescript
// Model operations
export const fetchGlobalModelList = createAsyncThunk(...)  // Fetch from /api/config/models
export const fetchAvailableModels = createAsyncThunk(...)  // Filter by provider

// Table metadata
export const fetchFieldSemanticType = createAsyncThunk(...)  // Fetch field semantic type

// Suggestions
export const generateStarterQuestions = createAsyncThunk(...)  // AI-generated questions

// Analytics
export const fetchColumnStats = createAsyncThunk(...)  // Column statistics

// Code & Explanation
export const fetchCodeExpl = createAsyncThunk(...)  // Code explanation
```

---

## API Client & Communication

### `src/app/apiClient.ts` - Unified API Client

Provides standardized request handling with error management, streaming support, and identity injection.

#### Key Exports

```typescript
// Error class
class ApiRequestError extends Error {
  constructor(
    public readonly apiError: ApiError,
    public readonly httpStatus: number
  )
  
  get isRetryable(): boolean
  get isAuthError(): boolean
}

// Response types
interface ApiError {
  code: string;
  message: string;
  detail?: string;
  retry?: boolean;
  request_id?: string;
}

interface StreamEvent<T = any> {
  type: string;
  data?: T;
  error?: ApiError;
  message?: string;
  message_code?: string;
  message_params?: Record<string, unknown>;
}

// API functions
async function apiRequest<T>(url, options): Promise<{data: T}>
async function* streamRequest<T>(url, options): AsyncGenerator<StreamEvent<T>>
```

#### Response Format

All API responses follow this envelope:

```json
{
  "status": "success" | "error",
  "data": {...},
  "error": {"code": "...", "message": "..."}
}
```

Streaming responses use NDJSON (newline-delimited JSON):

```json
{"type": "init", "data": {...}}
{"type": "action", "data": {...}}
{"type": "chunk", "message": "reasoning...", "data": {...}}
{"type": "completion", "data": {...}}
```

#### Usage Example

```typescript
// Non-streaming request
const response = await apiRequest('/api/agents/models', {
  method: 'POST',
  body: JSON.stringify({...})
});

// Streaming request (SSE)
for await (const event of streamRequest('/api/agents/run', {
  method: 'POST',
  body: JSON.stringify({...})
})) {
  if (event.type === 'chunk') {
    dispatch(updateProgress(event.data));
  } else if (event.type === 'completion') {
    dispatch(completeChartSynthesis(event.data));
  }
}
```

### Key API Endpoints

```
GET  /api/config/models              # Fetch global LLM models
GET  /api/connectors/list            # List available data connectors
POST /api/agents/run                 # Stream agent execution (SSE)
POST /api/tables/create              # Create table from data
POST /api/tables/{id}/refresh        # Refresh table data
GET  /api/workspaces                 # List workspaces
POST /api/workspaces                 # Create workspace
GET  /api/workspaces/{id}            # Load workspace
POST /api/workspaces/{id}            # Save workspace
DELETE /api/workspaces/{id}          # Delete workspace
```

### Streaming Communication Pattern

```
User asks question in chat
            ↓
Frontend POST to /api/agents/run with SSE
            ↓
Backend LLM processes request, streams events:
  - init: Initialize agent state
  - action: Tool call (e.g., aggregate data)
  - chunk: LLM reasoning token
  - completion: Final result
            ↓
Frontend receives each StreamEvent
            ↓
Redux dispatch updates (charts, messages, state)
            ↓
React re-render with updated UI
```

---

## Data Types & Semantics

### `/src/data/types.ts` - Type System

Defines data types, coercion, and type inference logic.

```typescript
enum Type {
  String = 'string',
  Boolean = 'boolean',
  Integer = 'integer',
  Number = 'number',
  Date = 'date',
  DateTime = 'datetime',
  Time = 'time',
  Duration = 'duration',
  Auto = 'auto',
}

// Coercion: value → Type
CoerceType: {
  number: (v) => +v,
  date: (v) => v.toISOString().slice(0, 10),
  datetime: (v) => v.toISOString(),
  ...
}

// Testing: value → boolean (is value of this type?)
TestType: {
  number: (v) => !isNaN(+v),
  date: (v) => /^\d{4}[-/]\d{1,2}[-/]\d{1,2}$/.test(v),
  ...
}

// Type inference: value[] → Type
testType(values: any[]): Type

// Vega mapping: Type → Vega-Lite type
getDType(type: Type, domain: any[]): 'quantitative' | 'nominal' | 'temporal'

// API type mapping: backend dtype string → App Type
mapApiTypeToAppType(apiType: string): Type
```

### `/src/data/table.ts` - ColumnTable

Column-oriented table representation for efficient operations.

```typescript
class ColumnTable {
  protected _data: Map<string, Column>;      // Column name → Column
  protected _names: string[];                // Column order
  protected _nrows: number;
  protected _objects: any[];                 // Row-oriented view

  numCols(): number
  numRows(): number
  column(name: string): Column | undefined
  columns(): Map<string, Column>
  names(): string[]
  get(name: string, row: number): any
  metadata(): [string, Type][]  // Column name and type
}
```

### `/src/data/column.ts` - Column

Single column storage.

```typescript
class Column {
  protected _data: any[];        // Values
  protected _type: Type;         // Column type
  protected _uniques: any[];     // Unique values (lazy computed)

  get uniques(): any[]
  get type(): Type
  get length(): number
  get(row: number): any
}
```

### Key Data Structures (`ComponentType.tsx`)

#### Chart Definition
```typescript
interface Chart {
  id: string;
  chartType: string;              // 'Line Chart', 'Bar Chart', etc.
  encodingMap: EncodingMap;       // Channel → Encoding
  tableRef: string;               // Reference to source table
  source: 'user' | 'trigger';
  config?: ChartStyleVariant;     // Style configuration
  // ... more fields
}

interface EncodingMap {
  [key: Channel]: EncodingItem;   // x, y, color, size, shape, etc.
}

interface EncodingItem {
  channel: Channel;
  field?: FieldItem;
  bin?: boolean;
  sort?: string;
  // ... more options
}
```

#### Table Definition
```typescript
interface InputTable {
  id: string;
  name: string;
  source: DataSourceType;         // 'paste', 'file', 'url', 'database'
  sourceConfig: DataSourceConfig;
  columns: InputTableColumn[];
  rows: any[];
  // ... more fields
}

interface DictTable {
  id: string;
  name: string;
  displayName?: string;
  fields: Field[];                // Column metadata
  rows: any[];                    // Data
  rowCount?: number;
  // ... more fields
}
```

#### Field Definition
```typescript
interface FieldItem {
  id: string;
  name: string;
  source: 'custom' | 'original';  // Derived or original
  tableRef: string;               // Source table ID
}

interface Field {
  name: string;
  type: Type;                     // data/types.ts Type
  semanticType?: string;          // 'ID', 'Measure', 'Date', 'Region', 'Ordinal'
  displayName?: string;
  // ... more metadata
}
```

#### Agent Message Types
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  images?: string[];              // Attached images
  attachments?: ChatAttachment[];
  // ... more fields
}

interface InteractionEntry {
  from: Actor;                    // 'user' | 'data-agent' | ...
  to: Actor;
  role: 'prompt' | 'clarify' | 'instruction' | 'error' | 'explain' | 'delegate';
  plan?: string;                  // Agent reasoning
  content: string;                // Message body
  displayContent?: string;
  // ... more fields
}
```

---

## View Components & Layout

### Main View Hierarchy

```
App.tsx (Root)
  ├── Router (React Router v6)
  │   ├── OidcCallback           (for OIDC login)
  │   ├── DataFormulator.tsx     (main workspace)
  │   └── [other routes]
  │
  └── DataFormulator.tsx
      ├── Toolbar (theme, auth, model selection, workspace menu)
      │
      ├── Allotment (vertical split: sidebar | canvas)
      │   │
      │   ├── DataSourceSidebar.tsx
      │   │   ├── Data Connector Forms
      │   │   ├── Session/Workspace List
      │   │   └── Knowledge Base Panel
      │   │
      │   └── Allotment (horizontal split: threads | report)
      │       ├── ThreadPane (Allotment, max 5 threads)
      │       │   ├── DataThread.tsx × N
      │       │   │   ├── AgentChatInput
      │       │   │   ├── ChatMessages
      │       │   │   ├── DataView (table/grid)
      │       │   │   ├── VisualizationView
      │       │   │   │   ├── ChartRenderService
      │       │   │   │   ├── EncodingShelfThread
      │       │   │   │   └── Chart Canvas
      │       │   │   └── AgentPausePanel (if clarifying)
      │       │   │
      │       │   └── ExampleSessions (if no data)
      │       │
      │       └── ReportView.tsx (if viewMode == 'report')
      │           └── TiptapReportEditor
      │               ├── Markdown editing
      │               ├── Chart embedding
      │               └── Export options
```

### Key View Components

#### `DataFormulator.tsx` - Landing/Workspace View
- Main workspace dispatcher
- Handles workspace loading/switching
- Shows empty state with example sessions
- Renders thread pane or report view based on mode
- Auto-saves workspace

#### `DataThread.tsx` - Analysis Thread
- Represents a single analysis path (branch)
- Contains agent interaction history
- Displays current data table
- Shows active chart for the thread
- Provides model/rendering selection
- Pause points for clarification

#### `VisualizationView.tsx` - Chart Rendering View
- Full-screen chart display
- Chart variant selector (themes/styles)
- Encoding shelf (bind fields to visual channels)
- Quick chart configuration
- Export/download options

#### `DataLoadingChat.tsx` - Data Connector Chat
- Conversational interface for loading data
- Connector auto-selection and configuration
- File upload integration
- Data preview before loading
- Multi-turn clarification

#### `DataSourceSidebar.tsx` - Sidebar Panel
- Data connector list and forms
- Workspace session switcher
- Knowledge base search
- Collapsible to rail view

#### `ReportView.tsx` - Report Editing
- Tiptap rich text editor
- Markdown + embedded charts
- Export to PDF, PNG, etc.
- Share/download options

---

## Internationalization (i18n)

### i18n Setup (`src/i18n/index.ts`)

```typescript
import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { en, zh } from './locales';

const resources = {
  en: { translation: en },
  zh: { translation: zh },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });
```

### Locale Files

**Structure:** `src/i18n/locales/{en,zh}/`

```
en/
  ├── common.json         # Common UI strings
  ├── chart.json          # Chart-related
  ├── data.json           # Data operations
  ├── error.json          # Error messages
  ├── help.json           # Help/tooltips
  ├── menu.json           # Menu items
  ├── message.json        # Chat messages
  ├── workspace.json      # Workspace operations
  └── ...
zh/
  └── [same structure in Chinese]
```

### Usage in Components

```typescript
import { useTranslation } from 'react-i18next';

export const MyComponent = () => {
  const { t, i18n } = useTranslation();
  
  return (
    <button onClick={() => i18n.changeLanguage('zh')}>
      {t('common:language')}
    </button>
  );
};
```

### Vega-Lite Localization

`src/i18n/vega-locale.ts` provides translations for Vega-Lite UI elements:
- Axis labels
- Legend titles
- Tooltip formatting
- Error messages

---

## Styling & Theming

### Design System (`src/app/tokens.ts`)

Centralized design tokens used throughout the app:

```typescript
// Colors
export const palettes = {
  light: {
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#333333',
    // ... many more
  },
  dark: {
    // ...
  }
};

export const paletteKeys = ['light', 'dark', 'auto'];
export const defaultPaletteKey = 'auto';  // System preference

// Semantic colors
export const bgAlpha = 'rgba(255, 255, 255, 0.5)';

// Spacing, typography, borders
export const borderColor = '#e0e0e0';
export const radius = '4px';
export const transition = 'all 0.3s ease';
```

### Material-UI Theme

`App.tsx` creates a theme using MUI `createTheme()`:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: blue[500] },
    secondary: { main: purple[500] },
    success: { main: green[600] },
    warning: { main: orange[500] },
    error: { main: red[500] },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    // ... sizing and weight configuration
  },
  components: {
    MuiButton: { styleOverrides: { ... } },
    MuiCard: { styleOverrides: { ... } },
    // ... component-specific overrides
  },
});
```

### SCSS Files

**Main stylesheets** in `src/scss/`:

```scss
// App.scss         - Global app layout
// DataView.scss    - Table/grid display
// VisualizationView.scss - Chart pane
// EncodingShelf.scss     - Encoding channel UI
// DraggableCard.scss     - Card components
```

Each SCSS file is imported as a CSS module and scoped to its component:

```typescript
import styles from '../scss/DataView.scss';

export const DataView = () => {
  return <div className={styles.container}>...</div>;
};
```

### CSS Variables (Design Scale)

Defined in `src/index.css`:

```css
:root {
  --df-scale: 1;                  /* Density scaling */
  --df-font-mono: "Roboto Mono", ...;
  --df-text-xxs: 10px;
  --df-text-xs: 11px;
  --df-text-sm: 12px;
  /* ... many more */
}
```

Responsive layout (`LayoutProvider.tsx`) adjusts `--df-scale` per density level.

---

## Data Flow Patterns

### Chart Synthesis Flow

```
User question in AgentChatInput
         ↓
addDataLoadingChatMessage dispatch
         ↓
DataLoadingChat sends SSE to /api/agents/run
         ↓
Backend processes with LLM + skills:
  - Streaming responses (init, action, chunk, completion)
         ↓
Frontend StreamEvent listener:
  ├─ init: Initialize agent state
  ├─ action: Tool call (e.g., "aggregate")
  ├─ chunk: Reasoning tokens
  └─ completion: Final chart spec
         ↓
Dispatch updateChartSynthesisInProgress
         ↓
ChartRenderService picks up new chart
         ↓
Render chart to canvas
         ↓
Save thumbnail to Redux
         ↓
VisualizationView displays result
```

### Data Loading Flow

```
User uploads file / pastes data / connects to DB
         ↓
UnifiedDataUploadDialog captures source
         ↓
API request to /api/tables/create
         ↓
addTable dispatch (InputTable)
         ↓
tableThunks.ts fetches semantic types
         ↓
tableResolution.ts materializes preview rows
         ↓
DataView displays loaded table
         ↓
User can now ask questions (triggers chart synthesis)
```

### Thread Branching Flow

```
User asks question in DataThread
         ↓
New analysis path (thread) created
         ↓
LLM derives new DictTable from existing
         ↓
Chat history preserved in TextTurns
         ↓
Alternative visualizations in parallel threads
         ↓
User can switch between threads via DataThreadCards
```

### Redux Update Pattern

```
User action (click, input, etc.)
         ↓
Event handler dispatches Redux action
  dispatch(dfActions.addChart(chart))
         ↓
dfSlice reducer updates state immutably
         ↓
Redux notifies connected components via selectors
         ↓
React re-render with new props
         ↓
Derived state computed (selectors)
         ↓
Side effects triggered (useEffect hooks)
```

---

## Component Hierarchy

### Critical Component Tree

```
App (root theme, routing)
  ├── DataFormulator (workspace, layout orchestration)
  │   ├── DataSourceSidebar (left pane)
  │   │   ├── ConnectorFormCard (for each source)
  │   │   ├── DataLoadingChat
  │   │   └── KnowledgePanel
  │   │
  │   └── Allotment (split pane)
  │       ├── ThreadPane (horizontal split × threads)
  │       │   └── DataThread (for each thread)
  │       │       ├── AgentChatInput
  │       │       ├── ChatDialog (message history)
  │       │       │   └── InteractionEntryCard (per message)
  │       │       ├── DataView (table display)
  │       │       │   └── ReactTable (virtualized rows)
  │       │       ├── VisualizationView (chart)
  │       │       │   ├── ChartRenderService (off-screen render)
  │       │       │   ├── EncodingShelfThread
  │       │       │   │   └── EncodingShelfCard (per channel)
  │       │       │   │       └── LittleConceptCard (field)
  │       │       │   └── ChartVariantStrip (theme picker)
  │       │       └── AgentPausePanel (if clarifying)
  │       │           └── ClarificationPanel
  │       │
  │       └── ReportView (if viewMode == 'report')
  │           └── TiptapReportEditor
  │
  └── Dialogs (modal overlays)
      ├── UnifiedDataUploadDialog
      ├── ModelSelectionDialog
      ├── ChartifactDialog
      └── [other modals]
```

### Reusable Component Patterns

#### Data Display Components
- `ReactTable` - Virtualized data grid (react-table)
- `SelectableDataGrid` - Row selection support
- `DataFrameTable` - Pandas-like display
- `ConnectorTablePreview` - Quick connector preview

#### Control Components
- `ChartQuickConfig` - Chart configuration UI
- `ColumnFilterPopover` - Column filter menu
- `EncodingBox` - Visual channel binding
- `EncodingShelfCard` - Single channel editor

#### Dialog & Form Components
- `ConnectorFormCard` - Connector credential form
- `LoadPlanCard` - Data load plan preview
- `DataOperationCard` - Data cleaning operation
- `AgentRulesDialog` - Agent constraint editor

#### Utility Components
- `MarkdownEditor` - Markdown with preview
- `RotatingTextBlock` - Animated suggestions
- `ScrollFade` - Fade at scroll edges
- `ResizeHandle` - Splitter drag handle

---

## Key Concepts & Data Structures

### Workspace

Container for an analysis session:
- **Fields:**
  - `id`: Stable folder name identifier
  - `displayName`: User-facing name (can be renamed)
  - `readOnly`: Whether user can edit
- **Persistence:** Local filesystem or Azure Blob Storage
- **Export/Import:** Full session serialization to/from ZIP

### Table Types

#### InputTable
- Source of truth data (uploaded, pasted, or from connector)
- Immutable after load
- Can have multiple input tables in same workspace

#### DictTable (Derived)
- Output from agent skill (aggregate, transform, etc.)
- Derived from existing table(s)
- Can be used as input for further operations

#### Virtual Table
- Lazy-loaded preview of large datasets
- Only fetches rows as needed (scroll-based)
- Metadata always available, data on-demand

### Thread

Analysis path branching:
- **Root thread:** Initial analysis with first table
- **Derived thread:** Alternative analysis from user question
- **Independent:** Each thread has its own chat history
- **Parallel:** Up to 5 threads visible simultaneously in split pane

### Data Thread

Redux state structure for thread-specific data:
```typescript
interface DataThread {
  id: string;
  tableId: string;              // Currently displayed table
  chartId?: string;             // Currently displayed chart
  interactions: InteractionEntry[];  // Chat history
  // ... more
}
```

### Chart

Visualization specification:
- **Type:** 'Line Chart', 'Bar Chart', 'Scatter', etc.
- **Encoding:** Maps table fields to visual channels (x, y, color, size, etc.)
- **Vega-Lite:** Underlying spec generation via `flint-chart`
- **Interaction:** Brush, hover, click handling

### Semantic Type

Metadata about column meaning:
- `ID` - Unique identifier (don't aggregate)
- `Measure` - Numeric quantity (aggregate: sum, avg, etc.)
- `Date` - Temporal data (for time axis)
- `Region` - Geographic area (for map/filtering)
- `Ordinal` - Categorical with order (custom sort)

Backend infers from data; frontend allows override.

### Display Instruction

Vega-Lite specification for rendering a chart:
- Generated by Flint semantic engine
- Includes:
  - Data reference and transformations
  - Encoding (channel → field mapping)
  - Mark (point, line, bar, etc.)
  - Scale, axis, legend, tooltip config
  - Interaction marks (brush, hover)
- Rendered by `react-vega` wrapper around Vega-Embed

### Skills

Plugin capabilities for the agent:
- `visualize` - Create chart from table
- `aggregate` - Group and summarize
- `sample` - Reduce rows
- `delegate` - Hand off to specialized agent (report_gen, data_loading)
- `clarify` - Ask user for input
- `explain` - Generate text explanation

### Clarification

Agent asks user a question:
- **Question text:** Displayed to user
- **Response type:** single_choice or free_text
- **Options:** Predefined answers or free input
- **User submits:** Flows back to agent
- **Agent resumes:** Continues with clarification context

---

## Summary

The **Data Formulator frontend** is a sophisticated React/TypeScript application structured around:

1. **Redux state management** - Single source of truth for all app state
2. **Component composition** - Reusable components organized by domain (views, components, data ops)
3. **API communication** - Unified client with streaming SSE for agent interactions
4. **Rich data model** - Tables, charts, fields, threads with semantic meaning
5. **i18n support** - English and Chinese with auto-detection
6. **Responsive layout** - Flexible split-pane architecture with density-aware scaling
7. **Material-UI theming** - Cohesive design system with customizable palette

The application emphasizes **real-time agent interaction** via streaming APIs, **complex state management** for multi-threaded analysis, and **powerful visualization** through Flint + Vega-Lite.

Key files to explore when developing:
- `src/app/dfSlice.tsx` - State and selectors
- `src/app/apiClient.ts` - Backend communication
- `src/views/DataFormulator.tsx` - Layout orchestration
- `src/views/DataThread.tsx` - Analysis experience
- `src/components/ComponentType.tsx` - Type definitions

---

## Appendix: Key File Size & Complexity

| File | Purpose | Complexity |
|------|---------|-----------|
| `dfSlice.tsx` | Redux state | ★★★★★ High - 2500+ lines |
| `DataFormulator.tsx` | Main view | ★★★★ High - 1000+ lines |
| `VisualizationView.tsx` | Chart view | ★★★★ High - 800+ lines |
| `DataThread.tsx` | Analysis thread | ★★★★ High - 800+ lines |
| `apiClient.ts` | API comm | ★★★ Medium - 300+ lines |
| `store.ts` | Redux config | ★★ Low - 50 lines |
| `App.tsx` | Root component | ★★★ Medium - 300+ lines |
| `index.tsx` | Entry point | ★ Low - 25 lines |

