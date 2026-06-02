from typing import Dict, Any, List

# Simulated database
MOCK_DB = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"},
    ],
    "products": [
        {"id": 1, "name": "Laptop", "price": 999, "stock": 10},
        {"id": 2, "name": "Mouse", "price": 25, "stock": 50},
    ]
}

def search_database(query: str, collection: str = "users") -> Dict[str, Any]:
    """
    Search the database for records
    """
    if collection not in MOCK_DB:
        return {
            "error": f"Collection '{collection}' not found",
            "available": list(MOCK_DB.keys())
        }
    
    results = []
    query_lower = query.lower()
    
    for record in MOCK_DB[collection]:
        # Simple search across all string fields
        for key, value in record.items():
            if isinstance(value, str) and query_lower in value.lower():
                results.append(record)
                break
            elif isinstance(value, (int, float)) and str(query_lower) in str(value):
                results.append(record)
                break
    
    return {
        "collection": collection,
        "query": query,
        "results": results,
        "count": len(results)
    }