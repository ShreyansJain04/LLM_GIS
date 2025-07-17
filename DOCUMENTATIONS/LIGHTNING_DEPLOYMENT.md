# Lightning AI Deployment Guide

This guide will help you deploy your AI Tutoring System to Lightning AI using Docker.

## Prerequisites

1. **Lightning AI Account**: Sign up at [lightning.ai](https://lightning.ai)
2. **Lightning AI CLI**: Install the Lightning CLI
3. **Docker**: Ensure Docker is installed on your local machine for testing

## Step 1: Prepare Your Environment

### 1.1 Install Lightning AI CLI
```bash
pip install lightning
```

### 1.2 Login to Lightning AI
```bash
lightning login
```

## Step 2: Set Up API Keys

You'll need to add your API keys as secrets in Lightning AI Studio:

1. Go to Lightning AI Studio
2. Navigate to your workspace settings
3. Add the following secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ANTHROPIC_API_KEY` - Your Anthropic API key (if using Claude)
   - `GOOGLE_API_KEY` - Your Google API key (if using Gemini)

## Step 3: Test Docker Build Locally (Optional but Recommended)

```bash
# Build the Docker image
docker build -t ai-tutoring-system .

# Test run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_key \
  ai-tutoring-system
```

Visit `http://localhost:8000/health` to verify the application is running.

## Step 4: Deploy to Lightning AI

### Option A: Using Lightning CLI

```bash
# Deploy using the configuration file
lightning deploy app lightning-deploy.yaml
```

### Option B: Using Lightning Studio

1. Upload your project to Lightning AI Studio
2. Create a new App
3. Use the provided `Dockerfile` and `lightning-deploy.yaml`
4. Configure environment variables in the Studio interface

## Step 5: Configure Your Deployment

### 5.1 Adjust Resources (if needed)

Edit `lightning-deploy.yaml` to modify:
- CPU/Memory allocation
- GPU requirements (set `gpu: 1` if you need GPU acceleration)
- Scaling parameters

### 5.2 Environment Variables

Make sure these environment variables are set in Lightning AI:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` (optional)
- `GOOGLE_API_KEY` (optional)

## Step 6: Access Your Application

Once deployed, Lightning AI will provide you with:
- A public URL to access your application
- Monitoring dashboard
- Logs and metrics

## File Structure

Your deployment includes these key files:

```
├── Dockerfile              # Multi-stage build for frontend + backend
├── .dockerignore           # Excludes unnecessary files from build
├── lightning-deploy.yaml   # Lightning AI deployment configuration
├── api_server.py          # FastAPI backend
├── frontend/              # React frontend
├── requirements.txt       # Python dependencies
└── docs/                  # Document storage for RAG
```

## Troubleshooting

### Common Issues:

1. **Build Failures**: Check that all dependencies in `requirements.txt` are compatible
2. **Memory Issues**: Increase memory allocation in `lightning-deploy.yaml`
3. **API Key Errors**: Verify secrets are properly configured in Lightning AI Studio
4. **Port Issues**: Ensure port 8000 is properly exposed

### Monitoring:

- Check application logs in Lightning AI Studio
- Monitor resource usage and scaling
- Use the `/health` endpoint to verify application status

## Updating Your Deployment

To update your deployment:

```bash
# Make your changes
# Then redeploy
lightning deploy app lightning-deploy.yaml
```

## Cost Optimization

- Start with minimal resources (2 CPU, 4GB RAM)
- Enable auto-scaling to handle traffic spikes
- Monitor usage and adjust resources accordingly
- Use GPU only if you need accelerated inference

## Security Notes

- Never commit API keys to your repository
- Use Lightning AI's secret management for sensitive data
- Regularly update dependencies for security patches
- Monitor access logs for unusual activity

## Support

If you encounter issues:
1. Check Lightning AI documentation
2. Review application logs in the Studio
3. Test locally first to isolate deployment issues
4. Contact Lightning AI support for platform-specific problems