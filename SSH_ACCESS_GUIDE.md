# 🌐 SSH Access Guide for AI Tutoring Chatbot

## 🎯 Quick Access (Recommended)

**From your local machine**, run this command:

```bash
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250
```

Then open in your browser: **http://localhost:3000**

## 🚀 Detailed Setup Instructions

### Method 1: SSH Port Forwarding (Safest)

1. **Open terminal on your local machine**
2. **Create SSH tunnel:**
   ```bash
   ssh -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250
   ```
3. **Keep this terminal open** (the tunnel stays active)
4. **Open browser** to: http://localhost:3000
5. **Login** with any username and start chatting!

### Method 2: Direct Remote Access

If your network allows direct access to the server:

- **Frontend**: http://10.165.77.250:3000
- **Backend API**: http://10.165.77.250:8000

### Method 3: VS Code Port Forwarding

If using VS Code with Remote SSH:

1. **Connect to server** via VS Code Remote SSH
2. **Go to Ports tab** in VS Code terminal panel
3. **Forward ports**: 3000 and 8000
4. **Click the links** VS Code provides

## 🛠️ Server Management Commands

**On the server (via SSH):**

```bash
# Start both servers
./start_chatbot.sh

# Check what's running
ps aux | grep -E "(uvicorn|react-scripts)" | grep -v grep

# View logs
tail -f backend.log    # Backend API logs
tail -f frontend.log   # Frontend React logs

# Stop all servers
pkill -f "uvicorn\|react-scripts"

# Check server health
curl http://localhost:8000/health
curl http://localhost:3000

# Original CLI (still works!)
python main.py
```

## 🔧 Troubleshooting

### SSH Tunnel Issues

**Problem**: Connection refused
```bash
# Solution: Restart the SSH tunnel
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250
```

**Problem**: Port already in use
```bash
# Solution: Use different local ports
ssh -L 3001:localhost:3000 -L 8001:localhost:8000 jain1012@10.165.77.250
# Then access: http://localhost:3001
```

### Server Issues

**Problem**: Backend not responding
```bash
# On server: Check backend status
curl http://localhost:8000/health

# Restart backend
pkill -f uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload &
```

**Problem**: Frontend not loading
```bash
# On server: Check frontend status
curl http://localhost:3000

# Restart frontend
pkill -f react-scripts
cd frontend && HOST=0.0.0.0 PORT=3000 npm start &
```

### Network Issues

**Problem**: Can't access from outside
- Ensure server firewall allows ports 3000 and 8000
- Check if your organization blocks these ports
- Use SSH tunneling instead of direct access

## 📱 Mobile Access

For mobile access, use SSH tunneling through a computer:

1. **Setup tunnel** on a computer connected to same network
2. **Access via computer's IP**: http://[computer-ip]:3000
3. **Or use** apps like Termius for mobile SSH tunneling

## ⚡ Performance Tips

### For Better SSH Performance:
```bash
# Use compression
ssh -C -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250

# Keep connection alive
ssh -o ServerAliveInterval=60 -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250
```

### For Better Chat Performance:
- Keep SSH connection stable
- Use wired connection when possible
- Close unnecessary browser tabs

## 🎓 Using the Chatbot

Once connected to http://localhost:3000:

### Basic Usage:
1. **Login** with your username
2. **Click "Chat"** in sidebar
3. **Start chatting!**

### Commands to try:
```
What is GIS?
!explain coordinate systems
!sources
!quiz GIS
!help
```

### Advanced Features:
- **Citations**: See document sources for each answer
- **Quiz Mode**: Interactive learning with immediate feedback
- **Progress Tracking**: Your learning history is saved
- **Multi-document**: Answers from your PDF/text files

## 🔐 Security Notes

- **SSH tunneling** is secure and encrypted
- **Direct access** exposes ports to network
- **Always use SSH** for production environments
- **Firewall rules** should restrict access as needed

## 📞 Need Help?

**Can't connect?**
1. Verify SSH access to server works
2. Check if servers are running (use `ps` command)
3. Try different ports in tunnel
4. Check firewall settings

**Chat not working?**
1. Check browser console (F12) for errors
2. Verify API server responds: `curl http://localhost:8000/health`
3. Check logs: `tail -f backend.log frontend.log`

---

**Happy Learning! 🎓✨**

Your AI tutor is ready to help you learn GIS and any topics in your documents! 