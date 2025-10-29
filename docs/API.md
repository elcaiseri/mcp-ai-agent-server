# API Documentation

## Available Tools

### 1. Weather Tool

**Endpoint**: `get_weather`

Get current weather information for any location.

**Input**:
```json
{
  "location": "New York"
}
```

**Output**:
```json
{
  "location": "New York",
  "country": "US",
  "temperature": 15.5,
  "feels_like": 14.2,
  "humidity": 65,
  "description": "partly cloudy",
  "wind_speed": 3.5,
  "error": null
}
```

---

### 2. News Tool

**Endpoint**: `fetch_news`

Fetch recent news articles on a topic.

**Input**:
```json
{
  "topic": "artificial intelligence",
  "limit": 5
}
```

**Output**:
```json
{
  "topic": "artificial intelligence",
  "total_results": 1250,
  "articles": [
    {
      "title": "AI Breakthrough...",
      "description": "...",
      "url": "https://...",
      "source": "TechNews",
      "published_at": "2025-10-29T10:30:00Z",
      "author": "John Doe"
    }
  ],
  "error": null
}
```

---

### 3. File Manager Tools

#### Create File

**Endpoint**: `create_file`

**Input**:
```json
{
  "path": "data/notes.txt",
  "content": "My important notes"
}
```

#### Read File

**Endpoint**: `read_file`

**Input**:
```json
{
  "path": "data/notes.txt"
}
```

#### Delete File

**Endpoint**: `delete_file`

**Input**:
```json
{
  "path": "data/notes.txt"
}
```

#### Search Files

**Endpoint**: `search_files`

**Input**:
```json
{
  "directory": "data",
  "pattern": "*.txt"
}
```

**Output**:
```json
{
  "success": true,
  "directory": "/path/to/data",
  "pattern": "*.txt",
  "files": [
    {
      "path": "/path/to/file.txt",
      "name": "file.txt",
      "size": 1024,
      "modified": 1635789123.456
    }
  ],
  "count": 1,
  "error": null
}
```

#### List Directory

**Endpoint**: `list_directory`

**Input**:
```json
{
  "directory": "data"
}
```

---

### 4. Web Fetcher

**Endpoint**: `fetch_webpage`

Fetch and parse webpage content.

**Input**:
```json
{
  "url": "https://example.com",
  "extract_text": true
}
```

**Output**:
```json
{
  "success": true,
  "url": "https://example.com",
  "status_code": 200,
  "content_type": "text/html",
  "title": "Example Domain",
  "text": "This domain is for use in...",
  "full_length": 1256,
  "error": null
}
```

---

### 5. Calculator

#### Calculate

**Endpoint**: `calculate`

Perform mathematical calculations.

**Input**:
```json
{
  "expression": "sqrt(16) + pow(2, 3)"
}
```

**Output**:
```json
{
  "success": true,
  "expression": "sqrt(16) + pow(2, 3)",
  "result": 12.0,
  "error": null
}
```

**Supported Functions**:
- Basic: `+`, `-`, `*`, `/`, `**` (power)
- Math: `sqrt`, `pow`, `abs`, `round`, `min`, `max`, `sum`
- Trigonometry: `sin`, `cos`, `tan`
- Logarithms: `log`, `log10`, `exp`
- Constants: `pi`, `e`

#### Convert Units

**Endpoint**: `convert_units`

Convert between different units.

**Input**:
```json
{
  "value": 100,
  "from_unit": "celsius",
  "to_unit": "fahrenheit"
}
```

**Supported Conversions**:

**Temperature**: celsius, fahrenheit, kelvin

**Length**: meter, kilometer, mile, foot, inch

**Weight**: kilogram, gram, pound, ounce

---

### 6. AI Agent

**Endpoint**: `execute_agent_task`

Execute complex multi-step tasks using LangChain AI agent.

**Input**:
```json
{
  "task": "Check the weather in Tokyo, fetch news about Japan, and write a brief report"
}
```

**Output**:
```json
{
  "success": true,
  "task": "Check the weather in Tokyo...",
  "result": "Based on the current weather data...",
  "steps": [...],
  "error": null
}
```

**Capabilities**:
- Multi-step reasoning
- Tool chaining
- Natural language understanding
- Context-aware responses

---

## Error Handling

All tools return consistent error structures:

```json
{
  "success": false,
  "error": "Error description",
  ...
}
```

Common error types:
- API key not configured
- Resource not found
- Network timeout
- Invalid input
- Permission denied

---

## Rate Limits

- **Weather API**: 60 calls/minute (free tier)
- **News API**: 100 calls/day (free tier)
- **OpenAI API**: Depends on your plan
- **File operations**: No limit
- **Web fetching**: Respect robots.txt

---

## Best Practices

1. **API Keys**: Store in `.env`, never commit
2. **File Paths**: Use relative paths when possible
3. **Error Handling**: Always check `success` field
4. **Rate Limits**: Implement caching for frequent requests
5. **Web Scraping**: Add delays between requests
6. **Large Files**: Use streaming for files > 10MB

---

## Examples

See `examples/usage_demo.py` for complete working examples.
