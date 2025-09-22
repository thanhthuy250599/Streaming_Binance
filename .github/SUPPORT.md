# Support

## Getting Help

If you need help with this project, here are the best ways to get support:

### 📚 Documentation

- **README.md**: Start here for setup and basic usage
- **docs/**: Detailed documentation and architecture guides
- **CONTRIBUTING.md**: Guidelines for contributing to the project

### 🐛 Bug Reports

If you encounter a bug:

1. Check existing issues first
2. Create a new issue with the bug report template
3. Include relevant logs and environment details

### 💡 Feature Requests

For new features:

1. Check existing feature requests
2. Create a new issue with the feature request template
3. Provide clear use cases and requirements

### 💬 Community Support

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Pull Requests**: Contribute code and improvements

## Common Issues

### Installation Problems

**Docker not starting:**
```bash
# Check Docker status
docker --version
docker compose --version

# Restart Docker service
sudo systemctl restart docker
```

**Python dependencies:**
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Port conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :3000
netstat -tulpn | grep :5432
netstat -tulpn | grep :9094
```

### Runtime Issues

**Services not starting:**
```bash
# Check Docker containers
docker compose ps

# Check logs
docker compose logs

# Restart services
docker compose down
docker compose up -d
```

**Data not flowing:**
```bash
# Check producer logs
tail -f producer.log

# Check aggregator logs
tail -f aggregator.log

# Check database
docker exec -it binance_streaming_project-postgres-1 psql -U grafana -d crypto -c "SELECT COUNT(*) FROM kpi_symbol_1m;"
```

## Performance Issues

### High Memory Usage
- Monitor Docker container resources
- Check for memory leaks in Python processes
- Optimize aggregation windows

### Slow Data Processing
- Check Kafka consumer lag
- Monitor database performance
- Optimize aggregation algorithms

## Troubleshooting Steps

1. **Check system requirements**
2. **Verify Docker installation**
3. **Check port availability**
4. **Review log files**
5. **Test individual components**
6. **Check network connectivity**
7. **Verify configuration**

## Contributing to Support

Help improve support by:

- Updating documentation
- Adding troubleshooting guides
- Sharing solutions to common problems
- Improving error messages
- Adding better logging

## Contact Information

- **Project Maintainer**: [Your Name]
- **Email**: [your-email@example.com]
- **GitHub**: [Your GitHub Profile]

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Python Documentation](https://docs.python.org/)