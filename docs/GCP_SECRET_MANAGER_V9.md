# GCP Secret Manager setup for v9

Recommended secrets:
- `WEBHOOK_SECRET`
- `DASHBOARD_VIEWER_API_KEY`
- `DASHBOARD_OPERATOR_API_KEY`
- `DASHBOARD_ADMIN_API_KEY`
- MT5 credentials when deploying a compatible private runtime

## Example

```bash
gcloud secrets create WEBHOOK_SECRET --data-file=-
gcloud secrets versions add WEBHOOK_SECRET --data-file=<(printf "your-secret")
```

Bind secrets in Cloud Run with:

```bash
gcloud run services update alpha-ai-terminal \
  --region europe-central2 \
  --set-secrets WEBHOOK_SECRET=WEBHOOK_SECRET:latest,DASHBOARD_ADMIN_API_KEY=DASHBOARD_ADMIN_API_KEY:latest
```

## Why this matters
Do not keep production secrets in `.env` files committed to source control. Secret Manager is the right path for Cloud Run deployments.