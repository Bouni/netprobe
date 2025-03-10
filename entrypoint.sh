if [[ "${MODULE}" == "NETPROBE" ]]; then
   uv run netprobe.py; 
elif [[ "${MODULE}" == "COLLECTOR" ]]; then
   uv run collector.py; 
elif [[ "${MODULE}" == "PRESENTATION" ]]; then
   uv run presentation.py; 
elif [[ "${MODULE}" == "SPEEDTEST" ]]; then
   uv run netprobe_speedtest.py; 
else 
  /bin/sh; 
fi
