# Codebase RAG — Frontend

React + Vite frontend for **Codebase RAG**, an AI-powered application for exploring and understanding GitHub codebases through natural-language questions.

The frontend provides the interface for repository ingestion, codebase querying, and displaying grounded answers with file, symbol, and line-level source references.

## Features

- Connect and index a public GitHub repository
- Ask natural-language questions about the codebase
- Display AI-generated answers grounded in retrieved source code
- Show source files, symbols, types, and exact line ranges
- Switch between repositories and rebuild the active index
- Responsive web interface
- Production API configuration through environment variables

## Tech Stack

- React
- Vite
- JavaScript
- CSS
- FastAPI backend
- Vercel deployment

## Local Development

Install dependencies:

```bash
npm install