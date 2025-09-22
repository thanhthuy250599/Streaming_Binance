# Binance Real-time Streaming Project

A real-time cryptocurrency data streaming pipeline that captures live trade data from Binance WebSocket API, processes it through Kafka, and stores aggregated metrics in PostgreSQL with Grafana visualization.

## 🏗️ Architecture

```
Binance WebSocket → Kafka → Python Aggregator → PostgreSQL → Grafana
```

## 🚀 Features

- **Real-time Data Streaming**: Live trade data from Binance WebSocket API
- **Message Queue**: Apache Kafka for reliable data streaming
- **Data Processing**: Python-based aggregation with 1-minute windows
- **Database Storage**: PostgreSQL for persistent data storage
- **Visualization**: Grafana dashboards for real-time monitoring
- **Containerized**: Docker Compose for easy deployment

## 📊 Data Pipeline

1. **Producer**: Connects to Binance WebSocket API and streams trade data to Kafka
2. **Aggregator**: Consumes from Kafka and calculates 1-minute aggregated metrics:
   - Trade count
   - Average price
   - VWAP (Volume Weighted Average Price)
   - Volume
   - Volatility
   - Anomaly detection
3. **Database**: Stores aggregated data in PostgreSQL
4. **Visualization**: Grafana dashboards for monitoring

## 🛠️ Tech Stack

- **Python 3.11+**: Main programming language
- **Apache Kafka**: Message streaming platform
- **PostgreSQL**: Relational database
- **Grafana**: Data visualization
- **Docker**: Containerization
- **WebSocket**: Real-time data connection

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd binance_streaming_project
```

### 2. Start the System

```bash
# Start all services
bash run_all.sh

# Or manually start Docker containers
docker compose up -d
```

### 3. Monitor the System

```bash
# Check logs
tail -f producer.log
tail -f aggregator.log

# Check database
docker exec -it binance_streaming_project-postgres-1 psql -U grafana -d crypto -c "SELECT COUNT(*) FROM kpi_symbol_1m;"
```

### 4. Access Grafana

Open your browser and go to: http://localhost:3000

- Username: `admin`
- Password: `admin`

## 📁 Project Structure

```
binance_streaming_project/
├── producers/
│   ├── binance_ws_to_kafka.py    # WebSocket to Kafka producer
│   └── requirements.txt          # Python dependencies
├── spark-jobs/
│   └── streaming_agg.py          # Kafka consumer and aggregator
├── docker-compose.yml            # Docker services configuration
├── run_all.sh                    # Start all services
├── stop_all.sh                   # Stop all services
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

The system uses the following environment variables:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address (default: localhost:9094)
- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_DB`: Database name (default: crypto)
- `POSTGRES_USER`: Database user (default: grafana)
- `POSTGRES_PASSWORD`: Database password (default: secret)

### Supported Symbols

Currently configured for:
- BTCUSDT
- ETHUSDT

## 📊 Database Schema

### kpi_symbol_1m Table

| Column | Type | Description |
|--------|------|-------------|
| window_start | TIMESTAMP | Start of 1-minute window |
| window_end | TIMESTAMP | End of 1-minute window |
| symbol | VARCHAR | Trading pair symbol |
| trades | INTEGER | Number of trades |
| avg_price | DECIMAL | Average price |
| vwap | DECIMAL | Volume Weighted Average Price |
| volume | DECIMAL | Total volume |
| volatility | DECIMAL | Price volatility |
| anomaly | BOOLEAN | Anomaly detection flag |
| inserted_at | TIMESTAMP | Record insertion time |

## 🛑 Stopping the System

```bash
# Stop all services
bash stop_all.sh

# Or manually stop Docker containers
docker compose down
```

## 📈 Monitoring

### Log Files

- `producer.log`: WebSocket producer logs
- `aggregator.log`: Data aggregation logs

### Grafana Dashboards

Access Grafana at http://localhost:3000 to view:
- Real-time trade volume
- Price movements
- System performance metrics
- Data pipeline health

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 5432, 9094 are available
2. **Docker issues**: Make sure Docker is running
3. **Permission errors**: Check file permissions for log files
4. **Connection issues**: Verify network connectivity

### Logs

Check the log files for detailed error information:
```bash
tail -f producer.log
tail -f aggregator.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Binance for providing the WebSocket API
- Apache Kafka for message streaming
- PostgreSQL for data storage
- Grafana for visualization