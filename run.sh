tmux start-server
tmux new-session -d -s monitoring -n "Logs"


tmux selectp -t 0    
tmux splitw -h -p 50 
tmux selectp -t 0    
tmux splitw -v -p 50 
tmux selectp -t 2    
tmux splitw -v -p 20

tmux resize-pane -t 3 -D 

tmux send-keys -t 0 "docker compose down;docker compose build base-builder;docker compose build --no-cache; docker compose up" C-m
tmux send-keys -t 1 "tail -f ./data_summary/factory_data.txt" C-m
tmux send-keys -t 2 "tail -f ./data_summary/stock_data.txt" C-m
tmux send-keys -t 3 "tail -f ./data_summary/product_data.txt" C-m

tmux attach-session -t monitoring
tmux send-keys -t 0 "docker compose down" C-m
tmux kill-server