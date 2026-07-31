# API Documentation

## A/B Testing Endpoints

### `POST /api/experiments/create`
Create a new pricing experiment.
**Body:**
```json
{
  "sku_id": "item-123",
  "treatment_price": 49.99,
  "duration_days": 14
}
```

### `GET /api/experiments/{id}`
Get the current statistical results of the experiment.

### `POST /api/experiments/{id}/conclude`
End the experiment and declare a winner.

### `POST /api/experiments/power-analysis`
Calculate required sample sizes.
