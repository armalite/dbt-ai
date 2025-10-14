#!/bin/bash
# Setup script for dbt CLI in cloud environments

set -e

echo "🔧 Setting up dbt CLI for Data Product Hub..."

# Check if dbt is already installed
if command -v dbt &> /dev/null; then
    echo "✅ dbt CLI already available: $(dbt --version | head -1)"
    exit 0
fi

echo "📦 Installing dbt CLI..."

# Install dbt with proper dependencies
pip install --no-cache-dir dbt-core~=1.5 dbt-snowflake~=1.5 setuptools standard-distutils

# Verify installation
if command -v dbt &> /dev/null; then
    echo "✅ dbt CLI installed successfully: $(dbt --version | head -1)"
else
    echo "❌ dbt CLI installation failed"
    exit 1
fi

echo "🎉 dbt CLI setup complete!"