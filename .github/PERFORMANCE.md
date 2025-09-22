# Performance Guidelines

This document outlines performance considerations and optimization strategies for the Binance Streaming Project.

## 🎯 Performance Goals

### Latency Targets
- **Data Processing**: < 100ms end-to-end
- **API Response**: < 50ms for simple queries
- **WebSocket Updates**: < 10ms for real-time data
- **Database Queries**: < 20ms for typical operations

### Throughput Targets
- **Message Processing**: 10,000+ messages/second
- **Concurrent Users**: 1,000+ simultaneous connections
- **Database Operations**: 1,000+ queries/second
- **API Requests**: 5,000+ requests/second

## 📊 Performance Monitoring

### Key Metrics

#### System Metrics
- **CPU Usage**: < 70% average
- **Memory Usage**: < 80% of available
- **Disk I/O**: < 80% of capacity
- **Network I/O**: Monitor bandwidth usage

#### Application Metrics
- **Message Processing Rate**: Messages per second
- **Database Query Time**: Average query duration
- **Error Rate**: < 0.1% of total requests
- **Response Time**: P50, P95, P99 percentiles

#### Business Metrics
- **Data Freshness**: Time from source to database
- **Data Accuracy**: Percentage of correct calculations
- **System Uptime**: > 99.9% availability
- **User Satisfaction**: Response time perception

### Monitoring Tools

```python
import time
import logging
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_performance
def process_trade_data(data):
    # Process trade data
    pass
```

## 🚀 Optimization Strategies

### Database Optimization

#### Indexing
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_kpi_symbol_1m_symbol_time ON kpi_symbol_1m(symbol, window_start);
CREATE INDEX idx_kpi_symbol_1m_window_start ON kpi_symbol_1m(window_start);

-- Use partial indexes for filtered queries
CREATE INDEX idx_kpi_symbol_1m_recent ON kpi_symbol_1m(window_start) 
WHERE window_start >= NOW() - INTERVAL '1 day';
```

#### Query Optimization
```sql
-- Use EXPLAIN ANALYZE to understand query performance
EXPLAIN ANALYZE 
SELECT symbol, AVG(avg_price) 
FROM kpi_symbol_1m 
WHERE window_start >= NOW() - INTERVAL '1 hour'
GROUP BY symbol;

-- Optimize with proper WHERE clauses
SELECT * FROM kpi_symbol_1m 
WHERE symbol = 'BTCUSDT' 
  AND window_start >= '2024-09-22 18:00:00'
  AND window_start < '2024-09-22 19:00:00'
ORDER BY window_start;
```

#### Connection Pooling
```python
import psycopg2.pool

class DatabaseManager:
    def __init__(self):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
    
    def get_connection(self):
        return self.pool.getconn()
    
    def return_connection(self, conn):
        self.pool.putconn(conn)
```

### Memory Optimization

#### Efficient Data Structures
```python
from collections import deque
import numpy as np

class EfficientAggregator:
    def __init__(self, window_size=60):
        # Use deque for O(1) append/pop operations
        self.prices = deque(maxlen=window_size)
        self.volumes = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
    
    def add_trade(self, price, volume, timestamp):
        self.prices.append(price)
        self.volumes.append(volume)
        self.timestamps.append(timestamp)
    
    def calculate_vwap(self):
        if not self.prices:
            return 0.0
        
        # Use numpy for efficient calculations
        prices_array = np.array(self.prices)
        volumes_array = np.array(self.volumes)
        
        total_volume = np.sum(volumes_array)
        if total_volume == 0:
            return 0.0
        
        weighted_prices = prices_array * volumes_array
        return np.sum(weighted_prices) / total_volume
```

#### Memory Profiling
```python
import tracemalloc
import psutil
import os

def monitor_memory():
    """Monitor memory usage of the current process."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Get memory usage percentage
    memory_percent = process.memory_percent()
    print(f"Memory Usage: {memory_percent:.2f}%")

# Usage
tracemalloc.start()
# Your code here
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

### Network Optimization

#### Connection Pooling
```python
import aiohttp
import asyncio

class ConnectionManager:
    def __init__(self):
        self.session = None
        self.connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(connector=self.connector)
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

# Usage
async def fetch_data(urls):
    async with ConnectionManager() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return responses
```

#### Compression
```python
import gzip
import json

def compress_data(data):
    """Compress data for network transmission."""
    json_data = json.dumps(data)
    compressed = gzip.compress(json_data.encode('utf-8'))
    return compressed

def decompress_data(compressed_data):
    """Decompress received data."""
    decompressed = gzip.decompress(compressed_data)
    return json.loads(decompressed.decode('utf-8'))
```

### CPU Optimization

#### Parallel Processing
```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def process_trades_parallel(trades, num_processes=None):
    """Process trades in parallel using multiple processes."""
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    chunk_size = len(trades) // num_processes
    chunks = [trades[i:i + chunk_size] for i in range(0, len(trades), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = executor.map(process_trade_chunk, chunks)
    
    return list(results)

def process_trades_threaded(trades, num_threads=None):
    """Process trades in parallel using threads."""
    if num_threads is None:
        num_threads = min(32, (os.cpu_count() or 1) + 4)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(process_single_trade, trades)
    
    return list(results)
```

#### Caching
```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=1000)
def expensive_calculation(symbol, timestamp):
    """Cache expensive calculations."""
    # Expensive computation here
    return result

# Redis caching
class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def get(self, key):
        return self.redis_client.get(key)
    
    def set(self, key, value, expire=3600):
        return self.redis_client.setex(key, expire, value)
    
    def delete(self, key):
        return self.redis_client.delete(key)
```

## 🔧 Performance Testing

### Load Testing

```python
import asyncio
import aiohttp
import time
from statistics import mean, median

async def load_test(url, num_requests=1000, concurrent_requests=100):
    """Perform load testing on an endpoint."""
    semaphore = asyncio.Semaphore(concurrent_requests)
    
    async def make_request(session):
        async with semaphore:
            start_time = time.time()
            try:
                async with session.get(url) as response:
                    await response.text()
                    return time.time() - start_time
            except Exception as e:
                print(f"Request failed: {e}")
                return None
    
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    # Filter out failed requests
    successful_results = [r for r in results if r is not None]
    
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {len(successful_results)}")
    print(f"Failed requests: {num_requests - len(successful_results)}")
    print(f"Average response time: {mean(successful_results):.3f}s")
    print(f"Median response time: {median(successful_results):.3f}s")
    print(f"Min response time: {min(successful_results):.3f}s")
    print(f"Max response time: {max(successful_results):.3f}s")

# Usage
asyncio.run(load_test("http://localhost:8000/api/data", 1000, 100))
```

### Benchmarking

```python
import time
import cProfile
import pstats
from io import StringIO

def benchmark_function(func, *args, **kwargs):
    """Benchmark a function's performance."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"Function {func.__name__} executed in {execution_time:.3f}s")
    
    return result

