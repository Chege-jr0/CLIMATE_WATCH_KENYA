cd "/c/DATA ANALYTICS/CLIMATE_WATCH"
cat > activate_env.sh << 'EOF'
export PATH="$(pwd)/.venv/Scripts:$PATH"
echo "Virtual environment activated"
EOF