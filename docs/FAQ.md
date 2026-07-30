# FAQ

**Q: How much historical data do I need?**
A: The AI models require a minimum of 90 days of historical sales data to detect seasonality patterns accurately.

**Q: Will the system automatically change my prices?**
A: By default, the system operates in "Recommendation Mode". It will only suggest prices, and you must approve them. You can enable "Auto-Pilot Mode" in the settings for specific products or categories.

**Q: How does the competitor tracking work?**
A: We use a combination of official APIs and targeted web scrapers to check competitor URLs every 4 hours.

**Q: Is my data secure?**
A: Yes. All data is encrypted at rest and in transit. Your integration API keys are encrypted using AES-256 (Fernet) before being saved to the database.