def profile_function(func, *args, **kwargs):
    """Profile a function to identify bottlenecks."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Print profiling results
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)  # Print top 10 functions
    print(s.getvalue())
    
    return result
```

## 📈 Performance Tuning

### JVM Tuning (for Kafka)

```properties
# Kafka server.properties
# Heap size
KAFKA_HEAP_OPTS="-Xmx4G -Xms4G"

# GC settings
KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35"

# Network settings
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
```

### PostgreSQL Tuning

```sql
-- postgresql.conf optimizations
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Python Optimization

```python
# Use __slots__ for memory efficiency
class TradeData:
    __slots__ = ['symbol', 'price', 'volume', 'timestamp']
    
    def __init__(self, symbol, price, volume, timestamp):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.timestamp = timestamp

# Use generators for memory efficiency
def process_large_dataset(data):
    for item in data:
        yield process_item(item)

# Use list comprehensions for performance
# Good
squares = [x**2 for x in range(1000)]

# Bad
squares = []
for x in range(1000):
    squares.append(x**2)
```

## 🚨 Performance Alerts

### Setting Up Alerts

```python
import logging
import psutil
import time

class PerformanceMonitor:
    def __init__(self, alert_thresholds):
        self.thresholds = alert_thresholds
        self.logger = logging.getLogger(__name__)
    
    def check_system_metrics(self):
        """Check system performance metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        if cpu_percent > self.thresholds['cpu']:
            self.logger.warning(f"High CPU usage: {cpu_percent}%")
        
        if memory_percent > self.thresholds['memory']:
            self.logger.warning(f"High memory usage: {memory_percent}%")
        
        if disk_percent > self.thresholds['disk']:
            self.logger.warning(f"High disk usage: {disk_percent}%")
    
    def start_monitoring(self, interval=60):
        """Start continuous monitoring."""
        while True:
            self.check_system_metrics()
            time.sleep(interval)

# Usage
monitor = PerformanceMonitor({
    'cpu': 80,
    'memory': 85,
    'disk': 90
})
monitor.start_monitoring()
```

## 📊 Performance Metrics Dashboard

### Grafana Queries

```sql
-- Average response time
SELECT 
    time_bucket('1 minute', timestamp) as time,
    avg(response_time) as avg_response_time
FROM api_metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time
ORDER BY time;

-- Request rate
SELECT 
    time_bucket('1 minute', timestamp) as time,
    count(*) as request_count
FROM api_metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time
ORDER BY time;

-- Error rate
SELECT 
    time_bucket('1 minute', timestamp) as time,
    count(*) FILTER (WHERE status_code >= 400) as error_count,
    count(*) as total_count,
    (count(*) FILTER (WHERE status_code >= 400) * 100.0 / count(*)) as error_rate
FROM api_metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time
ORDER BY time;
```

## 🔍 Performance Debugging

### Common Issues and Solutions

#### High Memory Usage
```python
# Use memory profiling
import tracemalloc
import gc

def debug_memory():
    """Debug memory usage."""
    tracemalloc.start()
    
    # Your code here
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    # Force garbage collection
    gc.collect()
    
    tracemalloc.stop()
```

#### Slow Database Queries
```python
import logging

# Enable query logging
logging.basicConfig(level=logging.DEBUG)

# Use connection pooling
from psycopg2 import pool

# Monitor query execution time
import time

def execute_query_with_timing(cursor, query, params=None):
    start_time = time.time()
    cursor.execute(query, params)
    execution_time = time.time() - start_time
    
    if execution_time > 1.0:  # Log slow queries
        logging.warning(f"Slow query ({execution_time:.3f}s): {query}")
    
    return cursor.fetchall()
```

#### Network Bottlenecks
```python
import asyncio
import aiohttp

async def test_network_performance():
    """Test network performance."""
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        tasks = []
        for i in range(100):
            task = session.get('http://localhost:8000/api/data')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"100 requests completed in {total_time:.3f}s")
        print(f"Average time per request: {total_time/100:.3f}s")
```

## 📚 Performance Resources

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Kafka Performance Tuning](https://kafka.apache.org/documentation/#tuning)
- [Docker Performance Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Grafana Performance Monitoring](https://grafana.com/docs/grafana/latest/administration/performance/)
