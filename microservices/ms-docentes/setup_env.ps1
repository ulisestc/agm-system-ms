python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install requests
python generate_grpc.py
Start-Process -NoNewWindow -FilePath ".\venv\Scripts\python.exe" -ArgumentList "main.py"
Start-Sleep -Seconds 5
