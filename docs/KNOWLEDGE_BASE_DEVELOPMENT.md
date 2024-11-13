# Knowledge Base Development Guide

## Overview

This guide provides detailed instructions for developers to add and manage information in Project Oracle's knowledge base system. The knowledge base uses ChromaDB for vector storage and semantic search capabilities, allowing efficient retrieval of information through both traditional and vector-based search methods.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Setup Requirements](#setup-requirements)
3. [Adding Knowledge Base Entries](#adding-knowledge-base-entries)
4. [Vector Store Operations](#vector-store-operations)
5. [Testing Your Changes](#testing-your-changes)
6. [Best Practices](#best-practices)

## System Architecture

Project Oracle's knowledge base consists of two main components:

1. **VectorStore Service**: Handles document embeddings and similarity search using ChromaDB
2. **KnowledgeBase Service**: Manages the overall knowledge system including data loading and search operations

## Setup Requirements

Before working with the knowledge base, ensure you have:

- Python 3.8 or higher installed
- Project dependencies installed via `pip install -r requirements.txt`
- OpenAI API key set in your environment variables
- Access permissions for the knowledge base JSON file and vector store directory

## Adding Knowledge Base Entries

### 1. JSON Structure

The knowledge base data is stored in a JSON file with the following structure:
