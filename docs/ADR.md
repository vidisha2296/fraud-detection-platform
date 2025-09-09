


---

### **/docs/ADR.md**
```md
# Architectural Decision Records (ADR)

1. **Frontend Rendering**: CSR (Client-Side Rendering) to improve interactivity and reduce server load.
2. **Backend Framework**: FastAPI for async support and easy integration with PostgreSQL & Redis.
3. **Database Choice**: PostgreSQL for relational consistency and complex queries.
4. **Caching**: Redis for caching frequent lookups and handling SSE notifications.
5. **Circuit Breaker Pattern**: Prevent cascading failures from agent downtime.
6. **Rate Limiting**: Protect system endpoints from abuse or accidental overload.
7. **Data Partitioning**: Monthly transaction partitions for scalability.
8. **Logging & Tracing**: Logs are redacted for PII; trace viewer integrated in frontend for debugging.
9. **Fallback Strategy**: If an agent fails, fallback actions are triggered automatically.
10. **Metrics Endpoint**: Exposes system and agent health for monitoring dashboards.
11. **Batch Processing**: Allows bulk fraud assessment with minimal latency.
12. **Evaluation Framework**: Separate eval cases with pass/fail metrics for reproducibility.
